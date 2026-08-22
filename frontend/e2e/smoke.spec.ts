import { expect, test } from '@playwright/test';

test('HR can sign in and open the employee directory', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel(/login id/i).fill('HRDEMO001');
  await page.getByLabel(/^password$/i).fill('Dayflow123!');
  await page.getByRole('button', { name: /sign in/i }).click();

  await expect(page.getByRole('heading', { name: 'Employees' })).toBeVisible();
  await expect(page.getByText('Ava Rao').first()).toBeVisible();
});

test('employee navigation is role-specific', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel(/login id/i).fill('EMPDEMO001');
  await page.getByLabel(/^password$/i).fill('Dayflow123!');
  await page.getByRole('button', { name: /sign in/i }).click();

  await expect(page.getByRole('heading', { name: 'My profile' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Employees' })).toHaveCount(0);
  await expect(page.getByRole('link', { name: 'Attendance' })).toBeVisible();
});
