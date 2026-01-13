/**
 * Tests API pour les tips
 */

import { describe, it, expect, beforeAll } from 'vitest'
import { getBaseURL, TEST_CREDENTIALS, authenticatedRequest } from '../utils/test-helpers'
import { checkDbConnection, seedTestData } from '../utils/test-db'
import { createBugReport } from '../utils/test-reports'

const baseURL = getBaseURL()

describe('Tips API', () => {
  let bugs: any[] = []
  let createdTipId: number | null = null

  beforeAll(async () => {
    const dbConnected = await checkDbConnection()
    if (!dbConnected) {
      throw new Error('Database connection failed')
    }
    
    await seedTestData()
  })

  describe('GET /api/tips', () => {
    it('should return list of tips', async () => {
      try {
        const response = await authenticatedRequest('/tips', {
          method: 'GET',
        })

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(Array.isArray(data)).toBe(true)
      } catch (error: any) {
        const bug = createBugReport(
          'get tips list',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should search tips by query', async () => {
      try {
        const response = await authenticatedRequest('/tips?search=maintenance', {
          method: 'GET',
        })

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(Array.isArray(data)).toBe(true)
      } catch (error: any) {
        const bug = createBugReport(
          'search tips',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should filter tips by category', async () => {
      try {
        const response = await authenticatedRequest('/tips?category=Maintenance', {
          method: 'GET',
        })

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(Array.isArray(data)).toBe(true)
      } catch (error: any) {
        const bug = createBugReport(
          'filter tips by category',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('POST /api/tips', () => {
    it('should create tip as admin', async () => {
      try {
        const tipData = {
          title: 'Test Tip',
          content: 'This is a test tip content',
          category: 'Test',
          tags: ['test', 'tip'],
        }

        const response = await authenticatedRequest('/tips', {
          method: 'POST',
          body: JSON.stringify(tipData),
        }, TEST_CREDENTIALS.admin)

        expect(response.status).toBe(201)
        const data = await response.json()
        expect(data).toHaveProperty('id')
        expect(data.title).toBe(tipData.title)
        createdTipId = data.id
      } catch (error: any) {
        const bug = createBugReport(
          'create tip as admin',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should return 403 when technician tries to create', async () => {
      try {
        const response = await authenticatedRequest('/tips', {
          method: 'POST',
          body: JSON.stringify({
            title: 'Test Tip',
            content: 'Content',
          }),
        }, TEST_CREDENTIALS.technician)

        expect(response.status).toBe(403)
      } catch (error: any) {
        const bug = createBugReport(
          'create tip as technician (should fail)',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('GET /api/tips/[id]', () => {
    it('should return tip details', async () => {
      if (!createdTipId) {
        // Créer un tip d'abord
        const createResponse = await authenticatedRequest('/tips', {
          method: 'POST',
          body: JSON.stringify({
            title: 'Test Tip',
            content: 'Content',
          }),
        }, TEST_CREDENTIALS.admin)
        const createData = await createResponse.json()
        createdTipId = createData.id
      }

      try {
        const response = await authenticatedRequest(`/tips/${createdTipId}`, {
          method: 'GET',
        })

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(data).toHaveProperty('id')
        expect(data).toHaveProperty('title')
        expect(data).toHaveProperty('content')
      } catch (error: any) {
        const bug = createBugReport(
          'get tip details',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('PUT /api/tips/[id]', () => {
    it('should update tip as admin', async () => {
      if (!createdTipId) return

      try {
        const response = await authenticatedRequest(`/tips/${createdTipId}`, {
          method: 'PUT',
          body: JSON.stringify({
            title: 'Updated Tip Title',
            content: 'Updated content',
          }),
        }, TEST_CREDENTIALS.admin)

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(data.title).toBe('Updated Tip Title')
      } catch (error: any) {
        const bug = createBugReport(
          'update tip as admin',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('DELETE /api/tips/[id]', () => {
    it('should delete tip as admin', async () => {
      // Créer un tip pour le supprimer
      const createResponse = await authenticatedRequest('/tips', {
        method: 'POST',
        body: JSON.stringify({
          title: 'Tip to Delete',
          content: 'Content',
        }),
      }, TEST_CREDENTIALS.admin)
      const createData = await createResponse.json()
      const tipToDelete = createData.id

      try {
        const response = await authenticatedRequest(`/tips/${tipToDelete}`, {
          method: 'DELETE',
        }, TEST_CREDENTIALS.admin)

        expect(response.status).toBe(200)
      } catch (error: any) {
        const bug = createBugReport(
          'delete tip as admin',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })
})
