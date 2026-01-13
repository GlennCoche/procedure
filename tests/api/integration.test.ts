/**
 * Tests d'intégration avec scénarios complets
 */

import { describe, it, expect, beforeAll } from 'vitest'
import { getBaseURL, TEST_CREDENTIALS, authenticatedRequest } from '../utils/test-helpers'
import { checkDbConnection, seedTestData } from '../utils/test-db'
import { createBugReport } from '../utils/test-reports'

const baseURL = getBaseURL()

describe('Integration Tests - Complete Scenarios', () => {
  let bugs: any[] = []
  let procedureId: number | null = null
  let executionId: number | null = null

  beforeAll(async () => {
    const dbConnected = await checkDbConnection()
    if (!dbConnected) {
      throw new Error('Database connection failed')
    }
    
    await seedTestData()
  })

  describe('Scenario 1: Admin creates procedure → Technician executes → Completion', () => {
    it('should complete full workflow', async () => {
      try {
        // Étape 1: Admin crée une procédure
        const createProcedureResponse = await authenticatedRequest('/procedures', {
          method: 'POST',
          body: JSON.stringify({
            title: 'Integration Test Procedure',
            description: 'Procedure for integration testing',
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

        expect(createProcedureResponse.status).toBe(201)
        const procedureData = await createProcedureResponse.json()
        procedureId = procedureData.id

        // Étape 2: Technicien démarre l'exécution
        const startExecutionResponse = await authenticatedRequest('/executions', {
          method: 'POST',
          body: JSON.stringify({
            procedureId,
          }),
        }, TEST_CREDENTIALS.technician)

        expect(startExecutionResponse.status).toBe(201)
        const executionData = await startExecutionResponse.json()
        executionId = executionData.id

        // Étape 3: Technicien complète les étapes
        const updateStepResponse = await authenticatedRequest(`/executions/${executionId}/step`, {
          method: 'PUT',
          body: JSON.stringify({
            stepId: 1,
            status: 'completed',
            comments: 'Step 1 completed',
          }),
        }, TEST_CREDENTIALS.technician)

        expect(updateStepResponse.status).toBe(200)

        // Étape 4: Technicien finalise l'exécution
        const completeResponse = await authenticatedRequest(`/executions/${executionId}/complete`, {
          method: 'POST',
        }, TEST_CREDENTIALS.technician)

        expect(completeResponse.status).toBe(200)
      } catch (error: any) {
        const bug = createBugReport(
          'complete workflow scenario',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('Scenario 2: Chat IA during execution', () => {
    it('should use chat IA during execution workflow', async () => {
      if (!process.env.OPENAI_API_KEY) {
        return // Skip si OpenAI n'est pas configuré
      }

      if (!procedureId) {
        // Créer une procédure d'abord
        const createResponse = await authenticatedRequest('/procedures', {
          method: 'POST',
          body: JSON.stringify({
            title: 'Chat Test Procedure',
            description: 'Procedure for chat testing',
            category: 'Test',
            steps: [{ order: 1, title: 'Step 1', validationType: 'manual' }],
          }),
        }, TEST_CREDENTIALS.admin)
        const createData = await createResponse.json()
        procedureId = createData.id
      }

      try {
        // Démarrer une exécution
        const execResponse = await authenticatedRequest('/executions', {
          method: 'POST',
          body: JSON.stringify({ procedureId }),
        }, TEST_CREDENTIALS.technician)
        const execData = await execResponse.json()
        const execId = execData.id

        // Utiliser le chat avec contexte de l'exécution
        const chatResponse = await authenticatedRequest('/chat', {
          method: 'POST',
          body: JSON.stringify({
            message: 'Comment compléter cette étape?',
            context: { execution_id: execId, procedure_id: procedureId },
          }),
        }, TEST_CREDENTIALS.technician)

        expect(chatResponse.status).toBe(200)
      } catch (error: any) {
        const bug = createBugReport(
          'chat IA during execution',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })
})
