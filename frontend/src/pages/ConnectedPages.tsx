import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Bell, Bot, Check, Coins, Send, Sparkles } from 'lucide-react'
import { useAuth } from '../auth'
import { EmptyState, ErrorState, InlineLoader, PageLoader, StatusTag } from '../components/Status'
import { chatbotService, notificationService, onboardingService, recognitionService, simulationService } from '../services'

export function OnboardingPage() {
  const { session } = useAuth()
  const client = useQueryClient()
  const query = useQuery({ queryKey: ['onboarding'], queryFn: onboardingService.mine, enabled: session?.role === 'employee' })
  const complete = useMutation({ mutationFn: onboardingService.complete, onSuccess: () => client.invalidateQueries({ queryKey: ['onboarding'] }) })
  if (session?.role !== 'employee') return <Unavailable title="Onboarding administration is not connected" message="Employee checklists work, but the backend only returns aggregate status to HR." />
  return <><Heading eyebrow="Getting started" title="Onboarding" text="Complete the checklist created when your employee account was opened." />{query.isLoading ? <PageLoader /> : query.isError ? <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} /> : !query.data?.length ? <EmptyState title="No onboarding tasks" message="HR has not assigned a checklist to this account." /> : <div className="request-list">{query.data.map((task) => <article className="request-card" key={task.id}><div className="request-head"><div><strong>{task.taskName}</strong><span>{task.dueDate || 'No due date'}</span></div><StatusTag value={task.status} /></div>{task.status !== 'done' && <button className="button button-primary" disabled={complete.isPending} onClick={() => complete.mutate(task.id)}><Check size={15} />Mark complete</button>}</article>)}</div>}</>
}

export function RecognitionPage() {
  const query = useQuery({ queryKey: ['leaderboard'], queryFn: recognitionService.leaderboard })
  return <><Heading eyebrow="Recognition" title="Leaderboard" text="Points already recorded by the backend, ranked without frontend fixtures." />{query.isLoading ? <PageLoader /> : query.isError ? <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} /> : !query.data?.length ? <EmptyState title="No points yet" message="The leaderboard will populate when backend events award points." /> : <div className="data-surface"><table className="data-table"><thead><tr><th>Rank</th><th>Employee</th><th>Department</th><th>Points</th></tr></thead><tbody>{query.data.map((entry) => <tr key={entry.employeeId}><td>#{entry.rank}</td><td>{entry.employeeName}</td><td>{entry.department}</td><td><strong>{entry.totalPoints}</strong></td></tr>)}</tbody></table></div>}</>
}

export function NotificationsPage() {
  const client = useQueryClient()
  const query = useQuery({ queryKey: ['notifications'], queryFn: notificationService.list })
  const read = useMutation({ mutationFn: notificationService.markRead, onSuccess: () => client.invalidateQueries({ queryKey: ['notifications'] }) })
  return <><Heading eyebrow="Inbox" title="Notifications" text="Alerts created by connected backend workflows." />{query.isLoading ? <PageLoader /> : query.isError ? <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} /> : !query.data?.length ? <EmptyState title="You’re all caught up" message="New backend notifications will appear here." /> : <div className="request-list">{query.data.map((item) => <article className={`request-card ${item.read ? 'is-read' : ''}`} key={item.id}><div className="request-head"><div><strong>{item.title}</strong><span>{item.type.toLowerCase().replace('_', ' ')}</span></div>{!item.read && <button className="button button-secondary" onClick={() => read.mutate(item.id)}><Bell size={14} />Mark read</button>}</div><p>{item.body}</p></article>)}</div>}</>
}

export function SimulationPage() {
  const [result, setResult] = useState<{ summary: string; impact: Record<string, unknown>; warnings: string[] } | null>(null)
  const mutation = useMutation({ mutationFn: ({ department, delta, salary }: { department: string; delta: number; salary: number }) => simulationService.runHeadcount(department, delta, salary), onSuccess: setResult })
  return <><Heading eyebrow="What-if planning" title="Headcount simulation" text="Estimate the annual cost impact of adding or removing roles." /><form className="form-page compact-form" onSubmit={(event) => { event.preventDefault(); const data = new FormData(event.currentTarget); mutation.mutate({ department: String(data.get('department')), delta: Number(data.get('delta')), salary: Number(data.get('salary')) }) }}><section><div className="form-grid"><Field name="department" label="Department" /><Field name="delta" label="Headcount change" type="number" /><Field name="salary" label="Average monthly salary" type="number" /></div></section>{mutation.isError && <ErrorState message={(mutation.error as Error).message} />}<button className="button button-primary" disabled={mutation.isPending}>{mutation.isPending ? <InlineLoader label="Running" /> : 'Run simulation'}</button></form>{result && <div className="placeholder-panel"><Sparkles size={22} /><div><strong>{result.summary}</strong><pre>{JSON.stringify(result.impact, null, 2)}</pre>{result.warnings.map((warning) => <p key={warning}>{warning}</p>)}</div></div>}</>
}

export function ChatbotPage() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([])
  const sessionMutation = useMutation({ mutationFn: chatbotService.createSession })
  const send = useMutation({ mutationFn: async (content: string) => {
    const session = sessionMutation.data ?? await sessionMutation.mutateAsync()
    return chatbotService.sendMessage(Number(session.id), content)
  }, onSuccess: (response) => setMessages((items) => [...items, { role: 'assistant', content: response }]) })
  const submit = (event: React.FormEvent) => { event.preventDefault(); const content = message.trim(); if (!content) return; setMessages((items) => [...items, { role: 'user', content }]); setMessage(''); send.mutate(content) }
  return <><Heading eyebrow="Assistant" title="Dayflow chatbot" text="Ask questions using the HR context currently available to the backend." /><div className="chat-panel">{messages.length === 0 && <EmptyState title="Start a conversation" message="The chatbot requires the local Ollama service to be running." />}{messages.map((item, index) => <div className={`chat-message chat-${item.role}`} key={`${item.role}-${index}`}><strong>{item.role === 'user' ? 'You' : 'Dayflow'}</strong><p>{item.content}</p></div>)}{send.isError && <ErrorState message={(send.error as Error).message} />}<form className="chat-compose" onSubmit={submit}><input value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Ask about your HR data" /><button className="button button-primary" disabled={send.isPending}><Send size={15} />{send.isPending ? 'Thinking' : 'Send'}</button></form></div></>
}

function Heading({ eyebrow, title, text }: { eyebrow: string; title: string; text: string }) { return <div className="page-heading"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p>{text}</p></div></div> }
function Unavailable({ title, message }: { title: string; message: string }) { return <><Heading eyebrow="Unavailable" title={title} text={message} /><EmptyState title="Not connected yet" message={message} /></> }
function Field({ name, label, type = 'text' }: { name: string; label: string; type?: string }) { return <label className="field"><span>{label}</span><input required name={name} type={type} /></label> }
