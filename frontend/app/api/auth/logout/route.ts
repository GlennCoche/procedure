import { NextResponse } from 'next/server'

export async function POST() {
  try {
    // Supprimer le cookie
    // Utiliser Response.cookies() pour Next.js 15
    const response = NextResponse.json({ success: true })
    response.cookies.delete('auth-token')

    return response
  } catch (error: any) {
    console.error('Erreur logout:', error)
    return NextResponse.json(
      { error: 'Erreur serveur' },
      { status: 500 }
    )
  }
}
