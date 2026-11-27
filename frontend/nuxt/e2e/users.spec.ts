import { test, expect } from '@playwright/test'
import { login, USERNAME } from './support'

test('admin can list users', async ({ page }) => {
  await login(page)
  await page.goto('/comun/usuario/usuarios')

  await expect(page.getByRole('heading', { name: /Usuarios|Users/ })).toBeVisible()
  await expect(page.getByRole('cell', { name: USERNAME, exact: true })).toBeVisible()
})

test('search filters the user table', async ({ page }) => {
  await login(page)
  await page.goto('/comun/usuario/usuarios')

  await page.getByRole('searchbox').fill('no-existe')
  await expect(page.getByText(/No hay usuarios para mostrar|No users to display/))
    .toBeVisible({ timeout: 10_000 })
})
