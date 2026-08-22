import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
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

async function signIn(employeeId: string, password = 'Dayflow123!') {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText(/login id/i), employeeId);
  await user.type(screen.getByLabelText(/^password$/i), password);
  await user.click(screen.getByRole('button', { name: /sign in/i }));
}

describe('Dayflow application', () => {
  it('shows the demo sign-in interface', () => {
    renderApp('/login');
    expect(screen.getByRole('heading', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByText(/HR: HRDEMO001/i)).toBeInTheDocument();
    expect(screen.getByText(/Employee: EMPDEMO001/i)).toBeInTheDocument();
  });

  it('redirects unauthenticated users to sign in', async () => {
    renderApp('/profile');
    expect(await screen.findByRole('heading', { name: /sign in/i })).toBeInTheDocument();
  });

  it('takes an employee to their profile after sign in', async () => {
    renderApp('/login');
    await signIn('EMPDEMO001');
    expect(await screen.findByRole('heading', { name: /my profile/i })).toBeInTheDocument();
    expect(await screen.findByRole('heading', { name: 'Ava Rao' })).toBeInTheDocument();
  });

  it('takes HR to the employee directory after sign in', async () => {
    renderApp('/login');
    await signIn('HRDEMO001');
    expect(await screen.findByRole('heading', { name: /employees/i })).toBeInTheDocument();
    expect((await screen.findAllByText('Dev Shah')).length).toBeGreaterThan(0);
  });

  it('enforces first-login password change', async () => {
    renderApp('/login');
    await signIn('NEWEMP001');
    expect(await screen.findByRole('heading', { name: /choose a new password/i })).toBeInTheDocument();
  });
});
