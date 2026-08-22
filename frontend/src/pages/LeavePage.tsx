import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check, Plus, X } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import { EmptyState, ErrorState, InlineLoader, PageLoader, StatusTag } from '../components/Status'
import { employeeService, leaveService } from '../services'

export function LeavePage() {
  const { session } = useAuth()
  const isEmployee = session?.role === 'employee'
  const client = useQueryClient()
  const query = useQuery({ queryKey: ['leave', isEmployee ? session?.employeeId : 'all'], queryFn: () => leaveService.list(isEmployee ? session!.employeeId : undefined) })
  const resolve = useMutation({ mutationFn: ({ id, status }: { id: number; status: 'approved' | 'rejected' }) => leaveService.resolve(id, status), onSuccess: () => client.invalidateQueries({ queryKey: ['leave'] }) })
  return <><div className="page-heading"><div><p className="eyebrow">Requests and approvals</p><h1>Time off</h1><p>{isEmployee ? 'Request leave and follow its approval status.' : 'Review and resolve employee leave requests.'}</p></div>{isEmployee && <Link className="button button-primary" to="/leave/new"><Plus size={15} />Request time off</Link>}</div>{query.isLoading ? <PageLoader /> : query.isError ? <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} /> : !query.data?.length ? <EmptyState title="No leave requests" message="New leave requests will appear here." action={isEmployee ? <Link className="button button-primary" to="/leave/new">Create request</Link> : undefined} /> : <div className="request-list">{query.data.map((request) => <article className="leave-card" key={request.id}><div><div className="leave-title"><strong>{isEmployee ? titleCase(request.type) : request.employeeName}</strong><StatusTag value={request.status} /></div><p>{isEmployee ? `${request.startDate} to ${request.endDate}` : `${titleCase(request.type)} · ${request.startDate} to ${request.endDate}`}</p><small>{request.remarks}</small></div>{!isEmployee && request.status === 'pending' && <div className="request-actions"><button className="button button-secondary danger-button" disabled={resolve.isPending} onClick={() => resolve.mutate({ id: request.id, status: 'rejected' })}><X size={15} />Reject</button><button className="button button-primary" disabled={resolve.isPending} onClick={() => resolve.mutate({ id: request.id, status: 'approved' })}><Check size={15} />Approve</button></div>}</article>)}</div>}</>
}

export function LeaveFormPage() {
  const { session } = useAuth()
  const navigate = useNavigate()
  const client = useQueryClient()
  const [type, setType] = useState<'paid' | 'sick' | 'unpaid'>('paid')
  const employeeQuery = useQuery({ queryKey: ['employee', session?.employeeId], queryFn: () => employeeService.get(session!.employeeId) })
  const mutation = useMutation({ mutationFn: (input: { startDate: string; endDate: string; remarks: string }) => leaveService.apply({ ...input, type, employeeId: session!.employeeId, employeeName: employeeQuery.data?.name ?? '' }), onSuccess: () => { client.invalidateQueries({ queryKey: ['leave'] }); navigate('/leave', { replace: true }) } })
  const submit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const values = new FormData(event.currentTarget)
    const startDate = String(values.get('startDate'))
    const endDate = String(values.get('endDate'))
    if (endDate < startDate) return
    mutation.mutate({ startDate, endDate, remarks: String(values.get('remarks')) })
  }
  return <><div className="page-heading"><div><Link className="back-link" to="/leave">← Back to time off</Link><h1>Request time off</h1><p>Emergency fast-track is hidden until the backend supports provisional approval.</p></div></div><form className="form-page compact-form" onSubmit={submit}><section><label className="field"><span>Leave type</span><select value={type} onChange={(event) => setType(event.target.value as typeof type)}><option value="paid">Paid leave</option><option value="sick">Sick leave</option><option value="unpaid">Unpaid leave</option></select></label><div className="form-grid"><label className="field"><span>Start date</span><input required name="startDate" type="date" /></label><label className="field"><span>End date</span><input required name="endDate" type="date" /></label></div><label className="field"><span>Reason</span><textarea required name="remarks" rows={4} /></label></section>{mutation.isError && <ErrorState message={(mutation.error as Error).message} />}<div className="form-actions"><Link className="button button-secondary" to="/leave">Cancel</Link><button className="button button-primary" disabled={mutation.isPending}>{mutation.isPending ? <InlineLoader label="Submitting" /> : 'Submit request'}</button></div></form></>
}

function titleCase(value: string) { return value.charAt(0).toUpperCase() + value.slice(1) }
