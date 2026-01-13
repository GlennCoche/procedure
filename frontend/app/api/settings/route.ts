import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'

export async function GET(request: NextRequest) {
  const user = await getCurrentUser()
  if (!user) {
    return NextResponse.json({ error: 'Non authentifié' }, { status: 401 })
  }

  try {
    const { searchParams } = new URL(request.url)
    const brand = searchParams.get('brand')
    const category = searchParams.get('category')
    const equipmentType = searchParams.get('equipmentType')
    const country = searchParams.get('country') || 'FR'
    const search = searchParams.get('search')

    // Construire les filtres
    const where: any = { country }

    if (brand) {
      where.brand = brand
    }

    if (category) {
      where.category = category
    }

    if (equipmentType) {
      where.equipmentType = equipmentType
    }

    if (search) {
      where.OR = [
        { name: { contains: search, mode: 'insensitive' } },
        { value: { contains: search, mode: 'insensitive' } },
        { notes: { contains: search, mode: 'insensitive' } },
      ]
    }

    const settings = await db.setting.findMany({
      where,
      orderBy: [
        { brand: 'asc' },
        { category: 'asc' },
        { name: 'asc' },
      ],
    })

    // Obtenir les valeurs distinctes pour les filtres
    const brands = await db.setting.findMany({
      where: { country },
      distinct: ['brand'],
      select: { brand: true },
    })

    const categories = await db.setting.findMany({
      where: { country },
      distinct: ['category'],
      select: { category: true },
    })

    const equipmentTypes = await db.setting.findMany({
      where: { country },
      distinct: ['equipmentType'],
      select: { equipmentType: true },
    })

    return NextResponse.json({
      settings,
      filters: {
        brands: brands.map(b => b.brand),
        categories: categories.map(c => c.category),
        equipmentTypes: equipmentTypes.map(e => e.equipmentType),
      },
      total: settings.length,
    })
  } catch (error) {
    console.error('Erreur récupération settings:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  const user = await getCurrentUser()
  if (!user || user.role !== 'admin') {
    return NextResponse.json({ error: 'Non autorisé' }, { status: 403 })
  }

  try {
    const data = await request.json()

    const setting = await db.setting.create({
      data: {
        brand: data.brand,
        equipmentType: data.equipmentType,
        model: data.model || null,
        category: data.category,
        name: data.name,
        value: data.value,
        unit: data.unit || null,
        country: data.country || 'FR',
        sourceDoc: data.sourceDoc || null,
        pageNumber: data.pageNumber || null,
        notes: data.notes || null,
      },
    })

    return NextResponse.json(setting)
  } catch (error) {
    console.error('Erreur création setting:', error)
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}
