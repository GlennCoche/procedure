import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Vérifier si l'utilisateur est authentifié en vérifiant le cookie
  const authToken = request.cookies.get('auth-token')

  // Routes protégées
  const protectedPaths = ['/dashboard', '/admin']
  const isProtectedPath = protectedPaths.some((path) =>
    request.nextUrl.pathname.startsWith(path)
  )

  // Routes d'authentification
  const authPaths = ['/login', '/register']
  const isAuthPath = authPaths.some((path) =>
    request.nextUrl.pathname.startsWith(path)
  )

  // Si l'utilisateur n'est pas authentifié et essaie d'accéder à une route protégée
  if (isProtectedPath && !authToken) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('from', request.nextUrl.pathname)
    return NextResponse.redirect(loginUrl)
  }

  // Si l'utilisateur est authentifié et essaie d'accéder à une route d'authentification
  if (isAuthPath && authToken) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  // Pour les routes admin, vérifier le rôle (nécessite un appel API)
  // Cette vérification sera faite côté serveur dans les pages admin
  if (request.nextUrl.pathname.startsWith('/admin')) {
    // La vérification du rôle admin sera faite dans les pages admin
    // Ici on vérifie juste l'authentification
    if (!authToken) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/admin/:path*', '/login', '/register'],
}
