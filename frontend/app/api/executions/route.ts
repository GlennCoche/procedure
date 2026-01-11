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
    const procedureId = searchParams.get('procedure_id')

    const where: any = { userId: user.id }
    if (procedureId) {
      where.procedureId = parseInt(procedureId)
    }

    const executions = await db.execution.findMany({
      where,
      include: {
        procedure: {
          select: {
            id: true,
            title: true,
            description: true,
          },
        },
        stepExecutions: {
          include: {
            step: {
              select: {
                id: true,
                title: true,
                order: true,
              },
            },
          },
        },
      },
      orderBy: {
        startedAt: 'desc',
      },
    })

    // Formatter les réponses
    const formattedExecutions = executions.map((exec) => ({
      ...exec,
      stepExecutions: exec.stepExecutions.map((se) => ({
        ...se,
        photos: se.photos ? (typeof se.photos === 'string' ? JSON.parse(se.photos) : se.photos) : [],
      })),
    }))

    return NextResponse.json(formattedExecutions)
  } catch (error) {
    console.error('Erreur GET /api/executions:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const user = await getCurrentUser()
    if (!user) {
      return NextResponse.json({ error: 'Non authentifié' }, { status: 401 })
    }

    const body = await request.json()

    // Vérifier que la procédure existe
    const procedure = await db.procedure.findUnique({
      where: { id: body.procedure_id },
    })

    if (!procedure) {
      return NextResponse.json({ error: 'Procédure non trouvée' }, { status: 404 })
    }

    const execution = await db.execution.create({
      data: {
        userId: user.id,
        procedureId: body.procedure_id,
        status: body.status || 'in_progress',
        currentStep: body.current_step || 0,
      },
      include: {
        procedure: {
          include: {
            steps: {
              orderBy: { order: 'asc' },
            },
          },
        },
        stepExecutions: true,
      },
    })

    return NextResponse.json(execution, { status: 201 })
  } catch (error) {
    console.error('Erreur POST /api/executions:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}
