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

    const execution = await db.execution.findUnique({
      where: { id: parseInt(params.id) },
    })

    if (!execution || execution.userId !== user.id) {
      return NextResponse.json({ error: 'Exécution non trouvée' }, { status: 404 })
    }

    const updatedExecution = await db.execution.update({
      where: { id: parseInt(params.id) },
      data: {
        status: 'completed',
        completedAt: new Date(),
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
    console.error('Erreur PUT /api/executions/[id]/complete:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}
