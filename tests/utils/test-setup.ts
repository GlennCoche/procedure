/**
 * Setup global pour les tests Vitest
 */
import { beforeAll, afterAll } from 'vitest'

// Configuration globale avant tous les tests
beforeAll(() => {
  // Définir les variables d'environnement de test si nécessaire
  process.env.NODE_ENV = 'test'
  process.env.DATABASE_URL = process.env.TEST_DATABASE_URL || process.env.DATABASE_URL
  process.env.JWT_SECRET = process.env.TEST_JWT_SECRET || process.env.JWT_SECRET || 'test-secret'
})

afterAll(() => {
  // Nettoyage après tous les tests
})
