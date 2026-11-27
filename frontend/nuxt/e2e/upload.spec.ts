import { test, expect } from '@playwright/test'
import { login } from './support'

test('uploads a valid CSV file', async ({ page }) => {
  await login(page)
  await page.goto('/datos/subir')

  await page.locator('input[type="file"]').setInputFiles({
    name: 'datos.csv',
    mimeType: 'text/csv',
    buffer: Buffer.from('nombre,valor\nuno,1\ndos,2\n')
  })

  await page.getByRole('button', { name: /Subir archivo|Upload file/ }).click()

  await expect(page.getByText(/Archivo subido correctamente|File uploaded successfully/))
    .toBeVisible()
  await expect(page.getByText('datos.csv')).toBeVisible()
})

test('rejects a fake xlsx file', async ({ page }) => {
  await login(page)
  await page.goto('/datos/subir')

  await page.locator('input[type="file"]').setInputFiles({
    name: 'falso.xlsx',
    mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    buffer: Buffer.from('esto no es un archivo zip')
  })

  await page.getByRole('button', { name: /Subir archivo|Upload file/ }).click()

  await expect(page.getByRole('alert')).toContainText(
    /No se pudo subir el archivo|The file could not be uploaded/
  )
})
