import { useState } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { Bell, Bot, CalendarDays, ChevronDown, CircleUserRound, ClipboardCheck, Coins, LogOut, Menu, MessageSquareText, Settings2, Sparkles, UserRound, Users, X } from 'lucide-react'
import { useAuth } from '../auth'

const employeeItems = [
  { to: '/profile', label: 'My profile', icon: UserRound },
  { to: '/attendance', label: 'Attendance', icon: CalendarDays },
  { to: '/leave', label: 'Time off', icon: ClipboardCheck },
  { to: '/onboarding', label: 'Onboarding', icon: Sparkles, planned: true },
  { to: '/recognition', label: 'Recognition', icon: Coins, planned: true },
  { to: '/notifications', label: 'Notifications', icon: Bell, planned: true },
]

const adminItems = [
  { to: '/employees', label: 'Employees', icon: Users },
  { to: '/attendance', label: 'Attendance', icon: CalendarDays },
  { to: '/leave', label: 'Time off', icon: ClipboardCheck },
  { to: '/payroll', label: 'Payroll', icon: Coins, planned: true },
  { to: '/onboarding', label: 'Onboarding', icon: Sparkles, planned: true },
  { to: '/recognition', label: 'Recognition', icon: Settings2, planned: true },
  { to: '/simulation', label: 'Simulation', icon: MessageSquareText, planned: true },
  { to: '/chatbot', label: 'Chatbot', icon: Bot, planned: true },
  { to: '/notifications', label: 'Notifications', icon: Bell, planned: true },
]

const routeNames: Record<string, string> = {
  profile: 'My profile', employees: 'Employees', attendance: 'Attendance', leave: 'Time off', payroll: 'Payroll', onboarding: 'Onboarding', recognition: 'Recognition', simulation: 'Simulation', chatbot: 'Chatbot', notifications: 'Notifications', new: 'New', edit: 'Edit', 'change-requests': 'Change requests',
}

export function Shell() {
  const { session, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const [accountOpen, setAccountOpen] = useState(false)
  const items = session?.role === 'employee' ? employeeItems : adminItems
  const crumbs = location.pathname.split('/').filter(Boolean).map((part) => routeNames[part] ?? 'Details')

  const signOut = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="app-shell">
      {open && <button className="drawer-scrim" aria-label="Close navigation" onClick={() => setOpen(false)} />}
      <aside className={`sidebar ${open ? 'sidebar-open' : ''}`}>
        <div className="sidebar-mobile-head"><span>Navigation</span><button className="icon-button" aria-label="Close navigation" onClick={() => setOpen(false)}><X /></button></div>
        <nav aria-label="Primary navigation">
          {items.map(({ to, label, icon: Icon, planned }) => (
            <NavLink key={to} to={to} onClick={() => setOpen(false)} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <Icon size={17} aria-hidden="true" /><span>{label}</span>{planned && <small>Later</small>}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-account">
          <CircleUserRound size={20} aria-hidden="true" />
          <div><strong>{session?.name}</strong><span>{session?.role === 'employee' ? 'Employee' : 'HR / Admin'}</span></div>
          <button className="icon-button" onClick={signOut} aria-label="Sign out"><LogOut size={17} /></button>
        </div>
      </aside>
      <div className="app-stage">
        <header className="utility-header">
          <button className="icon-button mobile-menu" aria-label="Open navigation" onClick={() => setOpen(true)}><Menu /></button>
          <div className="breadcrumbs" aria-label="Breadcrumb">{crumbs.map((crumb, index) => <span key={`${crumb}-${index}`}>{crumb}</span>)}</div>
          <div className="header-actions">
            <NavLink className="icon-button" to="/notifications" aria-label="Notifications"><Bell size={17} /></NavLink>
            <div className="account-menu-wrap">
              <button className="account-button" onClick={() => setAccountOpen((value) => !value)} aria-expanded={accountOpen}><span>{session?.name}</span><ChevronDown size={14} /></button>
              {accountOpen && <div className="account-menu"><button onClick={() => navigate('/profile')}><UserRound size={15} />Profile</button><button onClick={signOut}><LogOut size={15} />Sign out</button></div>}
            </div>
          </div>
        </header>
        <main className="page-stage"><Outlet /></main>
      </div>
    </div>
  )
}
