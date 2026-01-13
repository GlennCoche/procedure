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

// Prompts selon le mode
const EXPERT_PROMPT_STANDARD = `Tu es un EXPERT SENIOR en maintenance photovoltaïque avec 25 ans d'expérience terrain.

COMPORTEMENT OBLIGATOIRE:

1. CLARIFICATION D'ABORD
   - Si la question est ambiguë ou manque de détails, demande des précisions AVANT de répondre
   - Demande: marque de l'équipement, modèle exact, code erreur affiché, contexte d'intervention
   - Exemple: "Pour mieux vous aider, pouvez-vous préciser le modèle exact de l'onduleur et le message d'erreur affiché ?"

2. BASE DE DONNÉES EN PRIORITÉ
   - Utilise TOUJOURS les procédures et tips de la base en priorité
   - Cite explicitement tes sources: "Selon la procédure 'Installation ABB TRIO'..."

3. RÉPONSE STRUCTURÉE (format obligatoire)
   📋 DIAGNOSTIC
   Résumé du problème tel que tu l'as compris.

   ✅ SOLUTION PRINCIPALE  
   Étapes détaillées depuis la base documentaire si disponible.

   🔄 ALTERNATIVES
   Autres approches possibles si la solution principale ne fonctionne pas.

   ⚠️ PRÉCAUTIONS
   Points de sécurité et mises en garde importantes.

   📚 RÉFÉRENCES
   Procédures et tips pertinents de la base (avec titres exacts).

4. SPÉCIFICITÉS FRANCE
   - Connais les normes NF C 15-100, UTE C 15-712
   - Standards réseau France: 230/400V, 50Hz

CONTEXTE TECHNIQUE DISPONIBLE:
{context}

Réponds en français, de manière professionnelle mais accessible.`

const EXPERT_PROMPT_CONCISE = `Tu es un EXPERT SENIOR en maintenance photovoltaïque. Réponds de manière CONCISE et PRÉCISE.

RÈGLES STRICTES:
1. Réponses COURTES: 3-5 phrases maximum par section
2. Va DROIT AU BUT: pas de préambule, pas de redondance
3. POSE DES QUESTIONS si besoin de précisions (max 2 questions ciblées)
4. Format bullet points quand possible
5. Cite uniquement les références essentielles

FORMAT DE RÉPONSE:
• DIAGNOSTIC: 1-2 phrases
• SOLUTION: Étapes numérotées, concises
• ⚠️ SÉCURITÉ: Points critiques uniquement
• ❓ QUESTIONS: Si besoin de précisions

{context}

Réponds en français. Sois direct et efficace.`

export async function POST(request: NextRequest) {
  const user = await getCurrentUser()
  if (!user) {
    return new Response('Non authentifié', { status: 401 })
  }

  try {
    const { message, context, settings } = await request.json()

    if (!message) {
      return new Response('Message requis', { status: 400 })
    }

    // Paramètres de configuration
    const conciseMode = settings?.concise ?? false
    const dualMode = settings?.dualResponse ?? false

    // Récupérer l'historique des messages
    const history = await db.chatMessage.findMany({
      where: { userId: user.id },
      orderBy: { createdAt: 'desc' },
      take: 10,
    })

    // AUTO-LEARNING: Récupérer les réponses bien notées
    let learningContext = ''
    try {
      const positiveExamples = await db.messageRating.findMany({
        where: {
          rating: 'positive',
          message: { userId: user.id },
        },
        include: {
          message: { select: { message: true, response: true } },
        },
        orderBy: { createdAt: 'desc' },
        take: 3,
      })

      if (positiveExamples.length > 0) {
        learningContext = '\n\n📊 STYLE APPRÉCIÉ:\n'
        for (const ex of positiveExamples) {
          if (ex.message.response) {
            learningContext += `• "${ex.message.response.slice(0, 150)}..."\n`
          }
        }
      }
    } catch {
      // Table ratings n'existe pas encore
    }

    // Construire le contexte depuis la base de données
    let contextInfo = ''
    try {
      const keywords = message.toLowerCase().split(/\s+/).filter((w: string) => w.length > 3).slice(0, 5)
      
      if (keywords.length > 0) {
        const procedures = await db.procedure.findMany({
          where: {
            OR: keywords.flatMap((keyword: string) => [
              { title: { contains: keyword, mode: 'insensitive' as const } },
              { description: { contains: keyword, mode: 'insensitive' as const } },
            ])
          },
          include: { steps: { orderBy: { order: 'asc' } } },
          take: 3
        })

        if (procedures.length > 0) {
          contextInfo += '\n📖 PROCÉDURES:\n'
          for (const proc of procedures) {
            contextInfo += `• "${proc.title}": ${proc.steps.map(s => s.title).join(' → ')}\n`
          }
        }

        const tips = await db.tip.findMany({
          where: {
            OR: keywords.flatMap((keyword: string) => [
              { title: { contains: keyword, mode: 'insensitive' as const } },
              { content: { contains: keyword, mode: 'insensitive' as const } },
            ])
          },
          take: 3
        })

        if (tips.length > 0) {
          contextInfo += '\n💡 TIPS:\n'
          for (const tip of tips) {
            contextInfo += `• "${tip.title}": ${tip.content.slice(0, 100)}...\n`
          }
        }
      }
    } catch (error) {
      console.warn('Recherche par mots-clés échouée:', error)
    }

    if (!contextInfo) {
      contextInfo = '\n⚠️ Aucune doc trouvée. Utilise tes connaissances expert.\n'
    }

    const fullContext = contextInfo + learningContext
    const basePrompt = conciseMode ? EXPERT_PROMPT_CONCISE : EXPERT_PROMPT_STANDARD
    const systemMessage = basePrompt.replace('{context}', fullContext)

    // Construire les messages pour OpenAI
    const openaiMessages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
      { role: 'system', content: systemMessage },
      ...history
        .reverse()
        .filter((msg) => msg.message && msg.response)
        .slice(-6)
        .flatMap((msg) => [
          { role: 'user' as const, content: msg.message },
          { role: 'assistant' as const, content: msg.response! },
        ]),
      { role: 'user', content: message },
    ]

    const openai = getOpenAIClient()

    // MODE DUAL: Générer 2 réponses alternatives
    if (dualMode) {
      const [response1, response2] = await Promise.all([
        openai.chat.completions.create({
          model: 'gpt-4o-mini',
          messages: openaiMessages,
          temperature: 0.3,
          max_tokens: conciseMode ? 500 : 1500,
        }),
        openai.chat.completions.create({
          model: 'gpt-4o-mini',
          messages: [
            ...openaiMessages.slice(0, -1),
            { 
              role: 'user', 
              content: message + '\n\n[Propose une approche ALTERNATIVE différente de la première qui pourrait venir à l\'esprit]' 
            }
          ],
          temperature: 0.7,
          max_tokens: conciseMode ? 500 : 1500,
        }),
      ])

      const content1 = response1.choices[0]?.message?.content || ''
      const content2 = response2.choices[0]?.message?.content || ''

      // Sauvegarder le message (sans réponse pour l'instant)
      const chatMessage = await db.chatMessage.create({
        data: {
          userId: user.id,
          message,
          context: JSON.stringify({ ...context, dualMode: true }),
        },
      })

      return new Response(JSON.stringify({
        messageId: chatMessage.id,
        dualMode: true,
        responses: [
          { id: 'A', content: content1, label: 'Réponse A - Approche standard' },
          { id: 'B', content: content2, label: 'Réponse B - Approche alternative' },
        ]
      }), {
        headers: { 'Content-Type': 'application/json' },
      })
    }

    // MODE STANDARD: Streaming
    const chatMessage = await db.chatMessage.create({
      data: {
        userId: user.id,
        message,
        context: context ? JSON.stringify(context) : null,
      },
    })

    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: openaiMessages,
      stream: true,
      temperature: conciseMode ? 0.3 : 0.5,
      max_tokens: conciseMode ? 600 : 2000,
    })

    const stream = new ReadableStream({
      async start(controller) {
        let fullResponse = ''

        try {
          controller.enqueue(
            new TextEncoder().encode(`data: ${JSON.stringify({ messageId: chatMessage.id })}\n\n`)
          )

          for await (const chunk of completion) {
            const content = chunk.choices[0]?.delta?.content || ''
            if (content) {
              fullResponse += content
              controller.enqueue(
                new TextEncoder().encode(`data: ${JSON.stringify({ content })}\n\n`)
              )
            }
          }

          controller.enqueue(new TextEncoder().encode('data: [DONE]\n\n'))

          await db.chatMessage.update({
            where: { id: chatMessage.id },
            data: { response: fullResponse },
          })

          controller.close()
        } catch (error) {
          console.error('Erreur streaming:', error)
          controller.enqueue(
            new TextEncoder().encode(`data: ${JSON.stringify({ error: 'Erreur lors de la génération' })}\n\n`)
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

// Endpoint pour sélectionner une réponse en mode dual
export async function PUT(request: NextRequest) {
  const user = await getCurrentUser()
  if (!user) {
    return new Response('Non authentifié', { status: 401 })
  }

  try {
    const { messageId, selectedResponse, selectedId } = await request.json()

    if (!messageId || !selectedResponse) {
      return new Response('Données manquantes', { status: 400 })
    }

    // Mettre à jour le message avec la réponse sélectionnée
    await db.chatMessage.update({
      where: { id: messageId },
      data: { 
        response: selectedResponse,
        context: JSON.stringify({ selectedChoice: selectedId })
      },
    })

    // Enregistrer automatiquement un feedback positif pour la réponse choisie
    try {
      await db.messageRating.create({
        data: {
          messageId,
          rating: 'positive',
          feedback: `Réponse ${selectedId} sélectionnée`,
        },
      })
    } catch {
      // Table ratings n'existe pas encore
    }

    return new Response(JSON.stringify({ success: true }), {
      headers: { 'Content-Type': 'application/json' },
    })
  } catch (error) {
    console.error('Erreur sélection réponse:', error)
    return new Response('Erreur serveur', { status: 500 })
  }
}
