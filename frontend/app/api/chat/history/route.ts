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

    // Récupérer les messages avec leurs ratings
    const messages = await db.chatMessage.findMany({
      where: { userId: user.id },
      orderBy: { createdAt: 'asc' },
      skip: offset,
      take: limit,
      include: {
        ratings: {
          select: {
            id: true,
            rating: true,
            feedback: true,
            createdAt: true,
          },
        },
      },
    })

    // Compter le total de messages
    const total = await db.chatMessage.count({
      where: { userId: user.id },
    })

    return NextResponse.json({
      messages: messages.map((msg) => ({
        id: msg.id,
        message: msg.message,
        response: msg.response,
        context: msg.context ? JSON.parse(msg.context) : null,
        createdAt: msg.createdAt,
        rating: msg.ratings?.[0]?.rating || null,
        feedback: msg.ratings?.[0]?.feedback || null,
      })),
      total,
      hasMore: offset + messages.length < total,
    })
  } catch (error) {
    console.error('Erreur récupération historique:', error)
    return new Response('Erreur serveur', { status: 500 })
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
