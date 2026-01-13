/**
 * Tests API pour l'authentification
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import { getBaseURL, TEST_CREDENTIALS, authenticatedRequest } from '../utils/test-helpers'
import { checkDbConnection, seedTestData, cleanupTestDb } from '../utils/test-db'
import { createBugReport } from '../utils/test-reports'

const baseURL = getBaseURL()

describe('Authentication API', () => {
  let bugs: any[] = []

  beforeAll(async () => {
    // Vérifier la connexion à la base de données
    const dbConnected = await checkDbConnection()
    if (!dbConnected) {
      throw new Error('Database connection failed')
    }
    
    // Préparer les données de test
    await seedTestData()
  })

  afterAll(async () => {
    // Nettoyer après les tests si nécessaire
    // await cleanupTestDb()
  })

  describe('POST /api/auth/login', () => {
    it('should login successfully with valid credentials', async () => {
      try {
        const response = await fetch(`${baseURL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: TEST_CREDENTIALS.admin.email,
            password: TEST_CREDENTIALS.admin.password,
          }),
        })

        expect(response.status).toBe(200)
        
        const data = await response.json()
        expect(data).toHaveProperty('user')
        expect(data.user).toHaveProperty('id')
        expect(data.user).toHaveProperty('email')
        expect(data.user).toHaveProperty('role')
        expect(data.user.email).toBe(TEST_CREDENTIALS.admin.email)
        expect(data.user.role).toBe('admin')

        // Vérifier que le cookie est défini
        const setCookie = response.headers.get('set-cookie')
        expect(setCookie).toBeTruthy()
        expect(setCookie).toContain('auth-token')
      } catch (error: any) {
        const bug = createBugReport(
          'login with valid credentials',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should fail with invalid email', async () => {
      try {
        const response = await fetch(`${baseURL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: 'nonexistent@test.local',
            password: 'password123',
          }),
        })

        expect(response.status).toBe(401)
        const data = await response.json()
        expect(data).toHaveProperty('error')
      } catch (error: any) {
        const bug = createBugReport(
          'login with invalid email',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should fail with invalid password', async () => {
      try {
        const response = await fetch(`${baseURL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: TEST_CREDENTIALS.admin.email,
            password: 'wrongpassword',
          }),
        })

        expect(response.status).toBe(401)
        const data = await response.json()
        expect(data).toHaveProperty('error')
      } catch (error: any) {
        const bug = createBugReport(
          'login with invalid password',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should fail with missing email', async () => {
      try {
        const response = await fetch(`${baseURL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            password: 'password123',
          }),
        })

        expect(response.status).toBe(400)
        const data = await response.json()
        expect(data).toHaveProperty('error')
      } catch (error: any) {
        const bug = createBugReport(
          'login with missing email',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should normalize email to lowercase', async () => {
      try {
        const response = await fetch(`${baseURL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: TEST_CREDENTIALS.admin.email.toUpperCase(),
            password: TEST_CREDENTIALS.admin.password,
          }),
        })

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(data.user.email).toBe(TEST_CREDENTIALS.admin.email.toLowerCase())
      } catch (error: any) {
        const bug = createBugReport(
          'login with uppercase email normalization',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('POST /api/auth/register', () => {
    it('should register a new user successfully', async () => {
      try {
        const testEmail = `test-${Date.now()}@test.local`
        const response = await fetch(`${baseURL}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: testEmail,
            password: 'TestPassword123!',
            role: 'technician',
          }),
        })

        expect(response.status).toBe(201)
        const data = await response.json()
        expect(data).toHaveProperty('user')
        expect(data.user.email).toBe(testEmail.toLowerCase())
        expect(data.user.role).toBe('technician')

        // Vérifier que le cookie est défini
        const setCookie = response.headers.get('set-cookie')
        expect(setCookie).toBeTruthy()
        expect(setCookie).toContain('auth-token')
      } catch (error: any) {
        const bug = createBugReport(
          'register new user',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should fail with duplicate email', async () => {
      try {
        const response = await fetch(`${baseURL}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: TEST_CREDENTIALS.admin.email,
            password: 'Password123!',
          }),
        })

        expect(response.status).toBe(400)
        const data = await response.json()
        expect(data).toHaveProperty('error')
      } catch (error: any) {
        const bug = createBugReport(
          'register with duplicate email',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should fail with invalid email format', async () => {
      try {
        const response = await fetch(`${baseURL}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: 'invalid-email',
            password: 'Password123!',
          }),
        })

        // Peut retourner 400 ou 500 selon la validation
        expect([400, 500]).toContain(response.status)
      } catch (error: any) {
        const bug = createBugReport(
          'register with invalid email format',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('GET /api/auth/me', () => {
    it('should return current user when authenticated', async () => {
      try {
        const response = await authenticatedRequest('/auth/me', {
          method: 'GET',
        })

        expect(response.status).toBe(200)
        const data = await response.json()
        expect(data).toHaveProperty('user')
        expect(data.user).toHaveProperty('id')
        expect(data.user).toHaveProperty('email')
        expect(data.user).toHaveProperty('role')
      } catch (error: any) {
        const bug = createBugReport(
          'get current user when authenticated',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })

    it('should return 401 when not authenticated', async () => {
      try {
        const response = await fetch(`${baseURL}/api/auth/me`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        })

        expect(response.status).toBe(401)
        const data = await response.json()
        expect(data).toHaveProperty('error')
      } catch (error: any) {
        const bug = createBugReport(
          'get current user when not authenticated',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })

  describe('POST /api/auth/logout', () => {
    it('should logout successfully', async () => {
      try {
        // D'abord se connecter
        const loginResponse = await fetch(`${baseURL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: TEST_CREDENTIALS.admin.email,
            password: TEST_CREDENTIALS.admin.password,
          }),
        })

        const cookies = loginResponse.headers.get('set-cookie')
        
        // Ensuite se déconnecter
        const logoutResponse = await fetch(`${baseURL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(cookies ? { Cookie: cookies } : {}),
          },
        })

        expect(logoutResponse.status).toBe(200)
        const data = await logoutResponse.json()
        expect(data).toHaveProperty('success')
        expect(data.success).toBe(true)

        // Vérifier que le cookie est supprimé
        const setCookie = logoutResponse.headers.get('set-cookie')
        if (setCookie) {
          expect(setCookie).toContain('auth-token=;')
        }
      } catch (error: any) {
        const bug = createBugReport(
          'logout successfully',
          error.message,
          error.stack
        )
        bugs.push(bug)
        throw error
      }
    })
  })
})
