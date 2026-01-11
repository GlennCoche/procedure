import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await getCurrentUser()
    if (!user) {
      return NextResponse.json({ error: 'Non authentifié' }, { status: 401 })
    }

    const tip = await db.tip.findUnique({
      where: { id: parseInt(params.id) },
      include: {
        createdBy: {
          select: {
            email: true,
          },
        },
      },
    })

    if (!tip) {
      return NextResponse.json({ error: 'Non trouvé' }, { status: 404 })
    }

    // Formatter la réponse
    const formattedTip = {
      ...tip,
      tags: tip.tags ? (typeof tip.tags === 'string' ? JSON.parse(tip.tags) : tip.tags) : [],
    }

    return NextResponse.json(formattedTip)
  } catch (error) {
    console.error('Erreur GET /api/tips/[id]:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await getCurrentUser()
    if (!user || user.role !== 'admin') {
      return NextResponse.json({ error: 'Accès refusé' }, { status: 403 })
    }

    const body = await request.json()

    const tip = await db.tip.update({
      where: { id: parseInt(params.id) },
      data: {
        title: body.title,
        content: body.content,
        category: body.category,
        tags: body.tags ? JSON.stringify(body.tags) : null,
      },
      include: {
        createdBy: {
          select: {
            email: true,
          },
        },
      },
    })

    // Formatter la réponse
    const formattedTip = {
      ...tip,
      tags: tip.tags ? JSON.parse(tip.tags) : [],
    }

    return NextResponse.json(formattedTip)
  } catch (error) {
    console.error('Erreur PUT /api/tips/[id]:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await getCurrentUser()
    if (!user || user.role !== 'admin') {
      return NextResponse.json({ error: 'Accès refusé' }, { status: 403 })
    }

    await db.tip.delete({
      where: { id: parseInt(params.id) },
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Erreur DELETE /api/tips/[id]:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}
