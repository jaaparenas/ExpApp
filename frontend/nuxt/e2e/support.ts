import { expect, type Page } from '@playwright/test'

export const USERNAME = process.env.E2E_USERNAME || 'admin'
export const PASSWORD = process.env.E2E_PASSWORD || 'admin12345'

export async function login(page: Page) {
  await page.goto('/')
  await page.locator('input[autocomplete="username"]').fill(USERNAME)
  await page.locator('input[autocomplete="current-password"]').fill(PASSWORD)
  await page.locator('button[type="submit"]').click()
  await expect(page).toHaveURL(/\/escritorio$/)
}
