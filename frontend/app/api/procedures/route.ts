import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'

export async function GET(request: NextRequest) {
  try {
    const user = await getCurrentUser()
    if (!user) {
      return NextResponse.json({ error: 'Non authentifié' }, { status: 401 })
    }

    // Récupérer les paramètres de query
    const { searchParams } = new URL(request.url)
    const skip = parseInt(searchParams.get('skip') || '0')
    const limit = parseInt(searchParams.get('limit') || '100')
    const category = searchParams.get('category')

    // Construire la requête
    // SQLite utilise 1/0, PostgreSQL utilise true/false - Prisma gère la conversion
    const where: any = { isActive: 1 }
    if (category) {
      where.category = category
    }

    const procedures = await db.procedure.findMany({
      where,
      skip,
      take: limit,
      include: {
        steps: {
          orderBy: { order: 'asc' },
        },
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

    // Parser les champs JSON
    const formattedProcedures = procedures.map((proc) => ({
      ...proc,
      tags: proc.tags ? (typeof proc.tags === 'string' ? JSON.parse(proc.tags) : proc.tags) : [],
      flowchartData: proc.flowchartData
        ? typeof proc.flowchartData === 'string'
          ? JSON.parse(proc.flowchartData)
          : proc.flowchartData
        : null,
      steps: proc.steps.map((step) => ({
        ...step,
        photos: step.photos ? (typeof step.photos === 'string' ? JSON.parse(step.photos) : step.photos) : [],
        files: step.files ? (typeof step.files === 'string' ? JSON.parse(step.files) : step.files) : [],
      })),
    }))

    return NextResponse.json(formattedProcedures)
  } catch (error) {
    console.error('Erreur GET /api/procedures:', error)
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

    // Créer la procédure avec Prisma
    const procedure = await db.procedure.create({
      data: {
        title: body.title,
        description: body.description,
        category: body.category,
        tags: body.tags ? JSON.stringify(body.tags) : null,
        isActive: 1, // SQLite: 1 (true), PostgreSQL: true (automatique)
        createdById: user.id,
        flowchartData: body.flowchart_data ? JSON.stringify(body.flowchart_data) : null,
        steps: {
          create:
            body.steps?.map((step: any, index: number) => ({
              title: step.title,
              description: step.description,
              instructions: step.instructions,
              order: step.order || index + 1,
              photos: step.photos ? JSON.stringify(step.photos) : null,
              files: step.files ? JSON.stringify(step.files) : null,
              validationType: step.validation_type || 'manual',
            })) || [],
        },
      },
      include: {
        steps: {
          orderBy: { order: 'asc' },
        },
        createdBy: {
          select: {
            email: true,
          },
        },
      },
    })

    // Formatter la réponse
    const formattedProcedure = {
      ...procedure,
      tags: procedure.tags ? JSON.parse(procedure.tags) : [],
      flowchartData: procedure.flowchartData ? JSON.parse(procedure.flowchartData) : null,
      steps: procedure.steps.map((step) => ({
        ...step,
        photos: step.photos ? JSON.parse(step.photos) : [],
        files: step.files ? JSON.parse(step.files) : [],
      })),
    }

    return NextResponse.json(formattedProcedure, { status: 201 })
  } catch (error) {
    console.error('Erreur POST /api/procedures:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}
