import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Check, ChevronRight, Filter, Plus, Search, UserRound, X } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ErrorState, EmptyState, InlineLoader, PageLoader, StatusTag } from '../components/Status'
import { employeeService } from '../services'
import type { Employee } from '../types'

export function EmployeesPage() {
  const [search, setSearch] = useState('')
  const [department, setDepartment] = useState('all')
  const query = useQuery({ queryKey: ['employees'], queryFn: employeeService.list })
  const employees = query.data ?? []
  const departments = [...new Set(employees.map((employee) => employee.department))]
  const filtered = useMemo(() => employees.filter((employee) => {
    const matchesTerm = `${employee.name} ${employee.loginId} ${employee.department}`.toLowerCase().includes(search.toLowerCase())
    return matchesTerm && (department === 'all' || employee.department === department)
  }), [employees, search, department])

  return <><div className="page-heading"><div><p className="eyebrow">People directory</p><h1>Employees</h1><p>Find employees, review status, and manage profiles.</p></div><div className="heading-actions"><Link className="button button-secondary" to="/employees/change-requests">Change requests</Link><Link className="button button-primary" to="/employees/new"><Plus size={15} />Add employee</Link></div></div><div className="filter-bar"><label className="search-field"><Search size={16} /><span className="sr-only">Search employees</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search name, ID, or department" /></label><label className="select-field"><Filter size={15} /><span className="sr-only">Filter department</span><select value={department} onChange={(event) => setDepartment(event.target.value)}><option value="all">All departments</option>{departments.map((item) => <option key={item}>{item}</option>)}</select></label></div>{query.isLoading ? <PageLoader /> : query.isError ? <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} /> : filtered.length === 0 ? <EmptyState title="No employees found" message="Try a broader search or remove the department filter." /> : <div className="data-surface"><table className="data-table"><thead><tr><th>Employee</th><th>Department</th><th>Designation</th><th>Status</th><th><span className="sr-only">Action</span></th></tr></thead><tbody>{filtered.map((employee) => <tr key={employee.id}><td><Link className="person-cell" to={`/employees/${employee.id}`}><span className="mini-initial">{initials(employee.name)}</span><span><strong>{employee.name}</strong><small>{employee.loginId}</small></span></Link></td><td>{employee.department}</td><td>{employee.designation}</td><td><StatusTag value={employee.status} /></td><td><Link className="icon-button" to={`/employees/${employee.id}`} aria-label={`View ${employee.name}`}><ChevronRight /></Link></td></tr>)}</tbody></table><div className="mobile-list">{filtered.map((employee) => <Link className="mobile-record" to={`/employees/${employee.id}`} key={employee.id}><span className="mini-initial">{initials(employee.name)}</span><span><strong>{employee.name}</strong><small>{employee.designation} · {employee.department}</small></span><StatusTag value={employee.status} /></Link>)}</div></div>}</>
}

export function EmployeeDetailPage() {
  const id = Number(useParams().id)
  const query = useQuery({ queryKey: ['employee', id], queryFn: () => employeeService.get(id) })
  if (query.isLoading) return <PageLoader />
  if (query.isError) return <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} />
  const employee = query.data!
  return <><div className="page-heading"><div><Link className="back-link" to="/employees"><ArrowLeft size={15} />Back to employees</Link><h1>{employee.name}</h1><p>{employee.designation} · {employee.department}</p></div><Link className="button button-primary" to={`/employees/${employee.id}/edit`}>Edit employee</Link></div><section className="profile-grid"><div className="profile-summary"><div className="initial-tile">{initials(employee.name)}</div><div><h2>{employee.name}</h2><p>{employee.loginId}</p><StatusTag value={employee.status} /></div></div><div className="details-panel"><Detail label="Email" value={employee.email} /><Detail label="Phone" value={employee.phone} /><Detail label="Manager" value={employee.manager} /><Detail label="Location" value={employee.location} /><Detail label="Joined" value={employee.joinedOn} /></div><div className="content-panel"><h2>About</h2><p>{employee.about || 'No introduction has been added.'}</p><h3>Skills</h3><div className="skill-list">{employee.skills.map((skill) => <span key={skill}>{skill}</span>)}</div></div></section></>
}

export function EmployeeFormPage({ mode }: { mode: 'create' | 'edit' }) {
  const id = Number(useParams().id)
  const navigate = useNavigate()
  const client = useQueryClient()
  const employeeQuery = useQuery({ queryKey: ['employee', id], queryFn: () => employeeService.get(id), enabled: mode === 'edit' })
  const mutation = useMutation({ mutationFn: (input: Omit<Employee, 'id' | 'userId' | 'status' | 'about' | 'skills'>) => mode === 'create' ? employeeService.create(input) : employeeService.update(id, input), onSuccess: (employee) => { client.invalidateQueries({ queryKey: ['employees'] }); client.invalidateQueries({ queryKey: ['employee', employee.id] }); navigate(`/employees/${employee.id}`, { replace: true }) } })
  if (mode === 'edit' && employeeQuery.isLoading) return <PageLoader />
  if (mode === 'edit' && employeeQuery.isError) return <ErrorState message={(employeeQuery.error as Error).message} />
  const employee = employeeQuery.data
  const submit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    mutation.mutate({ name: String(data.get('name')), loginId: String(data.get('loginId')), email: String(data.get('email')), phone: String(data.get('phone')), department: String(data.get('department')), designation: String(data.get('designation')), manager: String(data.get('manager')), location: String(data.get('location')), joinedOn: String(data.get('joinedOn')) })
  }
  return <><div className="page-heading"><div><Link className="back-link" to={employee ? `/employees/${employee.id}` : '/employees'}><ArrowLeft size={15} />Back</Link><h1>{mode === 'create' ? 'Add employee' : 'Edit employee'}</h1><p>{mode === 'create' ? 'Create an account and the employee’s initial profile.' : 'Update employment and contact details.'}</p></div></div><form className="form-page" onSubmit={submit}><section><h2>Personal information</h2><div className="form-grid"><RequiredField name="name" label="Full name" defaultValue={employee?.name} /><RequiredField name="email" label="Work email" type="email" defaultValue={employee?.email} /><RequiredField name="phone" label="Phone" defaultValue={employee?.phone} /><RequiredField name="location" label="Location" defaultValue={employee?.location} /></div></section><section><h2>Employment</h2><div className="form-grid"><RequiredField name="loginId" label="Login ID" defaultValue={employee?.loginId} /><RequiredField name="department" label="Department" defaultValue={employee?.department} /><RequiredField name="designation" label="Designation" defaultValue={employee?.designation} /><RequiredField name="manager" label="Manager" defaultValue={employee?.manager} /><RequiredField name="joinedOn" label="Joining date" type="date" defaultValue={employee?.joinedOn} /></div></section>{mutation.isError && <ErrorState message={(mutation.error as Error).message} />}<div className="form-actions"><button type="button" className="button button-secondary" onClick={() => navigate(-1)}>Cancel</button><button className="button button-primary" disabled={mutation.isPending}>{mutation.isPending ? <InlineLoader label="Saving" /> : mode === 'create' ? 'Create employee' : 'Save changes'}</button></div></form></>
}

export function ChangeRequestsPage() {
  const client = useQueryClient()
  const query = useQuery({ queryKey: ['change-requests'], queryFn: employeeService.changes })
  const mutation = useMutation({ mutationFn: ({ id, status }: { id: number; status: 'approved' | 'rejected' }) => employeeService.resolveChange(id, status), onSuccess: () => client.invalidateQueries({ queryKey: ['change-requests'] }) })
  return <><div className="page-heading"><div><Link className="back-link" to="/employees"><ArrowLeft size={15} />Back to employees</Link><h1>Change requests</h1><p>Review verified profile updates before they are applied.</p></div></div>{query.isLoading ? <PageLoader /> : query.isError ? <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} /> : !query.data?.length ? <EmptyState title="No pending requests" message="Verified profile edits will appear here." /> : <div className="request-list">{query.data.map((request) => <article className="request-card" key={request.id}><div className="request-head"><div><strong>{request.employeeName}</strong><span>{request.field}</span></div><StatusTag value={request.status} /></div><div className="diff-grid"><div><span>Current</span><p>{request.oldValue}</p></div><div><span>Requested</span><p>{request.newValue}</p></div></div><p className="request-reason">{request.reason}</p>{request.status === 'pending' && <div className="request-actions"><button className="button button-secondary danger-button" disabled={mutation.isPending} onClick={() => mutation.mutate({ id: request.id, status: 'rejected' })}><X size={15} />Reject</button><button className="button button-primary" disabled={mutation.isPending} onClick={() => mutation.mutate({ id: request.id, status: 'approved' })}><Check size={15} />Approve</button></div>}</article>)}</div>}</>
}

function RequiredField({ name, label, type = 'text', defaultValue }: { name: string; label: string; type?: string; defaultValue?: string }) { return <label className="field"><span>{label}</span><input required name={name} type={type} defaultValue={defaultValue ?? ''} /></label> }
function Detail({ label, value }: { label: string; value: string }) { return <div className="detail-pair"><span>{label}</span><strong>{value}</strong></div> }
function initials(name: string) { return name.split(' ').map((part) => part[0]).join('').slice(0, 2) }
