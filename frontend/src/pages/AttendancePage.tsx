import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Clock3, LogIn, LogOut } from 'lucide-react'
import { useAuth } from '../auth'
import { ErrorState, InlineLoader, PageLoader, StatusTag } from '../components/Status'
import { attendanceService, employeeService } from '../services'

export function AttendancePage() {
  const { session } = useAuth()
  const isEmployee = session?.role === 'employee'
  const client = useQueryClient()
  const employeeQuery = useQuery({ queryKey: ['employee', session?.employeeId], queryFn: () => employeeService.get(session!.employeeId), enabled: isEmployee })
  const query = useQuery({ queryKey: ['attendance', isEmployee ? session?.employeeId : 'all'], queryFn: () => attendanceService.list(isEmployee ? session!.employeeId : undefined) })
  const action = useMutation({ mutationFn: (kind: 'in' | 'out') => kind === 'in' ? attendanceService.checkIn(employeeQuery.data!) : attendanceService.checkOut(session!.employeeId), onSuccess: () => client.invalidateQueries({ queryKey: ['attendance'] }) })
  const todayDate = new Date().toISOString().slice(0, 10)
  const today = query.data?.find((record) => record.employeeId === session?.employeeId && record.date === todayDate)

  return <><div className="page-heading"><div><p className="eyebrow">Daily records</p><h1>Attendance</h1><p>{isEmployee ? 'Check in, check out, and review your recent activity.' : 'Review today’s workforce attendance and status.'}</p></div>{isEmployee && <div className="heading-actions"><button className="button button-secondary" disabled={action.isPending || !!today?.checkIn} onClick={() => action.mutate('in')}><LogIn size={15} />Check in</button><button className="button button-primary" disabled={action.isPending || !today?.checkIn || !!today?.checkOut} onClick={() => action.mutate('out')}><LogOut size={15} />{action.isPending ? <InlineLoader label="Updating" /> : 'Check out'}</button></div>}</div>{action.isError && <ErrorState message={(action.error as Error).message} />}{query.isLoading ? <PageLoader /> : query.isError ? <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} /> : <><div className="stat-strip"><div><span>Today</span><strong>{today?.status.replace('_', ' ') ?? (isEmployee ? 'Not checked in' : `${query.data?.filter((item) => item.status === 'present').length ?? 0} present`)}</strong></div><div><span>Check in</span><strong>{today?.checkIn ?? '—'}</strong></div><div><span>Check out</span><strong>{today?.checkOut ?? '—'}</strong></div><div><span>Work hours</span><strong>{today?.workHours ? `${today.workHours}h` : '—'}</strong></div></div><div className="data-surface"><table className="data-table"><thead><tr>{!isEmployee && <th>Employee</th>}<th>Date</th><th>Check in</th><th>Check out</th><th>Hours</th><th>Status</th></tr></thead><tbody>{query.data?.map((record) => <tr key={record.id}>{!isEmployee && <td><strong>{record.employeeName}</strong></td>}<td>{record.date}</td><td>{record.checkIn ?? '—'}</td><td>{record.checkOut ?? '—'}</td><td>{record.workHours ? `${record.workHours}h` : '—'}</td><td><StatusTag value={record.status} /></td></tr>)}</tbody></table><div className="mobile-list">{query.data?.map((record) => <div className="mobile-record" key={record.id}><Clock3 size={17} /><span><strong>{isEmployee ? record.date : record.employeeName}</strong><small>{record.checkIn ?? '—'} → {record.checkOut ?? '—'}</small></span><StatusTag value={record.status} /></div>)}</div></div></>}</>
}
