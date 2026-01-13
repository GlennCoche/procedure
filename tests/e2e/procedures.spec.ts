/**
 * Tests E2E pour les procédures
 */

import { test, expect } from '@playwright/test'
import { TEST_CREDENTIALS } from '../utils/test-helpers'

const baseURL = process.env.TEST_URL || 'http://localhost:3000'

test.describe('Procedures E2E', () => {
  test.beforeEach(async ({ page, context }) => {
    // Se connecter en tant qu'admin
    await page.goto(`${baseURL}/login`)
    await page.fill('input[type="email"]', TEST_CREDENTIALS.admin.email)
    await page.fill('input[type="password"]', TEST_CREDENTIALS.admin.password)
    await page.click('button:has-text("Se connecter")')
    await page.waitForURL(`${baseURL}/dashboard`, { timeout: 10000 })
  })

  test('should display procedures list', async ({ page }) => {
    await page.goto(`${baseURL}/procedures`)
    
    // Vérifier que la page se charge
    await expect(page.locator('h1, h2')).toContainText(/procédure/i)
  })

  test('should navigate to procedure details', async ({ page }) => {
    await page.goto(`${baseURL}/procedures`)
    
    // Attendre que les procédures se chargent
    await page.waitForSelector('a, button', { timeout: 5000 })
    
    // Cliquer sur la première procédure (si disponible)
    const firstProcedure = page.locator('a').first()
    if (await firstProcedure.count() > 0) {
      await firstProcedure.click()
      // Vérifier qu'on est sur la page de détails
      await expect(page).toHaveURL(/\/procedures\/\d+/, { timeout: 5000 })
    }
  })

  test('should access admin procedures page', async ({ page }) => {
    await page.goto(`${baseURL}/admin/procedures`)
    
    // Vérifier que la page admin se charge
    await expect(page.locator('h1, h2')).toContainText(/procédure|admin/i)
  })
})
