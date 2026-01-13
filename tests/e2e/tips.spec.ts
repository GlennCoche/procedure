/**
 * Tests E2E pour les tips
 */

import { test, expect } from '@playwright/test'
import { TEST_CREDENTIALS } from '../utils/test-helpers'

const baseURL = process.env.TEST_URL || 'http://localhost:3000'

test.describe('Tips E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Se connecter
    await page.goto(`${baseURL}/login`)
    await page.fill('input[type="email"]', TEST_CREDENTIALS.admin.email)
    await page.fill('input[type="password"]', TEST_CREDENTIALS.admin.password)
    await page.click('button:has-text("Se connecter")')
    await page.waitForURL(`${baseURL}/dashboard`, { timeout: 10000 })
  })

  test('should display tips list', async ({ page }) => {
    await page.goto(`${baseURL}/tips`)
    
    // Vérifier que la page se charge
    await expect(page.locator('h1, h2')).toContainText(/tip|astuce/i)
  })

  test('should search tips', async ({ page }) => {
    await page.goto(`${baseURL}/tips`)
    
    // Attendre que la page se charge
    await page.waitForSelector('input', { timeout: 5000 })
    
    // Chercher un champ de recherche
    const searchInput = page.locator('input[type="search"], input[placeholder*="search"], input[placeholder*="recherche"]')
    if (await searchInput.count() > 0) {
      await searchInput.fill('maintenance')
      await page.waitForTimeout(1000) // Attendre les résultats
    }
  })
})
