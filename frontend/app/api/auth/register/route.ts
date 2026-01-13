import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { hashPassword, createToken } from '@/lib/auth'

export async function POST(request: NextRequest) {
  try {
    const { email, password, role } = await request.json()

    if (!email || !password) {
      return NextResponse.json(
        { error: 'Email et mot de passe requis' },
        { status: 400 }
      )
    }

    // Normaliser l'email en minuscules
    const normalizedEmail = email.toLowerCase().trim()

    // Vérifier si l'email existe déjà
    const existingUser = await db.user.findUnique({
      where: { email: normalizedEmail },
    })

    if (existingUser) {
      return NextResponse.json(
        { error: 'Cet email est déjà enregistré' },
        { status: 400 }
      )
    }

    // Hasher le mot de passe
    const passwordHash = await hashPassword(password)

    // Créer l'utilisateur
    const user = await db.user.create({
      data: {
        email: normalizedEmail,
        passwordHash,
        role: role || 'technician',
      },
      select: {
        id: true,
        email: true,
        role: true,
      },
    })

    // Créer le token
    const token = createToken({ id: user.id, role: user.role })

    // Stocker dans un cookie HTTP-only
    // Utiliser Response.cookies() pour Next.js 15
    const response = NextResponse.json(
      {
        user: {
          id: user.id,
          email: user.email,
          role: user.role,
        },
      },
      { status: 201 }
    )

    response.cookies.set('auth-token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7, // 7 jours
      path: '/',
    })

    return response
  } catch (error: any) {
    console.error('Erreur register:', error)
    // Log plus détaillé pour le debugging
    console.error('Error details:', {
      message: error?.message,
      stack: error?.stack,
      name: error?.name,
    })
    return NextResponse.json(
      { error: 'Erreur serveur', details: process.env.NODE_ENV === 'development' ? error?.message : undefined },
      { status: 500 }
    )
  }
}
