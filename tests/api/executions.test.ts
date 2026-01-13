/**
 * Tests API pour les exécutions
 */

import { describe, it, expect, beforeAll } from 'vitest'
import { getBaseURL, TEST_CREDENTIALS, authenticatedRequest } from '../utils/test-helpers'
import { checkDbConnection, seedTestData } from '../utils/test-db'
import { createBugReport } from '../utils/test-reports'

const baseURL = getBaseURL()

describe('Executions API', () => {
  let bugs: any[] = []
  let procedureId: number | null = null
  let executionId: number | null = null

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
          title: 'Test Procedure for Execution',
          description: 'Procedure for testing executions',
          category: 'Test',
          steps: [
            {
              order: 1,
              title: 'Step 1',
              description: 'First step',
              validationType: 'manual',
            },
            {
              order: 2,
              title: 'Step 2',
              description: 'Second step',
              validationType: 'manual',
            },
          ],
        }),
      }, TEST_CREDENTIALS.admin)
      
      const createData = await createResponse.json()
      procedureId = createData.id
    } catch (error) {
      console.error('Failed to create test procedure:', error)
    }
  })

  describe('POST /api/executions', () => {
    it('should start execution successfully', async () => {
      if (!procedureId) {
        throw new Error('No procedure available for testing')
      }

      try {
        const response = await authenticatedRequest('/executions', {
          method: 'POST',
          body: JSON.stringify({
            procedureId,
          }),
        }, TEST_CREDENTIALS.technician)

        expect(response.status).toBe(201)
        const data = await response.json()
        expect(data).toHaveProperty('id')
        expect(data).toHaveProperty('status')
        expect(data.status).toBe('in_progress')
        executionId = data.id
      } catch (error: any) {
        const bug = createBugReport(
          'start execution',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should return 404 for non-existent procedure', async () => {
      try {
        const response = await authenticatedRequest('/executions', {
          method: 'POST',
          body: JSON.stringify({
            procedureId: 99999,
          }),
        }, TEST_CREDENTIALS.technician)

        expect(response.status).toBe(404)
      } catch (error: any) {
        const bug = createBugReport(
          'start execution with invalid procedure',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('GET /api/executions', () => {
    it('should return list of executions', async () => {
      try {
        const response = await authenticatedRequest('/executions', {
          method: 'GET',
        })

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(Array.isArray(data)).toBe(true)
      } catch (error: any) {
        const bug = createBugReport(
          'get executions list',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('GET /api/executions/[id]', () => {
    it('should return execution details', async () => {
      if (!executionId) {
        // Créer une exécution d'abord
        if (!procedureId) return
        const createResponse = await authenticatedRequest('/executions', {
          method: 'POST',
          body: JSON.stringify({ procedureId }),
        }, TEST_CREDENTIALS.technician)
        const createData = await createResponse.json()
        executionId = createData.id
      }

      try {
        const response = await authenticatedRequest(`/executions/${executionId}`, {
          method: 'GET',
        })

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(data).toHaveProperty('id')
        expect(data).toHaveProperty('status')
        expect(data).toHaveProperty('procedure')
      } catch (error: any) {
        const bug = createBugReport(
          'get execution details',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('PUT /api/executions/[id]/step', () => {
    it('should update execution step', async () => {
      if (!executionId) return

      try {
        const response = await authenticatedRequest(`/executions/${executionId}/step`, {
          method: 'PUT',
          body: JSON.stringify({
            stepId: 1,
            status: 'completed',
            comments: 'Step completed successfully',
          }),
        }, TEST_CREDENTIALS.technician)

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(data).toHaveProperty('success')
      } catch (error: any) {
        const bug = createBugReport(
          'update execution step',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('POST /api/executions/[id]/complete', () => {
    it('should complete execution', async () => {
      if (!executionId) return

      try {
        const response = await authenticatedRequest(`/executions/${executionId}/complete`, {
          method: 'POST',
        }, TEST_CREDENTIALS.technician)

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(data).toHaveProperty('success')
      } catch (error: any) {
        const bug = createBugReport(
          'complete execution',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })
})
