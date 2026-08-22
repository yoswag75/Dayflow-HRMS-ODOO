import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';
import { AuthProvider } from './auth';

function renderApp(path = '/') {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

const employees = [
  {
    id: 1,
    user_id: 1,
    name: 'Test HR',
    login_id: 'TEST-HR',
    email: 'hr@example.test',
    phone: '',
    department: 'People Operations',
    designation: 'HR Manager',
    manager: '',
    location: 'Remote',
    status: 'present',
    about: '',
    skills: [],
    joined_on: '2026-01-01',
  },
  {
    id: 2,
    user_id: 2,
    name: 'Test Employee',
    login_id: 'TEST-EMPLOYEE',
    email: 'employee@example.test',
    phone: '',
    department: 'Engineering',
    designation: 'Developer',
    manager: 'Test HR',
    location: 'Remote',
    status: 'present',
    about: '',
    skills: [],
    joined_on: '2026-01-01',
  },
];

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith('/auth/login')) {
      const credentials = JSON.parse(String(init?.body)) as { email: string };
      const isEmployee = credentials.email !== 'hr@example.test';
      const employee = employees[isEmployee ? 1 : 0];
      return json({
        access_token: 'test-access-token',
        user_id: employee.user_id,
        employee_id: employee.id,
        name: employee.name,
        login_id: credentials.email,
        role: isEmployee ? 'employee' : 'hr',
        must_change_password: credentials.email === 'first@example.test',
      });
    }
    if (url.endsWith('/employees/2')) return json(employees[1]);
    if (url.endsWith('/employees')) return json({ employees });
    return json({ detail: 'Test endpoint not configured.' }, 404);
  }));
});

async function signIn(email: string, password = 'TestPassword123!') {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText(/work email/i), email);
  await user.type(screen.getByLabelText(/^password$/i), password);
  await user.click(screen.getByRole('button', { name: /sign in/i }));
}

describe('Dayflow application', () => {
  it('shows the sign-in interface without seeded credentials', () => {
    renderApp('/login');
    expect(screen.getByRole('heading', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.queryByText(/demo access/i)).not.toBeInTheDocument();
  });

  it('redirects unauthenticated users to sign in', async () => {
    renderApp('/profile');
    expect(await screen.findByRole('heading', { name: /sign in/i })).toBeInTheDocument();
  });

  it('takes an employee to their profile after sign in', async () => {
    renderApp('/login');
    await signIn('employee@example.test');
    expect(await screen.findByRole('heading', { name: /my profile/i })).toBeInTheDocument();
    expect(await screen.findByRole('heading', { name: 'Test Employee' })).toBeInTheDocument();
  });

  it('takes HR to the employee directory after sign in', async () => {
    renderApp('/login');
    await signIn('hr@example.test');
    expect(await screen.findByRole('heading', { name: /employees/i })).toBeInTheDocument();
    expect((await screen.findAllByText('Test Employee')).length).toBeGreaterThan(0);
  });

  it('enforces first-login password change', async () => {
    renderApp('/login');
    await signIn('first@example.test');
    expect(await screen.findByRole('heading', { name: /choose a new password/i })).toBeInTheDocument();
  });
});
