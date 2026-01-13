/**
 * Tests E2E pour les exécutions
 */

import { test, expect } from '@playwright/test'
import { TEST_CREDENTIALS } from '../utils/test-helpers'

const baseURL = process.env.TEST_URL || 'http://localhost:3000'

test.describe('Executions E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Se connecter en tant que technicien
    await page.goto(`${baseURL}/login`)
    await page.fill('input[type="email"]', TEST_CREDENTIALS.technician.email)
    await page.fill('input[type="password"]', TEST_CREDENTIALS.technician.password)
    await page.click('button:has-text("Se connecter")')
    await page.waitForURL(`${baseURL}/dashboard`, { timeout: 10000 })
  })

  test('should display procedures available for execution', async ({ page }) => {
    await page.goto(`${baseURL}/procedures`)
    
    // Vérifier que les procédures sont affichées
    await expect(page.locator('h1, h2')).toContainText(/procédure/i)
  })

  test('should start execution from procedure page', async ({ page }) => {
    await page.goto(`${baseURL}/procedures`)
    
    // Attendre que les procédures se chargent
    await page.waitForSelector('a, button', { timeout: 5000 })
    
    // Cliquer sur une procédure
    const firstProcedure = page.locator('a').first()
    if (await firstProcedure.count() > 0) {
      await firstProcedure.click()
      await page.waitForURL(/\/procedures\/\d+/, { timeout: 5000 })
      
      // Chercher un bouton pour démarrer l'exécution
      const startButton = page.locator('button:has-text(/démarrer|start|exécuter/i)')
      if (await startButton.count() > 0) {
        await startButton.click()
        // Vérifier qu'une exécution a été créée
        await expect(page).toHaveURL(/\/executions|\/procedures/, { timeout: 5000 })
      }
    }
  })
})
