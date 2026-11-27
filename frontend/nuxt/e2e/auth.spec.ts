import { test, expect } from '@playwright/test'
import { login } from './support'

test('login, dashboard and logout', async ({ page }) => {
  await login(page)

  await expect(page.getByRole('heading', { name: /Escritorio|Dashboard/ })).toBeVisible()
  await expect(page.locator('.nav a[href="/datos/subir"]')).toBeVisible()

  await page.getByRole('button', { name: /Salir|Sign out/ }).click()
  await expect(page).toHaveURL(/\/$/)
  await expect(page.locator('input[autocomplete="username"]')).toBeVisible()
})

test('login rejects invalid credentials', async ({ page }) => {
  await page.goto('/')
  await page.locator('input[autocomplete="username"]').fill('admin')
  await page.locator('input[autocomplete="current-password"]').fill('incorrecta')
  await page.locator('button[type="submit"]').click()

  await expect(page.getByRole('alert')).toContainText(
    /Usuario o contraseña incorrectos|Invalid username or password/
  )
  await expect(page).toHaveURL(/\/$/)
})

test('protected route redirects to login', async ({ page }) => {
  await page.context().clearCookies()
  await page.goto('/comun/usuario/perfil')
  await expect(page).toHaveURL(/\/$/)
  await expect(page.locator('input[autocomplete="username"]')).toBeVisible()
})
