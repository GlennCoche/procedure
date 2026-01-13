import { NextResponse } from 'next/server'
import { db } from '@/lib/db'

export async function GET() {
  try {
    // Vérifier la connexion à la base de données
    const dbStatus = await db.$queryRaw`SELECT 1 as test`
    
    // Vérifier que les API routes fonctionnent
    const backendStatus = {
      running: true,
      url: process.env.NEXT_PUBLIC_APP_URL || process.env.VERCEL_URL || 'https://procedure1.vercel.app'
    }
    
    const frontendStatus = {
      running: true,
      url: process.env.NEXT_PUBLIC_APP_URL || process.env.VERCEL_URL || 'https://procedure1.vercel.app'
    }
    
    return NextResponse.json({
      backend: backendStatus,
      frontend: frontendStatus,
      database: {
        connected: true,
        provider: 'postgresql'
      }
    })
  } catch (error: any) {
    console.error('Erreur lors de la vérification du status:', error)
    
    // Même en cas d'erreur DB, les services Next.js sont actifs
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || process.env.VERCEL_URL || 'https://procedure1.vercel.app'
    
    return NextResponse.json({
      backend: {
        running: true,
        url: baseUrl
      },
      frontend: {
        running: true,
        url: baseUrl
      },
      database: {
        connected: false,
        error: error.message
      }
    })
  }
}
