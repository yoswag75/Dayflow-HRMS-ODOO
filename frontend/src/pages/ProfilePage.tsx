import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, BriefcaseBusiness, CalendarDays, Mail } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth'
import { EmptyState, ErrorState, PageLoader, StatusTag } from '../components/Status'
import { employeeService } from '../services'

export function ProfilePage() {
  const { session } = useAuth()
  const query = useQuery({ queryKey: ['employee', session?.employeeId], queryFn: () => employeeService.get(session!.employeeId) })
  if (query.isLoading) return <PageLoader rows={6} />
  if (query.isError) return <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} />
  const employee = query.data!
  return <><div className="page-heading"><div><p className="eyebrow">Personal workspace</p><h1>My profile</h1><p>Review the employment information currently held by HR.</p></div></div><section className="profile-grid"><div className="profile-summary"><div className="initial-tile">{employee.name.split(' ').map((part) => part[0]).join('').slice(0, 2)}</div><div><h2>{employee.name}</h2><p>{employee.designation || 'No designation'}</p><StatusTag value={employee.status} /></div></div><div className="details-panel"><Info icon={Mail} label="Email" value={employee.email} /><Info icon={BriefcaseBusiness} label="Department" value={employee.department} /><Info icon={BriefcaseBusiness} label="Designation" value={employee.designation} /><Info icon={CalendarDays} label="Joined" value={employee.joinedOn} /></div></section></>
}

export function ProfileEditPage() {
  return <><div className="page-heading"><div><Link className="back-link" to="/profile"><ArrowLeft size={15} />Back to profile</Link><p className="eyebrow">Unavailable</p><h1>Profile editing is not connected</h1><p>The current backend exposes employee records as read-only.</p></div></div><EmptyState title="Read-only profile" message="HR and employee profile update endpoints still need to be implemented." /></>
}

function Info({ icon: Icon, label, value }: { icon: typeof Mail; label: string; value: string }) { return <div className="info-row"><Icon size={17} /><span>{label}<strong>{value || '—'}</strong></span></div> }
