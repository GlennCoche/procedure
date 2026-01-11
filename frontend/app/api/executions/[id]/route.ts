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

    const execution = await db.execution.findUnique({
      where: { id: parseInt(params.id) },
      include: {
        procedure: {
          include: {
            steps: {
              orderBy: { order: 'asc' },
            },
          },
        },
        stepExecutions: {
          include: {
            step: true,
          },
        },
      },
    })

    if (!execution) {
      return NextResponse.json({ error: 'Non trouvé' }, { status: 404 })
    }

    if (execution.userId !== user.id) {
      return NextResponse.json({ error: 'Accès refusé' }, { status: 403 })
    }

    // Formatter la réponse
    const formattedExecution = {
      ...execution,
      procedure: {
        ...execution.procedure,
        tags: execution.procedure.tags
          ? typeof execution.procedure.tags === 'string'
            ? JSON.parse(execution.procedure.tags)
            : execution.procedure.tags
          : [],
        flowchartData: execution.procedure.flowchartData
          ? typeof execution.procedure.flowchartData === 'string'
            ? JSON.parse(execution.procedure.flowchartData)
            : execution.procedure.flowchartData
          : null,
        steps: execution.procedure.steps.map((step) => ({
          ...step,
          photos: step.photos ? (typeof step.photos === 'string' ? JSON.parse(step.photos) : step.photos) : [],
          files: step.files ? (typeof step.files === 'string' ? JSON.parse(step.files) : step.files) : [],
        })),
      },
      stepExecutions: execution.stepExecutions.map((se) => ({
        ...se,
        photos: se.photos ? (typeof se.photos === 'string' ? JSON.parse(se.photos) : se.photos) : [],
      })),
    }

    return NextResponse.json(formattedExecution)
  } catch (error) {
    console.error('Erreur GET /api/executions/[id]:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await getCurrentUser()
    if (!user) {
      return NextResponse.json({ error: 'Non authentifié' }, { status: 401 })
    }

    const body = await request.json()

    const execution = await db.execution.findUnique({
      where: { id: parseInt(params.id) },
    })

    if (!execution) {
      return NextResponse.json({ error: 'Non trouvé' }, { status: 404 })
    }

    if (execution.userId !== user.id) {
      return NextResponse.json({ error: 'Accès refusé' }, { status: 403 })
    }

    const updatedExecution = await db.execution.update({
      where: { id: parseInt(params.id) },
      data: {
        status: body.status || execution.status,
        currentStep: body.current_step !== undefined ? body.current_step : execution.currentStep,
        completedAt: body.status === 'completed' ? new Date() : execution.completedAt,
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

    return NextResponse.json(updatedExecution)
  } catch (error) {
    console.error('Erreur PUT /api/executions/[id]:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}
