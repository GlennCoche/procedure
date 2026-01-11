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

    const procedure = await db.procedure.findUnique({
      where: { id: parseInt(params.id) },
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

    if (!procedure) {
      return NextResponse.json({ error: 'Non trouvé' }, { status: 404 })
    }

    // Formatter la réponse
    const formattedProcedure = {
      ...procedure,
      tags: procedure.tags ? (typeof procedure.tags === 'string' ? JSON.parse(procedure.tags) : procedure.tags) : [],
      flowchartData: procedure.flowchartData
        ? typeof procedure.flowchartData === 'string'
          ? JSON.parse(procedure.flowchartData)
          : procedure.flowchartData
        : null,
      steps: procedure.steps.map((step) => ({
        ...step,
        photos: step.photos ? (typeof step.photos === 'string' ? JSON.parse(step.photos) : step.photos) : [],
        files: step.files ? (typeof step.files === 'string' ? JSON.parse(step.files) : step.files) : [],
      })),
    }

    return NextResponse.json(formattedProcedure)
  } catch (error) {
    console.error('Erreur GET /api/procedures/[id]:', error)
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

    // Vérifier que la procédure existe
    const existingProcedure = await db.procedure.findUnique({
      where: { id: parseInt(params.id) },
    })

    if (!existingProcedure) {
      return NextResponse.json({ error: 'Non trouvé' }, { status: 404 })
    }

    // Supprimer les anciennes étapes
    await db.step.deleteMany({
      where: { procedureId: parseInt(params.id) },
    })

    // Mettre à jour la procédure
    const procedure = await db.procedure.update({
      where: { id: parseInt(params.id) },
      data: {
        title: body.title,
        description: body.description,
        category: body.category,
        tags: body.tags ? JSON.stringify(body.tags) : null,
        flowchartData: body.flowchart_data ? JSON.stringify(body.flowchart_data) : null,
        isActive: body.is_active !== undefined ? (body.is_active ? 1 : 0) : existingProcedure.isActive,
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

    // Créer les nouvelles étapes
    if (body.steps && body.steps.length > 0) {
      await db.step.createMany({
        data: body.steps.map((step: any, index: number) => ({
          procedureId: parseInt(params.id),
          title: step.title,
          description: step.description,
          instructions: step.instructions,
          order: step.order || index + 1,
          photos: step.photos ? JSON.stringify(step.photos) : null,
          files: step.files ? JSON.stringify(step.files) : null,
          validationType: step.validation_type || 'manual',
        })),
      })
    }

    // Recharger avec les étapes
    const updatedProcedure = await db.procedure.findUnique({
      where: { id: parseInt(params.id) },
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
      ...updatedProcedure!,
      tags: updatedProcedure!.tags ? JSON.parse(updatedProcedure!.tags) : [],
      flowchartData: updatedProcedure!.flowchartData ? JSON.parse(updatedProcedure!.flowchartData) : null,
      steps: updatedProcedure!.steps.map((step) => ({
        ...step,
        photos: step.photos ? JSON.parse(step.photos) : [],
        files: step.files ? JSON.parse(step.files) : [],
      })),
    }

    return NextResponse.json(formattedProcedure)
  } catch (error) {
    console.error('Erreur PUT /api/procedures/[id]:', error)
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

    const procedure = await db.procedure.findUnique({
      where: { id: parseInt(params.id) },
    })

    if (!procedure) {
      return NextResponse.json({ error: 'Non trouvé' }, { status: 404 })
    }

    // Soft delete: marquer comme inactive
    await db.procedure.update({
      where: { id: parseInt(params.id) },
      data: { isActive: 0 }, // SQLite: 0, PostgreSQL: false
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Erreur DELETE /api/procedures/[id]:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}
