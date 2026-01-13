import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { comparePassword, createToken } from '@/lib/auth'

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    if (!email || !password) {
      return NextResponse.json(
        { error: 'Email et mot de passe requis' },
        { status: 400 }
      )
    }

    // Normaliser l'email en minuscules
    const normalizedEmail = email.toLowerCase().trim()

    // Trouver l'utilisateur
    const user = await db.user.findUnique({
      where: { email: normalizedEmail },
    })

    if (!user) {
      return NextResponse.json(
        { error: 'Email ou mot de passe incorrect' },
        { status: 401 }
      )
    }

    // Vérifier le mot de passe
    const isValid = await comparePassword(password, user.passwordHash)
    if (!isValid) {
      return NextResponse.json(
        { error: 'Email ou mot de passe incorrect' },
        { status: 401 }
      )
    }

    // Créer le token
    const token = createToken({ id: user.id, role: user.role })

    // Stocker dans un cookie HTTP-only (plus sécurisé que localStorage)
    // Utiliser Response.cookies() pour Next.js 15
    const response = NextResponse.json({
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
      },
    })

    response.cookies.set('auth-token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7, // 7 jours
      path: '/',
    })

    return response
  } catch (error: any) {
    console.error('Erreur login:', error)
    // Log plus détaillé pour le debugging
    console.error('Error details:', {
      message: error?.message,
      stack: error?.stack,
      name: error?.name,
      code: error?.code,
    })
    
    // Retourner plus de détails en développement
    const errorDetails: any = {
      error: 'Erreur serveur',
    }
    
    if (process.env.NODE_ENV === 'development') {
      errorDetails.details = error?.message
      errorDetails.stack = error?.stack
    } else {
      // En production, retourner un code d'erreur spécifique si possible
      if (error?.code === 'P1001') {
        errorDetails.details = 'Impossible de se connecter à la base de données'
      } else if (error?.message?.includes('DATABASE_URL')) {
        errorDetails.details = 'Configuration de la base de données manquante'
      }
    }
    
    return NextResponse.json(errorDetails, { status: 500 })
  }
}
