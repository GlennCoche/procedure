import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'

/**
 * GET /api/chat/history
 * Récupère l'historique des conversations de l'utilisateur
 */
export async function GET(request: NextRequest) {
  try {
    const user = await getCurrentUser()
    if (!user) {
      return new Response('Non authentifié', { status: 401 })
    }

    // Récupérer les paramètres de pagination
    const { searchParams } = new URL(request.url)
    const limit = parseInt(searchParams.get('limit') || '50')
    const offset = parseInt(searchParams.get('offset') || '0')

    // Récupérer les messages (sans ratings pour éviter les erreurs si table n'existe pas)
    const messages = await db.chatMessage.findMany({
      where: { userId: user.id },
      orderBy: { createdAt: 'asc' },
      skip: offset,
      take: limit,
    })

    // Compter le total de messages
    const total = await db.chatMessage.count({
      where: { userId: user.id },
    })

    // Essayer de récupérer les ratings séparément (si la table existe)
    let ratingsMap: Record<number, { rating: string; feedback: string | null }> = {}
    try {
      const ratings = await db.messageRating.findMany({
        where: {
          messageId: { in: messages.map(m => m.id) }
        },
        select: {
          messageId: true,
          rating: true,
          feedback: true,
        }
      })
      ratingsMap = ratings.reduce((acc, r) => {
        acc[r.messageId] = { rating: r.rating, feedback: r.feedback }
        return acc
      }, {} as Record<number, { rating: string; feedback: string | null }>)
    } catch {
      // Table ratings n'existe pas encore, on continue sans
      console.log('Table message_ratings non disponible, chargement sans ratings')
    }

    return NextResponse.json({
      messages: messages.map((msg) => ({
        id: msg.id,
        message: msg.message,
        response: msg.response,
        context: msg.context ? JSON.parse(msg.context) : null,
        createdAt: msg.createdAt,
        rating: ratingsMap[msg.id]?.rating || null,
        feedback: ratingsMap[msg.id]?.feedback || null,
      })),
      total,
      hasMore: offset + messages.length < total,
    })
  } catch (error) {
    console.error('Erreur récupération historique:', error)
    return new Response(JSON.stringify({ error: 'Erreur serveur', details: String(error) }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

/**
 * DELETE /api/chat/history
 * Efface l'historique des conversations de l'utilisateur
 */
export async function DELETE(request: NextRequest) {
  try {
    const user = await getCurrentUser()
    if (!user) {
      return new Response('Non authentifié', { status: 401 })
    }

    // Supprimer tous les messages de l'utilisateur
    await db.chatMessage.deleteMany({
      where: { userId: user.id },
    })

    return NextResponse.json({ success: true, message: 'Historique effacé' })
  } catch (error) {
    console.error('Erreur suppression historique:', error)
    return new Response('Erreur serveur', { status: 500 })
  }
}
