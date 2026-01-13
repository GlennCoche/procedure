import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'

/**
 * POST /api/chat/feedback
 * Enregistre un rating (like/dislike) sur une réponse de l'IA
 */
export async function POST(request: NextRequest) {
  try {
    const user = await getCurrentUser()
    if (!user) {
      return new Response('Non authentifié', { status: 401 })
    }

    const { messageId, rating, feedback } = await request.json()

    if (!messageId || !rating) {
      return new Response('messageId et rating requis', { status: 400 })
    }

    if (!['positive', 'negative'].includes(rating)) {
      return new Response('Rating doit être "positive" ou "negative"', { status: 400 })
    }

    // Vérifier que le message appartient à l'utilisateur
    const message = await db.chatMessage.findFirst({
      where: {
        id: messageId,
        userId: user.id,
      },
    })

    if (!message) {
      return new Response('Message non trouvé', { status: 404 })
    }

    // Créer ou mettre à jour le rating
    const existingRating = await db.messageRating.findFirst({
      where: { messageId },
    })

    let savedRating
    if (existingRating) {
      // Mettre à jour
      savedRating = await db.messageRating.update({
        where: { id: existingRating.id },
        data: {
          rating,
          feedback: feedback || null,
        },
      })
    } else {
      // Créer
      savedRating = await db.messageRating.create({
        data: {
          messageId,
          rating,
          feedback: feedback || null,
        },
      })
    }

    return NextResponse.json({
      success: true,
      rating: savedRating,
    })
  } catch (error) {
    console.error('Erreur enregistrement feedback:', error)
    return new Response('Erreur serveur', { status: 500 })
  }
}

/**
 * GET /api/chat/feedback/stats
 * Récupère les statistiques de feedback pour l'auto-learning
 */
export async function GET(request: NextRequest) {
  try {
    const user = await getCurrentUser()
    if (!user) {
      return new Response('Non authentifié', { status: 401 })
    }

    // Récupérer les messages bien notés pour l'auto-learning
    const positiveRatings = await db.messageRating.findMany({
      where: {
        rating: 'positive',
        message: {
          userId: user.id,
        },
      },
      include: {
        message: {
          select: {
            message: true,
            response: true,
          },
        },
      },
      orderBy: { createdAt: 'desc' },
      take: 10,
    })

    // Statistiques globales
    const stats = await db.messageRating.groupBy({
      by: ['rating'],
      _count: {
        rating: true,
      },
      where: {
        message: {
          userId: user.id,
        },
      },
    })

    return NextResponse.json({
      positiveExamples: positiveRatings.map((r) => ({
        question: r.message.message,
        answer: r.message.response,
        feedback: r.feedback,
      })),
      stats: stats.reduce(
        (acc, s) => {
          acc[s.rating] = s._count.rating
          return acc
        },
        {} as Record<string, number>
      ),
    })
  } catch (error) {
    console.error('Erreur récupération stats feedback:', error)
    return new Response('Erreur serveur', { status: 500 })
  }
}
