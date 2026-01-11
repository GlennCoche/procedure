import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function POST() {
  try {
    // Supprimer le cookie
    cookies().delete('auth-token')

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Erreur logout:', error)
    return NextResponse.json(
      { error: 'Erreur serveur' },
      { status: 500 }
    )
  }
}
