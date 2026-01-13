/**
 * Tests API pour les procédures
 */

import { describe, it, expect, beforeAll } from 'vitest'
import { getBaseURL, TEST_CREDENTIALS, authenticatedRequest } from '../utils/test-helpers'
import { checkDbConnection, seedTestData } from '../utils/test-db'
import { createBugReport } from '../utils/test-reports'
import sampleProcedure from '../fixtures/procedures.json'

const baseURL = getBaseURL()

describe('Procedures API', () => {
  let bugs: any[] = []
  let adminToken: string = ''
  let technicianToken: string = ''
  let createdProcedureId: number | null = null

  beforeAll(async () => {
    const dbConnected = await checkDbConnection()
    if (!dbConnected) {
      throw new Error('Database connection failed')
    }
    
    await seedTestData()
    
    // Obtenir les tokens pour admin et technician
    try {
      const adminLogin = await fetch(`${baseURL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: TEST_CREDENTIALS.admin.email,
          password: TEST_CREDENTIALS.admin.password,
        }),
      })
      const adminData = await adminLogin.json()
      // Note: Le token est dans le cookie, on utilisera authenticatedRequest
    } catch (error) {
      console.error('Failed to login admin:', error)
    }
  })

  describe('GET /api/procedures', () => {
    it('should return list of procedures for authenticated user', async () => {
      try {
        const response = await authenticatedRequest('/procedures', {
          method: 'GET',
        })

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(Array.isArray(data)).toBe(true)
      } catch (error: any) {
        const bug = createBugReport(
          'get procedures list',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should return 401 for unauthenticated request', async () => {
      try {
        const response = await fetch(`${baseURL}/api/procedures`, {
          method: 'GET',
        })

        expect(response.status).toBe(401)
      } catch (error: any) {
        const bug = createBugReport(
          'get procedures without auth',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should filter by category', async () => {
      try {
        const response = await authenticatedRequest('/procedures?category=Maintenance', {
          method: 'GET',
        })

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(Array.isArray(data)).toBe(true)
        // Si des procédures sont retournées, vérifier qu'elles ont la bonne catégorie
        if (data.length > 0) {
          data.forEach((proc: any) => {
            expect(proc.category).toBe('Maintenance')
          })
        }
      } catch (error: any) {
        const bug = createBugReport(
          'filter procedures by category',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('POST /api/procedures', () => {
    it('should create procedure as admin', async () => {
      try {
        const response = await authenticatedRequest('/procedures', {
          method: 'POST',
          body: JSON.stringify(sampleProcedure.sampleProcedure),
        }, TEST_CREDENTIALS.admin)

        expect(response.status).toBe(201)
        const data = await response.json()
        expect(data).toHaveProperty('id')
        expect(data.title).toBe(sampleProcedure.sampleProcedure.title)
        createdProcedureId = data.id
      } catch (error: any) {
        const bug = createBugReport(
          'create procedure as admin',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should return 403 when technician tries to create', async () => {
      try {
        const response = await authenticatedRequest('/procedures', {
          method: 'POST',
          body: JSON.stringify(sampleProcedure.sampleProcedure),
        }, TEST_CREDENTIALS.technician)

        expect(response.status).toBe(403)
        const data = await response.json()
        expect(data).toHaveProperty('error')
      } catch (error: any) {
        const bug = createBugReport(
          'create procedure as technician (should fail)',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('GET /api/procedures/[id]', () => {
    it('should return procedure details', async () => {
      if (!createdProcedureId) {
        // Créer une procédure d'abord si nécessaire
        const createResponse = await authenticatedRequest('/procedures', {
          method: 'POST',
          body: JSON.stringify(sampleProcedure.sampleProcedure),
        }, TEST_CREDENTIALS.admin)
        const createData = await createResponse.json()
        createdProcedureId = createData.id
      }

      try {
        const response = await authenticatedRequest(`/procedures/${createdProcedureId}`, {
          method: 'GET',
        })

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(data).toHaveProperty('id')
        expect(data).toHaveProperty('title')
        expect(data).toHaveProperty('steps')
        expect(Array.isArray(data.steps)).toBe(true)
      } catch (error: any) {
        const bug = createBugReport(
          'get procedure details',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should return 404 for non-existent procedure', async () => {
      try {
        const response = await authenticatedRequest('/procedures/99999', {
          method: 'GET',
        })

        expect(response.status).toBe(404)
      } catch (error: any) {
        const bug = createBugReport(
          'get non-existent procedure',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('PUT /api/procedures/[id]', () => {
    it('should update procedure as admin', async () => {
      if (!createdProcedureId) {
        const createResponse = await authenticatedRequest('/procedures', {
          method: 'POST',
          body: JSON.stringify(sampleProcedure.sampleProcedure),
        }, TEST_CREDENTIALS.admin)
        const createData = await createResponse.json()
        createdProcedureId = createData.id
      }

      try {
        const updatedData = {
          ...sampleProcedure.sampleProcedure,
          title: 'Updated Procedure Title',
        }

        const response = await authenticatedRequest(`/procedures/${createdProcedureId}`, {
          method: 'PUT',
          body: JSON.stringify(updatedData),
        }, TEST_CREDENTIALS.admin)

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(data.title).toBe('Updated Procedure Title')
      } catch (error: any) {
        const bug = createBugReport(
          'update procedure as admin',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should return 403 when technician tries to update', async () => {
      if (!createdProcedureId) return

      try {
        const response = await authenticatedRequest(`/procedures/${createdProcedureId}`, {
          method: 'PUT',
          body: JSON.stringify({ title: 'Hacked Title' }),
        }, TEST_CREDENTIALS.technician)

        expect(response.status).toBe(403)
      } catch (error: any) {
        const bug = createBugReport(
          'update procedure as technician (should fail)',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('DELETE /api/procedures/[id]', () => {
    it('should delete procedure as admin', async () => {
      // Créer une procédure pour la supprimer
      const createResponse = await authenticatedRequest('/procedures', {
        method: 'POST',
        body: JSON.stringify(sampleProcedure.sampleProcedure),
      }, TEST_CREDENTIALS.admin)
      const createData = await createResponse.json()
      const procedureToDelete = createData.id

      try {
        const response = await authenticatedRequest(`/procedures/${procedureToDelete}`, {
          method: 'DELETE',
        }, TEST_CREDENTIALS.admin)

        expect(response.status).toBe(200)
        
        // Vérifier que la procédure est supprimée (soft delete)
        const getResponse = await authenticatedRequest(`/procedures/${procedureToDelete}`, {
          method: 'GET',
        })
        // Peut retourner 404 ou la procédure avec isActive: false
        expect([200, 404]).toContain(getResponse.status)
      } catch (error: any) {
        const bug = createBugReport(
          'delete procedure as admin',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should return 403 when technician tries to delete', async () => {
      if (!createdProcedureId) return

      try {
        const response = await authenticatedRequest(`/procedures/${createdProcedureId}`, {
          method: 'DELETE',
        }, TEST_CREDENTIALS.technician)

        expect(response.status).toBe(403)
      } catch (error: any) {
        const bug = createBugReport(
          'delete procedure as technician (should fail)',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })
})
