/**
 * Tests API pour le chat IA
 */

import { describe, it, expect, beforeAll, skip } from 'vitest'
import { getBaseURL, TEST_CREDENTIALS, authenticatedRequest } from '../utils/test-helpers'
import { checkDbConnection, seedTestData } from '../utils/test-db'
import { createBugReport } from '../utils/test-reports'

const baseURL = getBaseURL()

describe('Chat IA API', () => {
  let bugs: any[] = []

  beforeAll(async () => {
    const dbConnected = await checkDbConnection()
    if (!dbConnected) {
      throw new Error('Database connection failed')
    }
    
    await seedTestData()
  })

  describe('POST /api/chat', () => {
    it('should send message and get AI response', async () => {
      // Skip si OPENAI_API_KEY n'est pas configuré
      if (!process.env.OPENAI_API_KEY) {
        skip('OPENAI_API_KEY not configured')
        return
      }

      try {
        const response = await authenticatedRequest('/chat', {
          method: 'POST',
          body: JSON.stringify({
            message: 'Bonjour, comment fonctionne la maintenance photovoltaïque?',
          }),
        })

        expect(response.status).toBe(200)
        // Le chat peut retourner un stream, donc on vérifie juste que la réponse est OK
        const contentType = response.headers.get('content-type')
        expect(contentType).toBeTruthy()
      } catch (error: any) {
        const bug = createBugReport(
          'send chat message',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should return 401 when not authenticated', async () => {
      try {
        const response = await fetch(`${baseURL}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: 'Test message',
          }),
        })

        expect(response.status).toBe(401)
      } catch (error: any) {
        const bug = createBugReport(
          'send chat message without auth',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should return 400 with empty message', async () => {
      try {
        const response = await authenticatedRequest('/chat', {
          method: 'POST',
          body: JSON.stringify({
            message: '',
          }),
        })

        expect(response.status).toBe(400)
      } catch (error: any) {
        const bug = createBugReport(
          'send empty chat message',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })
})
