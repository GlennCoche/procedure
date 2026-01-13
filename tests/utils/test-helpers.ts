/**
 * Helpers pour les tests
 */

export interface TestUser {
  email: string
  password: string
  role: 'admin' | 'technician'
}

export interface TestCredentials {
  admin: TestUser
  technician: TestUser
}

/**
 * Credentials de test par défaut
 */
export const TEST_CREDENTIALS: TestCredentials = {
  admin: {
    email: 'admin@procedures.local',
    password: 'AdminSecure123!',
    role: 'admin',
  },
  technician: {
    email: 'technician@procedures.local',
    password: 'Technician123!',
    role: 'technician',
  },
}

/**
 * URL de base pour les tests
 */
export const getBaseURL = (): string => {
  return process.env.TEST_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'
}

/**
 * Helper pour faire des requêtes API avec authentification
 */
export async function authenticatedRequest(
  endpoint: string,
  options: RequestInit = {},
  user: TestUser = TEST_CREDENTIALS.admin
): Promise<Response> {
  const baseURL = getBaseURL()
  
  // D'abord, se connecter pour obtenir le cookie
  const loginResponse = await fetch(`${baseURL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: user.email,
      password: user.password,
    }),
    credentials: 'include',
  })

  if (!loginResponse.ok) {
    throw new Error(`Login failed: ${loginResponse.statusText}`)
  }

  // Extraire les cookies de la réponse
  const cookies = loginResponse.headers.get('set-cookie')
  
  // Faire la requête avec les cookies
  return fetch(`${baseURL}/api${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(cookies ? { Cookie: cookies } : {}),
      ...options.headers,
    },
    credentials: 'include',
  })
}

/**
 * Helper pour créer un utilisateur de test
 */
export async function createTestUser(user: Partial<TestUser>): Promise<TestUser> {
  const baseURL = getBaseURL()
  
  const response = await fetch(`${baseURL}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: user.email || `test-${Date.now()}@test.local`,
      password: user.password || 'TestPassword123!',
      role: user.role || 'technician',
    }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(`Failed to create test user: ${error.error || response.statusText}`)
  }

  const data = await response.json()
  return {
    email: data.user.email,
    password: user.password || 'TestPassword123!',
    role: data.user.role,
  }
}

/**
 * Helper pour attendre un délai
 */
export const wait = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Helper pour formater les erreurs de test
 */
export function formatTestError(error: any): string {
  if (error instanceof Error) {
    return `${error.name}: ${error.message}\n${error.stack}`
  }
  return String(error)
}

/**
 * Helper pour valider la structure d'une réponse API
 */
export function validateApiResponse(data: any, requiredFields: string[]): void {
  for (const field of requiredFields) {
    if (!(field in data)) {
      throw new Error(`Missing required field: ${field}`)
    }
  }
}
