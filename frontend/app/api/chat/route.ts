import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'
import OpenAI from 'openai'
import { Prisma } from '@prisma/client'

// Créer le client OpenAI de manière lazy pour éviter les erreurs au build
function getOpenAIClient() {
  const apiKey = process.env.OPENAI_API_KEY
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY is not configured')
  }
  return new OpenAI({ apiKey })
}

// System prompt expert photovoltaïque
const EXPERT_SYSTEM_PROMPT = `Tu es un EXPERT SENIOR en maintenance photovoltaïque avec 25 ans d'expérience terrain.

COMPORTEMENT OBLIGATOIRE:

1. CLARIFICATION D'ABORD
   - Si la question est ambiguë ou manque de détails, demande des précisions AVANT de répondre
   - Demande: marque de l'équipement, modèle exact, code erreur affiché, contexte d'intervention
   - Exemple: "Pour mieux vous aider, pouvez-vous préciser le modèle exact de l'onduleur et le message d'erreur affiché ?"

2. BASE DE DONNÉES EN PRIORITÉ
   - Utilise TOUJOURS les procédures et tips de la base en priorité
   - Cite explicitement tes sources: "Selon la procédure 'Installation ABB TRIO'..."
   - Indique clairement si l'info vient de la base documentaire ou de tes connaissances générales

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

4. SI INFORMATION MANQUANTE
   - Indique clairement que l'info n'est pas dans la base documentaire
   - Donne une réponse basée sur tes connaissances d'expert
   - Propose des pistes de recherche sur les sites constructeurs officiels

5. STYLE EXPERT
   - Langage technique précis mais accessible
   - Valeurs numériques quand pertinent (tensions, courants, températures)
   - Conseils terrain basés sur l'expérience pratique
   - Mise en garde sécurité SYSTÉMATIQUE (risques électriques, travail en hauteur)

6. SPÉCIFICITÉS FRANCE
   - Connais les normes NF C 15-100, UTE C 15-712
   - Standards réseau France: 230/400V, 50Hz
   - Références aux seuils de déclenchement standard France

CONTEXTE TECHNIQUE DISPONIBLE:
{context}

Réponds en français, de manière professionnelle mais accessible.`

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

    // Récupérer l'historique des messages (augmenté à 15)
    const history = await db.chatMessage.findMany({
      where: { userId: user.id },
      orderBy: { createdAt: 'desc' },
      take: 15,
    })

    // Construire le contexte depuis la base de données
    let contextInfo = ''
    let foundProcedures: string[] = []
    let foundTips: string[] = []

    // Recherche vectorielle pour enrichir le contexte
    try {
      const openai = getOpenAIClient()
      const embeddingResponse = await openai.embeddings.create({
        model: 'text-embedding-3-small',
        input: message.slice(0, 8000),
      })
      const queryEmbedding = embeddingResponse.data[0].embedding
      const embeddingStr = '[' + queryEmbedding.join(',') + ']'

      // Recherche vectorielle améliorée (seuil abaissé à 0.5, top_k augmenté à 10)
      const escapedEmbedding = embeddingStr.replace(/'/g, "''")
      const vectorResults = await db.$queryRaw<Array<{
        id: number
        document_type: string
        document_id: number
        content: string
        metadata: string | null
        similarity: number
      }>>(
        Prisma.raw(`
          SELECT 
            id,
            document_type,
            document_id,
            content,
            metadata,
            1 - (embedding <=> '${escapedEmbedding}'::vector) as similarity
          FROM document_embeddings
          WHERE embedding IS NOT NULL
          AND (1 - (embedding <=> '${escapedEmbedding}'::vector)) >= 0.5
          ORDER BY similarity DESC
          LIMIT 10
        `)
      )

      // Enrichir le contexte avec les résultats de recherche
      if (vectorResults.length > 0) {
        contextInfo += '\n📖 DOCUMENTATION PERTINENTE TROUVÉE:\n'
        
        for (const result of vectorResults) {
          const metadata = result.metadata ? JSON.parse(result.metadata) : {}
          const title = metadata.title || `Document ${result.document_id}`
          const similarity = Math.round(result.similarity * 100)
          
          if (result.document_type === 'procedure') {
            foundProcedures.push(title)
            contextInfo += `\n🔧 PROCÉDURE: "${title}" (pertinence: ${similarity}%)\n`
            contextInfo += `   ${result.content.slice(0, 500)}\n`
          } else if (result.document_type === 'tip') {
            foundTips.push(title)
            contextInfo += `\n💡 TIP: "${title}" (pertinence: ${similarity}%)\n`
            contextInfo += `   ${result.content.slice(0, 300)}\n`
          }
        }
      }
    } catch (error) {
      console.warn('Recherche vectorielle non disponible:', error)
    }

    // Recherche par mots-clés en fallback si pas de résultats vectoriels
    if (!contextInfo) {
      try {
        // Recherche dans les procédures
        const keywords = message.toLowerCase().split(/\s+/).filter((w: string) => w.length > 3).slice(0, 5)
        if (keywords.length > 0) {
          const procedures = await db.procedure.findMany({
            where: {
              OR: keywords.map((keyword: string) => ({
                OR: [
                  { title: { contains: keyword, mode: 'insensitive' as const } },
                  { description: { contains: keyword, mode: 'insensitive' as const } },
                  { tags: { contains: keyword, mode: 'insensitive' as const } },
                ]
              }))
            },
            include: { steps: { orderBy: { order: 'asc' } } },
            take: 3
          })

          if (procedures.length > 0) {
            contextInfo += '\n📖 PROCÉDURES LIÉES (recherche par mots-clés):\n'
            for (const proc of procedures) {
              foundProcedures.push(proc.title)
              contextInfo += `\n🔧 "${proc.title}"\n`
              contextInfo += `   ${proc.description || ''}\n`
              if (proc.steps.length > 0) {
                contextInfo += `   Étapes: ${proc.steps.map(s => s.title).join(' → ')}\n`
              }
            }
          }

          // Recherche dans les tips
          const tips = await db.tip.findMany({
            where: {
              OR: keywords.map((keyword: string) => ({
                OR: [
                  { title: { contains: keyword, mode: 'insensitive' as const } },
                  { content: { contains: keyword, mode: 'insensitive' as const } },
                  { tags: { contains: keyword, mode: 'insensitive' as const } },
                ]
              }))
            },
            take: 3
          })

          if (tips.length > 0) {
            contextInfo += '\n💡 TIPS LIÉS:\n'
            for (const tip of tips) {
              foundTips.push(tip.title)
              contextInfo += `\n"${tip.title}" (${tip.category || 'Général'})\n`
              contextInfo += `   ${tip.content.slice(0, 200)}...\n`
            }
          }
        }
      } catch (error) {
        console.warn('Recherche par mots-clés échouée:', error)
      }
    }

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
        contextInfo += `\n\n📋 CONTEXTE PROCÉDURE EN COURS: "${procedure.title}"\n`
        contextInfo += `Description: ${procedure.description || 'Non spécifiée'}\n`
        contextInfo += `Étapes:\n${procedure.steps.map((s, i) => `  ${i + 1}. ${s.title}: ${s.description || s.instructions || ''}`).join('\n')}\n`
      }
    }

    // Ajouter résumé des références trouvées
    if (foundProcedures.length > 0 || foundTips.length > 0) {
      contextInfo += `\n📚 RÉFÉRENCES DISPONIBLES:\n`
      if (foundProcedures.length > 0) {
        contextInfo += `- Procédures: ${foundProcedures.join(', ')}\n`
      }
      if (foundTips.length > 0) {
        contextInfo += `- Tips: ${foundTips.join(', ')}\n`
      }
    } else {
      contextInfo += '\n⚠️ Aucune documentation spécifique trouvée dans la base. Utilise tes connaissances d\'expert.\n'
    }

    // Construire le message système avec le contexte
    const systemMessage = EXPERT_SYSTEM_PROMPT.replace('{context}', contextInfo)

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

    // Appeler OpenAI avec streaming (température légèrement réduite pour plus de précision)
    const openai = getOpenAIClient()
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages,
      stream: true,
      temperature: 0.5,
      max_tokens: 2000,
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
              controller.enqueue(
                new TextEncoder().encode(`data: ${JSON.stringify({ content })}\n\n`)
              )
            }
          }

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
