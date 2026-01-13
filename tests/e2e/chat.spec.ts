/**
 * Tests E2E pour le chat IA
 */

import { test, expect } from '@playwright/test'
import { TEST_CREDENTIALS } from '../utils/test-helpers'

const baseURL = process.env.TEST_URL || 'http://localhost:3000'

test.describe('Chat IA E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Se connecter
    await page.goto(`${baseURL}/login`)
    await page.fill('input[type="email"]', TEST_CREDENTIALS.admin.email)
    await page.fill('input[type="password"]', TEST_CREDENTIALS.admin.password)
    await page.click('button:has-text("Se connecter")')
    await page.waitForURL(`${baseURL}/dashboard`, { timeout: 10000 })
  })

  test('should display chat interface', async ({ page }) => {
    await page.goto(`${baseURL}/chat`)
    
    // Vérifier que l'interface de chat se charge
    await expect(page.locator('input, textarea')).toBeVisible({ timeout: 5000 })
  })

  test('should send message in chat', async ({ page }) => {
    await page.goto(`${baseURL}/chat`)
    
    // Attendre que l'interface soit prête
    await page.waitForSelector('input, textarea', { timeout: 5000 })
    
    // Remplir et envoyer un message
    const input = page.locator('input, textarea').first()
    await input.fill('Bonjour, comment ça marche?')
    
    const sendButton = page.locator('button:has-text(/envoyer|send/i)')
    if (await sendButton.count() > 0) {
      await sendButton.click()
      // Attendre une réponse (peut prendre du temps)
      await page.waitForTimeout(3000)
    }
  })
})
