import { NextResponse } from 'next/server'
import { db } from '@/lib/db'

/**
 * Endpoint de test pour diagnostiquer les problèmes de connexion
 * À supprimer après diagnostic
 */
export async function GET() {
  const diagnostics: any = {
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV,
    checks: {},
  }

  // Test 1: Variables d'environnement
  diagnostics.checks.env = {
    DATABASE_URL: !!process.env.DATABASE_URL,
    JWT_SECRET: !!process.env.JWT_SECRET,
    NEXTAUTH_URL: process.env.NEXTAUTH_URL || 'non défini',
    NEXTAUTH_SECRET: !!process.env.NEXTAUTH_SECRET,
  }

  // Test 2: Connexion à la base de données
  try {
    const userCount = await db.user.count()
    diagnostics.checks.database = {
      connected: true,
      userCount,
    }
  } catch (error: any) {
    diagnostics.checks.database = {
      connected: false,
      error: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
    }
  }

  // Test 3: Test de requête simple
  try {
    const firstUser = await db.user.findFirst({
      select: {
        id: true,
        email: true,
        role: true,
      },
    })
    diagnostics.checks.query = {
      success: true,
      hasUsers: !!firstUser,
      sampleUser: firstUser ? { id: firstUser.id, email: firstUser.email, role: firstUser.role } : null,
    }
  } catch (error: any) {
    diagnostics.checks.query = {
      success: false,
      error: error.message,
    }
  }

  return NextResponse.json(diagnostics, {
    status: diagnostics.checks.database?.connected ? 200 : 500,
  })
}
