import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'

export async function GET(request: NextRequest) {
  try {
    const user = await getCurrentUser()
    if (!user) {
      return NextResponse.json({ error: 'Non authentifié' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const search = searchParams.get('search')
    const category = searchParams.get('category')
    const skip = parseInt(searchParams.get('skip') || '0')
    const limit = parseInt(searchParams.get('limit') || '100')

    const where: any = {}

    if (search) {
      where.OR = [
        {
          title: {
            contains: search,
            mode: 'insensitive' as const,
          },
        },
        {
          content: {
            contains: search,
            mode: 'insensitive' as const,
          },
        },
      ]
    }

    if (category) {
      where.category = category
    }

    const tips = await db.tip.findMany({
      where,
      skip,
      take: limit,
      include: {
        createdBy: {
          select: {
            email: true,
          },
        },
      },
      orderBy: {
        createdAt: 'desc',
      },
    })

    // Formatter les réponses
    const formattedTips = tips.map((tip) => ({
      ...tip,
      tags: tip.tags ? (typeof tip.tags === 'string' ? JSON.parse(tip.tags) : tip.tags) : [],
    }))

    return NextResponse.json(formattedTips)
  } catch (error) {
    console.error('Erreur GET /api/tips:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const user = await getCurrentUser()
    if (!user || user.role !== 'admin') {
      return NextResponse.json({ error: 'Accès refusé' }, { status: 403 })
    }

    const body = await request.json()

    const tip = await db.tip.create({
      data: {
        title: body.title,
        content: body.content,
        category: body.category,
        tags: body.tags ? JSON.stringify(body.tags) : null,
        createdById: user.id,
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

    return NextResponse.json(formattedTip, { status: 201 })
  } catch (error) {
    console.error('Erreur POST /api/tips:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}
