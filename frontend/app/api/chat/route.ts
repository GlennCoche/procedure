import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'
import OpenAI from 'openai'

// Créer le client OpenAI de manière lazy pour éviter les erreurs au build
function getOpenAIClient() {
  const apiKey = process.env.OPENAI_API_KEY
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY is not configured')
  }
  return new OpenAI({ apiKey })
}

export async function POST(request: NextRequest) {
  const user = await getCurrentUser()
  if (!user) {
    return new Response('Non authentifié', { status: 401 })
  }

  try {
    const { message, context } = await request.json()

    if (!message) {
      return new Response('Message requis', { status: 400 })
    }

    // Récupérer l'historique des messages
    const history = await db.chatMessage.findMany({
      where: { userId: user.id },
      orderBy: { createdAt: 'desc' },
      take: 10,
    })

    // Construire le contexte système
    let systemMessage = 'Tu es un assistant technique spécialisé en maintenance photovoltaïque. Tu aides les techniciens à résoudre des problèmes et à suivre des procédures de maintenance.'

    // Ajouter le contexte de la procédure si disponible
    if (context?.procedure_id) {
      const procedure = await db.procedure.findUnique({
        where: { id: context.procedure_id },
        include: {
          steps: {
            orderBy: { order: 'asc' },
          },
        },
      })

      if (procedure) {
        systemMessage += `\n\nContexte de la procédure "${procedure.title}":\n${procedure.description || ''}\n\nÉtapes:\n${procedure.steps.map((s, i) => `${i + 1}. ${s.title}: ${s.description || ''}`).join('\n')}`
      }
    }

    // Construire les messages pour OpenAI
    const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
      {
        role: 'system',
        content: systemMessage,
      },
      ...history
        .reverse()
        .filter((msg) => msg.message && msg.response)
        .flatMap((msg) => [
          {
            role: 'user' as const,
            content: msg.message,
          },
          {
            role: 'assistant' as const,
            content: msg.response!,
          },
        ]),
      {
        role: 'user',
        content: message,
      },
    ]

    // Sauvegarder le message utilisateur
    const chatMessage = await db.chatMessage.create({
      data: {
        userId: user.id,
        message,
        context: context ? JSON.stringify(context) : null,
      },
    })

    // Appeler OpenAI avec streaming
    const openai = getOpenAIClient()
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages,
      stream: true,
      temperature: 0.7,
    })

    // Créer un stream de réponse
    const stream = new ReadableStream({
      async start(controller) {
        let fullResponse = ''

        try {
          for await (const chunk of completion) {
            const content = chunk.choices[0]?.delta?.content || ''
            if (content) {
              fullResponse += content
              // Envoyer le chunk au client
              controller.enqueue(
                new TextEncoder().encode(`data: ${JSON.stringify({ content })}\n\n`)
              )
            }
          }

          // Marquer la fin
          controller.enqueue(new TextEncoder().encode('data: [DONE]\n\n'))

          // Sauvegarder la réponse complète
          await db.chatMessage.update({
            where: { id: chatMessage.id },
            data: { response: fullResponse },
          })

          controller.close()
        } catch (error) {
          console.error('Erreur streaming:', error)
          controller.enqueue(
            new TextEncoder().encode(
              `data: ${JSON.stringify({ error: 'Erreur lors de la génération' })}\n\n`
            )
          )
          controller.close()
        }
      },
    })

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      },
    })
  } catch (error) {
    console.error('Erreur chat:', error)
    return new Response('Erreur serveur', { status: 500 })
  }
}
