import { NextRequest, NextResponse } from 'next/server'
import { getCurrentUser } from '@/lib/auth'
import { db } from '@/lib/db'
import OpenAI from 'openai'

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

export async function POST(request: NextRequest) {
  const user = await getCurrentUser()
  if (!user) {
    return NextResponse.json({ error: 'Non authentifié' }, { status: 401 })
  }

  try {
    const formData = await request.formData()
    const file = formData.get('image') as File

    if (!file) {
      return NextResponse.json({ error: 'Image requise' }, { status: 400 })
    }

    // Convertir en base64
    const arrayBuffer = await file.arrayBuffer()
    const buffer = Buffer.from(arrayBuffer)
    const base64 = buffer.toString('base64')

    // Appeler OpenAI Vision
    const response = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'text',
              text: 'Identifie cet équipement photovoltaïque et suggère des procédures de maintenance appropriées. Décris l\'état de l\'équipement, les problèmes potentiels et les actions recommandées. Sois précis et technique.',
            },
            {
              type: 'image_url',
              image_url: {
                url: `data:${file.type};base64,${base64}`,
              },
            },
          ],
        },
      ],
      max_tokens: 1000,
    })

    const analysis = response.choices[0]?.message?.content || ''

    // Rechercher des procédures similaires dans la DB
    // Extraire des mots-clés de l'analyse
    const keywords = analysis
      .toLowerCase()
      .split(/\s+/)
      .filter((word) => word.length > 4)
      .slice(0, 5)

    const suggestedProcedures = await db.procedure.findMany({
      where: {
        isActive: 1, // SQLite: 1, PostgreSQL: true
        OR: [
          ...keywords.map((keyword) => ({
            title: {
              contains: keyword,
              mode: 'insensitive' as const,
            },
          })),
          ...keywords.map((keyword) => ({
            description: {
              contains: keyword,
              mode: 'insensitive' as const,
            },
          })),
        ],
      },
      take: 5,
      select: {
        id: true,
        title: true,
        description: true,
        category: true,
      },
    })

    return NextResponse.json({
      analysis,
      suggestedProcedures: suggestedProcedures.map((p) => ({
        id: p.id,
        title: p.title,
        description: p.description,
        category: p.category,
      })),
    })
  } catch (error) {
    console.error('Erreur vision:', error)
    return NextResponse.json(
      { error: 'Erreur lors de l\'analyse de l\'image' },
      { status: 500 }
    )
  }
}
