import { test, expect } from '@playwright/test'

test('reset password page rejects a missing token', async ({ page }) => {
  await page.goto('/reset-password')
  await expect(page.getByRole('alert')).toContainText(
    /El enlace no es válido|The link is invalid/
  )
})

test('reset password page rejects an invalid token', async ({ page }) => {
  await page.goto('/reset-password?token=token-invalido')
  await expect(page.getByRole('alert')).toContainText(
    /El enlace no es válido|The link is invalid/
  )
})
