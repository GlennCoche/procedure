/**
 * Helpers pour la base de données de test
 */

import { PrismaClient } from '@prisma/client'

let prisma: PrismaClient | null = null

/**
 * Obtenir une instance Prisma pour les tests
 */
export function getTestDb(): PrismaClient {
  if (!prisma) {
    prisma = new PrismaClient({
      log: process.env.DEBUG ? ['query', 'error', 'warn'] : ['error'],
    })
  }
  return prisma
}

/**
 * Nettoyer la base de données de test
 */
export async function cleanupTestDb(): Promise<void> {
  const db = getTestDb()
  
  try {
    // Supprimer dans l'ordre des dépendances
    await db.stepExecution.deleteMany({})
    await db.execution.deleteMany({})
    await db.step.deleteMany({})
    await db.procedure.deleteMany({})
    await db.chatMessage.deleteMany({})
    await db.tip.deleteMany({})
    await db.user.deleteMany({
      where: {
        email: {
          not: 'admin@procedures.local', // Garder l'admin
        },
      },
    })
  } catch (error) {
    console.error('Error cleaning up test database:', error)
  }
}

/**
 * Créer des données de test
 */
export async function seedTestData(): Promise<void> {
  const db = getTestDb()
  
  // Créer un utilisateur technicien de test s'il n'existe pas
  const technician = await db.user.findUnique({
    where: { email: 'technician@procedures.local' },
  })

  if (!technician) {
    const bcrypt = require('bcryptjs')
    const passwordHash = await bcrypt.hash('Technician123!', 10)
    
    await db.user.create({
      data: {
        email: 'technician@procedures.local',
        passwordHash,
        role: 'technician',
      },
    })
  }
}

/**
 * Vérifier que la base de données est accessible
 */
export async function checkDbConnection(): Promise<boolean> {
  try {
    const db = getTestDb()
    await db.$queryRaw`SELECT 1`
    return true
  } catch (error) {
    console.error('Database connection failed:', error)
    return false
  }
}

/**
 * Fermer la connexion Prisma
 */
export async function closeTestDb(): Promise<void> {
  if (prisma) {
    await prisma.$disconnect()
    prisma = null
  }
}
