/**
 * Tests API pour la vision IA
 */

import { describe, it, expect, beforeAll, skip } from 'vitest'
import { getBaseURL, TEST_CREDENTIALS, authenticatedRequest } from '../utils/test-helpers'
import { checkDbConnection, seedTestData } from '../utils/test-db'
import { createBugReport } from '../utils/test-reports'

const baseURL = getBaseURL()

describe('Vision IA API', () => {
  let bugs: any[] = []

  beforeAll(async () => {
    const dbConnected = await checkDbConnection()
    if (!dbConnected) {
      throw new Error('Database connection failed')
    }
    
    await seedTestData()
  })

  describe('POST /api/vision', () => {
    it('should analyze image and suggest procedures', async () => {
      // Skip si OPENAI_API_KEY n'est pas configuré
      if (!process.env.OPENAI_API_KEY) {
        skip('OPENAI_API_KEY not configured')
        return
      }

      // Créer une image de test (base64 minimal)
      const testImageBase64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='

      try {
        const response = await authenticatedRequest('/vision', {
          method: 'POST',
          body: JSON.stringify({
            image: testImageBase64,
          }),
        })

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(data).toHaveProperty('analysis')
      } catch (error: any) {
        const bug = createBugReport(
          'analyze image with vision API',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should return 401 when not authenticated', async () => {
      try {
        const response = await fetch(`${baseURL}/api/vision`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image: 'test',
          }),
        })

        expect(response.status).toBe(401)
      } catch (error: any) {
        const bug = createBugReport(
          'analyze image without auth',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should return 400 with invalid image', async () => {
      try {
        const response = await authenticatedRequest('/vision', {
          method: 'POST',
          body: JSON.stringify({
            image: 'invalid-image-data',
          }),
        })

        expect([400, 500]).toContain(response.status)
      } catch (error: any) {
        const bug = createBugReport(
          'analyze invalid image',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })
})
