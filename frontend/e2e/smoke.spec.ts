import { expect, test, type Page } from '@playwright/test';

const employees = [
  {
    id: 1, user_id: 1, name: 'Test HR', login_id: 'TEST-HR',
    email: 'hr@example.test', department: 'People Operations', designation: 'HR Manager',
    phone: '', manager: '', location: 'Remote', status: 'present', about: '', skills: [], joined_on: '2026-01-01',
  },
  {
    id: 2, user_id: 2, name: 'Test Employee', login_id: 'TEST-EMPLOYEE',
    email: 'employee@example.test', department: 'Engineering', designation: 'Developer',
    phone: '', manager: 'Test HR', location: 'Remote', status: 'present', about: '', skills: [], joined_on: '2026-01-01',
  },
];

async function installApiStub(page: Page) {
  await page.route('http://localhost:8000/**', async (route) => {
    const url = route.request().url();
    let body: unknown;
    let status = 200;

    if (url.endsWith('/auth/login')) {
      const credentials = route.request().postDataJSON() as { email: string };
      const isEmployee = credentials.email === 'employee@example.test';
      const employee = employees[isEmployee ? 1 : 0];
      body = {
        access_token: 'test-access-token', user_id: employee.user_id, employee_id: employee.id,
        name: employee.name, login_id: employee.login_id, role: isEmployee ? 'employee' : 'hr',
        must_change_password: false,
      };
    } else if (url.endsWith('/employees/2')) {
      body = employees[1];
    } else if (url.endsWith('/employees')) {
      body = { employees };
    } else {
      status = 404;
      body = { detail: 'Test endpoint not configured.' };
    }

    await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) });
  });
}

test('HR can sign in and open the employee directory', async ({ page }) => {
  await installApiStub(page);
  await page.goto('/login');
  await page.getByLabel(/work email/i).fill('hr@example.test');
  await page.getByLabel(/^password$/i).fill('TestPassword123!');
  await page.getByRole('button', { name: /sign in/i }).click();

  await expect(page.getByRole('heading', { name: 'Employees' })).toBeVisible();
  await expect(page.getByText('Test Employee').filter({ visible: true }).first()).toBeVisible();
});

test('employee navigation is role-specific', async ({ page }) => {
  await installApiStub(page);
  await page.goto('/login');
  await page.getByLabel(/work email/i).fill('employee@example.test');
  await page.getByLabel(/^password$/i).fill('TestPassword123!');
  await page.getByRole('button', { name: /sign in/i }).click();

  await expect(page.getByRole('heading', { name: 'My profile' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Employees' })).toHaveCount(0);
  await expect(page.getByRole('link', { name: 'Attendance' })).toBeVisible();
});
