import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { roleLanding, useAuth } from './auth'
import { Shell } from './components/Shell'
import { AttendancePage } from './pages/AttendancePage'
import { ChangePasswordPage, ForbiddenPage, LoginPage, NotFoundPage, SetupPage } from './pages/AuthPages'
import { ChangeRequestsPage, EmployeeDetailPage, EmployeeFormPage, EmployeesPage } from './pages/EmployeesPage'
import { LeaveFormPage, LeavePage } from './pages/LeavePage'
import { PlaceholderPage } from './pages/PlaceholderPage'
import { ChatbotPage, NotificationsPage, OnboardingPage, RecognitionPage, SimulationPage } from './pages/ConnectedPages'
import { ProfileEditPage, ProfilePage } from './pages/ProfilePage'
import type { ReactNode } from 'react'

function Protected({ children }: { children: ReactNode }) {
  const { session } = useAuth()
  const location = useLocation()
  if (!session) return <Navigate to={`/login?returnTo=${encodeURIComponent(location.pathname + location.search)}`} replace />
  if (session.mustChangePassword) return <Navigate to="/change-password" replace />
  return children
}

function AdminOnly({ children }: { children: ReactNode }) {
  const { session } = useAuth()
  return session?.role === 'employee' ? <Navigate to="/forbidden" replace /> : children
}

function HomeRedirect() {
  const { session } = useAuth()
  return <Navigate to={session ? roleLanding(session) : '/login'} replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/setup" element={<SetupPage />} />
      <Route path="/change-password" element={<ChangePasswordPage />} />
      <Route path="/forbidden" element={<ForbiddenPage />} />
      <Route path="/not-found" element={<NotFoundPage />} />
      <Route path="/" element={<HomeRedirect />} />
      <Route element={<Protected><Shell /></Protected>}>
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/profile/edit" element={<ProfileEditPage />} />
        <Route path="/attendance" element={<AttendancePage />} />
        <Route path="/leave" element={<LeavePage />} />
        <Route path="/leave/new" element={<LeaveFormPage />} />
        <Route path="/employees" element={<AdminOnly><EmployeesPage /></AdminOnly>} />
        <Route path="/employees/new" element={<AdminOnly><EmployeeFormPage mode="create" /></AdminOnly>} />
        <Route path="/employees/change-requests" element={<AdminOnly><ChangeRequestsPage /></AdminOnly>} />
        <Route path="/employees/:id" element={<AdminOnly><EmployeeDetailPage /></AdminOnly>} />
        <Route path="/employees/:id/edit" element={<AdminOnly><EmployeeFormPage mode="edit" /></AdminOnly>} />
        <Route path="/payroll" element={<AdminOnly><PlaceholderPage page="payroll" /></AdminOnly>} />
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/recognition" element={<RecognitionPage />} />
        <Route path="/simulation" element={<AdminOnly><SimulationPage /></AdminOnly>} />
        <Route path="/chatbot" element={<ChatbotPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/not-found" replace />} />
    </Routes>
  )
}
