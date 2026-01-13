/**
 * Tests de performance
 */

import { describe, it, expect, beforeAll } from 'vitest'
import { getBaseURL, TEST_CREDENTIALS, authenticatedRequest } from '../utils/test-helpers'
import { checkDbConnection, seedTestData } from '../utils/test-db'

const baseURL = getBaseURL()
const PERFORMANCE_THRESHOLD = 2000 // 2 secondes en millisecondes

describe('Performance Tests', () => {
  beforeAll(async () => {
    const dbConnected = await checkDbConnection()
    if (!dbConnected) {
      throw new Error('Database connection failed')
    }
    
    await seedTestData()
  })

  describe('API Response Times', () => {
    it('should respond to /api/auth/me within threshold', async () => {
      const startTime = Date.now()
      
      await authenticatedRequest('/auth/me', {
        method: 'GET',
      })

      const duration = Date.now() - startTime
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD)
    })

    it('should respond to /api/procedures within threshold', async () => {
      const startTime = Date.now()
      
      await authenticatedRequest('/procedures', {
        method: 'GET',
      })

      const duration = Date.now() - startTime
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD)
    })

    it('should respond to /api/tips within threshold', async () => {
      const startTime = Date.now()
      
      await authenticatedRequest('/tips', {
        method: 'GET',
      })

      const duration = Date.now() - startTime
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD)
    })
  })
})
