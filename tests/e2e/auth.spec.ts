/**
 * Tests E2E pour l'authentification
 */

import { test, expect } from '@playwright/test'
import { TEST_CREDENTIALS } from '../utils/test-helpers'

const baseURL = process.env.TEST_URL || 'http://localhost:3000'

test.describe('Authentication E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Aller sur la page de login avant chaque test
    await page.goto(`${baseURL}/login`)
  })

  test('should display login page correctly', async ({ page }) => {
    await expect(page.locator('text=Connexion')).toBeVisible()
    await expect(page.locator('input[type="email"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('button:has-text("Se connecter")')).toBeVisible()
  })

  test('should login successfully with valid credentials', async ({ page }) => {
    // Remplir le formulaire
    await page.fill('input[type="email"]', TEST_CREDENTIALS.admin.email)
    await page.fill('input[type="password"]', TEST_CREDENTIALS.admin.password)
    
    // Soumettre
    await page.click('button:has-text("Se connecter")')
    
    // Attendre la redirection vers le dashboard
    await page.waitForURL(`${baseURL}/dashboard`, { timeout: 10000 })
    
    // Vérifier qu'on est sur le dashboard
    expect(page.url()).toContain('/dashboard')
  })

  test('should show error with invalid credentials', async ({ page }) => {
    // Remplir avec de mauvais identifiants
    await page.fill('input[type="email"]', 'wrong@email.com')
    await page.fill('input[type="password"]', 'wrongpassword')
    
    // Soumettre
    await page.click('button:has-text("Se connecter")')
    
    // Attendre le message d'erreur
    await expect(page.locator('text=/erreur|incorrect/i')).toBeVisible({ timeout: 5000 })
    
    // Vérifier qu'on reste sur la page de login
    expect(page.url()).toContain('/login')
  })

  test('should redirect to login when not authenticated', async ({ page }) => {
    // Essayer d'accéder au dashboard sans être connecté
    await page.goto(`${baseURL}/dashboard`)
    
    // Devrait rediriger vers login
    await page.waitForURL(`${baseURL}/login`, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })

  test('should navigate to register page', async ({ page }) => {
    // Cliquer sur le lien d'inscription
    await page.click('text=/inscrire|register/i')
    
    // Vérifier qu'on est sur la page d'inscription
    await page.waitForURL(`${baseURL}/register`, { timeout: 5000 })
    expect(page.url()).toContain('/register')
  })

  test('should register a new user', async ({ page }) => {
    // Aller sur la page d'inscription
    await page.goto(`${baseURL}/register`)
    
    const testEmail = `test-${Date.now()}@test.local`
    
    // Remplir le formulaire
    await page.fill('input[type="email"]', testEmail)
    await page.fill('input[type="password"]', 'TestPassword123!')
    
    // Soumettre
    await page.click('button:has-text(/inscrire|register/i)')
    
    // Attendre la redirection vers le dashboard
    await page.waitForURL(`${baseURL}/dashboard`, { timeout: 10000 })
    
    // Vérifier qu'on est connecté
    expect(page.url()).toContain('/dashboard')
  })
})
