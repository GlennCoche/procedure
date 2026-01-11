import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'

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

    // Vérifier que l'exécution existe et appartient à l'utilisateur
    const execution = await db.execution.findUnique({
      where: { id: parseInt(params.id) },
      include: {
        procedure: true,
      },
    })

    if (!execution || execution.userId !== user.id) {
      return NextResponse.json({ error: 'Exécution non trouvée' }, { status: 404 })
    }

    // Vérifier que l'étape existe et appartient à la procédure
    const step = await db.step.findUnique({
      where: { id: body.step_id },
    })

    if (!step || step.procedureId !== execution.procedureId) {
      return NextResponse.json({ error: 'Étape invalide' }, { status: 400 })
    }

    // Chercher ou créer la stepExecution
    const stepExecution = await db.stepExecution.upsert({
      where: {
        executionId_stepId: {
          executionId: parseInt(params.id),
          stepId: body.step_id,
        },
      },
      update: {
        status: body.status,
        photos: body.photos ? JSON.stringify(body.photos) : null,
        comments: body.comments || null,
        completedAt: body.status === 'completed' ? new Date() : undefined,
      },
      create: {
        executionId: parseInt(params.id),
        stepId: body.step_id,
        status: body.status || 'pending',
        photos: body.photos ? JSON.stringify(body.photos) : null,
        comments: body.comments || null,
        completedAt: body.status === 'completed' ? new Date() : null,
      },
    })

    // Mettre à jour l'exécution si l'étape est complétée
    if (body.status === 'completed') {
      await db.execution.update({
        where: { id: parseInt(params.id) },
        data: {
          currentStep: step.order + 1,
        },
      })
    }

    // Formatter la réponse
    const formattedStepExecution = {
      ...stepExecution,
      photos: stepExecution.photos ? JSON.parse(stepExecution.photos) : [],
    }

    return NextResponse.json(formattedStepExecution)
  } catch (error) {
    console.error('Erreur PUT /api/executions/[id]/step:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}
