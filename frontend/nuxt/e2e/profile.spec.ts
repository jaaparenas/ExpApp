import { test, expect } from '@playwright/test'
import { login, PASSWORD } from './support'

test('profile shows account data and validates password confirmation', async ({ page }) => {
  await login(page)
  await page.goto('/comun/usuario/perfil')

  await expect(page.getByRole('heading', { name: /Perfil|Profile/ })).toBeVisible()
  await expect(page.getByText('admin@local.com')).toBeVisible()

  await page.locator('input[autocomplete="current-password"]').fill(PASSWORD)
  await page.locator('input[autocomplete="new-password"]').first().fill('nuevaClave123')
  await page.locator('input[autocomplete="new-password"]').nth(1).fill('otraClave123')
  await page.getByRole('button', { name: /Guardar|Save/ }).click()

  await expect(page.getByRole('alert')).toContainText(
    /Las contraseñas no coinciden|Passwords do not match/
  )
})
