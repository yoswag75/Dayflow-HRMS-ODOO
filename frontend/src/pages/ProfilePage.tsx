import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, BriefcaseBusiness, Mail, MapPin, Pencil, Phone, Save, ShieldCheck } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import { ErrorState, InlineLoader, PageLoader, StatusTag } from '../components/Status'
import { employeeService } from '../services'

export function ProfilePage() {
  const { session } = useAuth()
  const query = useQuery({ queryKey: ['employee', session?.employeeId], queryFn: () => employeeService.get(session!.employeeId) })
  if (query.isLoading) return <PageLoader rows={6} />
  if (query.isError) return <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} />
  const employee = query.data!
  return <><div className="page-heading"><div><p className="eyebrow">Personal workspace</p><h1>My profile</h1><p>Review your work information and manage the fields you own.</p></div><Link to="/profile/edit" className="button button-primary"><Pencil size={15} />Edit profile</Link></div><section className="profile-grid"><div className="profile-summary"><div className="initial-tile">{employee.name.split(' ').map((part) => part[0]).join('')}</div><div><h2>{employee.name}</h2><p>{employee.designation}</p><StatusTag value={employee.status} /></div></div><div className="details-panel"><Info icon={Mail} label="Email" value={employee.email} /><Info icon={Phone} label="Phone" value={employee.phone} /><Info icon={BriefcaseBusiness} label="Department" value={employee.department} /><Info icon={MapPin} label="Location" value={employee.location} /></div><div className="content-panel"><h2>About</h2><p>{employee.about}</p><h3>Skills</h3><div className="skill-list">{employee.skills.map((skill) => <span key={skill}>{skill}</span>)}</div></div><div className="content-panel pastel-note"><ShieldCheck size={19} /><div><h2>Verified information</h2><p>Phone, address, emergency contact, and bank details are reviewed before they change.</p></div></div></section></>
}

function Info({ icon: Icon, label, value }: { icon: typeof Mail; label: string; value: string }) { return <div className="info-row"><Icon size={17} /><span>{label}<strong>{value}</strong></span></div> }

export function ProfileEditPage() {
  const { session } = useAuth()
  const navigate = useNavigate()
  const client = useQueryClient()
  const query = useQuery({ queryKey: ['employee', session?.employeeId], queryFn: () => employeeService.get(session!.employeeId) })
  const [message, setMessage] = useState('')
  const mutation = useMutation({ mutationFn: (updates: { about: string; phone: string; location: string }) => employeeService.update(session!.employeeId, updates), onSuccess: () => { client.invalidateQueries({ queryKey: ['employee', session?.employeeId] }); setMessage('Profile saved. Verified fields are shown as pending review.'); window.setTimeout(() => navigate('/profile'), 650) } })
  if (query.isLoading) return <PageLoader />
  if (query.isError) return <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} />
  const employee = query.data!
  return <><div className="page-heading"><div><Link className="back-link" to="/profile"><ArrowLeft size={15} />Back to profile</Link><h1>Edit profile</h1><p>Self-serve details update immediately. Verified details enter review.</p></div></div>{message && <div className="success-banner" role="status">{message}</div>}<form className="form-page" onSubmit={(event) => { event.preventDefault(); const values = new FormData(event.currentTarget); mutation.mutate({ about: String(values.get('about')), phone: String(values.get('phone')), location: String(values.get('location')) }) }}><section><h2>Self-serve information</h2><label className="field"><span>About</span><textarea name="about" rows={5} defaultValue={employee.about} /></label></section><section><div className="section-heading"><div><h2>Verified information</h2><p>Changes here are recorded for HR review.</p></div><ShieldCheck size={18} /></div><div className="form-grid"><label className="field"><span>Phone</span><input name="phone" defaultValue={employee.phone} /></label><label className="field"><span>Location</span><input name="location" defaultValue={employee.location} /></label></div></section>{mutation.isError && <ErrorState message={(mutation.error as Error).message} />}<div className="form-actions"><Link className="button button-secondary" to="/profile">Cancel</Link><button className="button button-primary" disabled={mutation.isPending}><Save size={15} />{mutation.isPending ? <InlineLoader label="Saving" /> : 'Save changes'}</button></div></form></>
}
