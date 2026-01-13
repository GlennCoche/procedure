/**
 * Tests de sécurité
 */

import { describe, it, expect, beforeAll } from 'vitest'
import { getBaseURL, TEST_CREDENTIALS, authenticatedRequest } from '../utils/test-helpers'
import { checkDbConnection, seedTestData } from '../utils/test-db'
import { createBugReport } from '../utils/test-reports'

const baseURL = getBaseURL()

describe('Security Tests', () => {
  let bugs: any[] = []
  let procedureId: number | null = null

  beforeAll(async () => {
    const dbConnected = await checkDbConnection()
    if (!dbConnected) {
      throw new Error('Database connection failed')
    }
    
    await seedTestData()

    // Créer une procédure pour les tests
    try {
      const createResponse = await authenticatedRequest('/procedures', {
        method: 'POST',
        body: JSON.stringify({
          title: 'Security Test Procedure',
          description: 'Procedure for security testing',
          category: 'Test',
          steps: [{ order: 1, title: 'Step 1', validationType: 'manual' }],
        }),
      }, TEST_CREDENTIALS.admin)
      const createData = await createResponse.json()
      procedureId = createData.id
    } catch (error) {
      console.error('Failed to create test procedure:', error)
    }
  })

  describe('Permission Checks', () => {
    it('should prevent technician from creating procedures', async () => {
      try {
        const response = await authenticatedRequest('/procedures', {
          method: 'POST',
          body: JSON.stringify({
            title: 'Hacked Procedure',
            description: 'Should not work',
          }),
        }, TEST_CREDENTIALS.technician)

        expect(response.status).toBe(403)
        const data = await response.json()
        expect(data).toHaveProperty('error')
      } catch (error: any) {
        const bug = createBugReport(
          'technician creating procedure (should fail)',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should prevent technician from deleting procedures', async () => {
      if (!procedureId) return

      try {
        const response = await authenticatedRequest(`/procedures/${procedureId}`, {
          method: 'DELETE',
        }, TEST_CREDENTIALS.technician)

        expect(response.status).toBe(403)
      } catch (error: any) {
        const bug = createBugReport(
          'technician deleting procedure (should fail)',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('Input Validation', () => {
    it('should validate email format on login', async () => {
      try {
        const response = await fetch(`${baseURL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: 'invalid-email',
            password: 'password',
          }),
        })

        // Devrait retourner 400 ou 401
        expect([400, 401]).toContain(response.status)
      } catch (error: any) {
        const bug = createBugReport(
          'validate email format',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should validate required fields', async () => {
      try {
        const response = await fetch(`${baseURL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}),
        })

        expect(response.status).toBe(400)
      } catch (error: any) {
        const bug = createBugReport(
          'validate required fields',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('SQL Injection Protection', () => {
    it('should handle SQL injection attempts safely', async () => {
      try {
        // Tenter une injection SQL dans un paramètre
        const response = await authenticatedRequest('/procedures?category=test\'; DROP TABLE procedures; --', {
          method: 'GET',
        })

        // Ne devrait pas crasher, peut retourner 200 avec résultats vides ou 400
        expect([200, 400]).toContain(response.status)
      } catch (error: any) {
        const bug = createBugReport(
          'SQL injection protection',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })
})
