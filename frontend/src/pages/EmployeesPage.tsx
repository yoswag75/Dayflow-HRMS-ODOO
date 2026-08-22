import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, ChevronRight, Copy, Filter, Plus, Search } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { EmptyState, ErrorState, InlineLoader, PageLoader, StatusTag } from '../components/Status'
import { employeeService } from '../services'
import type { Employee, OnboardResult } from '../types'

export function EmployeesPage() {
  const [search, setSearch] = useState('')
  const [department, setDepartment] = useState('all')
  const query = useQuery({ queryKey: ['employees'], queryFn: employeeService.list })
  const employees = query.data ?? []
  const departments = [...new Set(employees.map((employee) => employee.department).filter(Boolean))]
  const filtered = useMemo(() => employees.filter((employee) => {
    const matches = `${employee.name} ${employee.email} ${employee.department}`.toLowerCase().includes(search.toLowerCase())
    return matches && (department === 'all' || employee.department === department)
  }), [employees, search, department])

  return <>
    <div className="page-heading"><div><p className="eyebrow">People directory</p><h1>Employees</h1><p>Find employees and onboard new teammates.</p></div><Link className="button button-primary" to="/employees/new"><Plus size={15} />Add employee</Link></div>
    <div className="filter-bar"><label className="search-field"><Search size={16} /><span className="sr-only">Search employees</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search name, email, or department" /></label><label className="select-field"><Filter size={15} /><span className="sr-only">Filter department</span><select value={department} onChange={(event) => setDepartment(event.target.value)}><option value="all">All departments</option>{departments.map((item) => <option key={item}>{item}</option>)}</select></label></div>
    {query.isLoading ? <PageLoader /> : query.isError ? <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} /> : filtered.length === 0 ? <EmptyState title="No employees found" message="Add the first employee or adjust your filters." /> : <div className="data-surface"><table className="data-table"><thead><tr><th>Employee</th><th>Department</th><th>Designation</th><th>Status</th><th><span className="sr-only">Action</span></th></tr></thead><tbody>{filtered.map((employee) => <tr key={employee.id}><td><Link className="person-cell" to={`/employees/${employee.id}`}><span className="mini-initial">{initials(employee.name)}</span><span><strong>{employee.name}</strong><small>{employee.email}</small></span></Link></td><td>{employee.department || '—'}</td><td>{employee.designation || '—'}</td><td><StatusTag value={employee.status} /></td><td><Link className="icon-button" to={`/employees/${employee.id}`} aria-label={`View ${employee.name}`}><ChevronRight /></Link></td></tr>)}</tbody></table><div className="mobile-list">{filtered.map((employee) => <Link className="mobile-record" to={`/employees/${employee.id}`} key={employee.id}><span className="mini-initial">{initials(employee.name)}</span><span><strong>{employee.name}</strong><small>{employee.designation || 'No designation'} · {employee.department || 'No department'}</small></span><StatusTag value={employee.status} /></Link>)}</div></div>}
  </>
}

export function EmployeeDetailPage() {
  const id = Number(useParams().id)
  const query = useQuery({ queryKey: ['employee', id], queryFn: () => employeeService.get(id) })
  if (query.isLoading) return <PageLoader />
  if (query.isError) return <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} />
  const employee = query.data!
  return <><div className="page-heading"><div><Link className="back-link" to="/employees"><ArrowLeft size={15} />Back to employees</Link><h1>{employee.name}</h1><p>{employee.designation || 'No designation'} · {employee.department || 'No department'}</p></div></div><section className="profile-grid"><div className="profile-summary"><div className="initial-tile">{initials(employee.name)}</div><div><h2>{employee.name}</h2><p>{employee.email}</p><StatusTag value={employee.status} /></div></div><div className="details-panel"><Detail label="Email" value={employee.email} /><Detail label="Department" value={employee.department} /><Detail label="Designation" value={employee.designation} /><Detail label="Joined" value={employee.joinedOn} /></div></section></>
}

export function EmployeeFormPage({ mode }: { mode: 'create' | 'edit' }) {
  const navigate = useNavigate()
  const client = useQueryClient()
  const [created, setCreated] = useState<OnboardResult | null>(null)
  const mutation = useMutation({
    mutationFn: employeeService.create,
    onSuccess: (result) => {
      setCreated(result)
      client.invalidateQueries({ queryKey: ['employees'] })
    },
  })
  if (mode === 'edit') return <Unavailable title="Employee editing is not connected" message="The current backend supports employee creation and viewing, but not profile updates." />
  if (created) return <><div className="page-heading"><div><p className="eyebrow">Employee onboarded</p><h1>{created.employee.name}</h1><p>The account and onboarding checklist are ready.</p></div></div><div className="credential-panel"><strong>Temporary password</strong><code>{created.temporaryPassword}</code><button className="button button-secondary" onClick={() => navigator.clipboard.writeText(created.temporaryPassword)}><Copy size={15} />Copy password</button><p>Share this once through a secure channel. The employee will be asked to replace it after signing in.</p></div><div className="form-actions"><button className="button button-primary" onClick={() => navigate(`/employees/${created.employee.id}`)}>View employee</button><button className="button button-secondary" onClick={() => setCreated(null)}>Add another</button></div></>

  const submit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    mutation.mutate({
      name: String(data.get('name')),
      email: String(data.get('email')),
      department: String(data.get('department')),
      designation: String(data.get('designation')),
      joinedOn: String(data.get('joinedOn')),
      loginId: '', phone: '', manager: '', location: '',
    })
  }
  return <><div className="page-heading"><div><Link className="back-link" to="/employees"><ArrowLeft size={15} />Back</Link><h1>Add employee</h1><p>Create a real employee account and onboarding checklist.</p></div></div><form className="form-page" onSubmit={submit}><section><h2>Employee information</h2><div className="form-grid"><RequiredField name="name" label="Full name" /><RequiredField name="email" label="Work email" type="email" /><RequiredField name="department" label="Department" /><RequiredField name="designation" label="Designation" /><RequiredField name="joinedOn" label="Joining date" type="date" /></div></section>{mutation.isError && <ErrorState message={(mutation.error as Error).message} />}<div className="form-actions"><button type="button" className="button button-secondary" onClick={() => navigate(-1)}>Cancel</button><button className="button button-primary" disabled={mutation.isPending}>{mutation.isPending ? <InlineLoader label="Creating" /> : 'Create employee'}</button></div></form></>
}

export function ChangeRequestsPage() {
  return <Unavailable title="Change requests are not connected" message="The backend data model exists, but employee change-request routes are not available yet." />
}

function Unavailable({ title, message }: { title: string; message: string }) { return <><div className="page-heading"><div><p className="eyebrow">Unavailable</p><h1>{title}</h1><p>{message}</p></div></div><EmptyState title="Not connected yet" message={message} /></> }
function RequiredField({ name, label, type = 'text' }: { name: string; label: string; type?: string }) { return <label className="field"><span>{label}</span><input required name={name} type={type} /></label> }
function Detail({ label, value }: { label: string; value: string }) { return <div className="detail-pair"><span>{label}</span><strong>{value || '—'}</strong></div> }
function initials(name: string) { return name.split(' ').map((part) => part[0]).join('').slice(0, 2) }
