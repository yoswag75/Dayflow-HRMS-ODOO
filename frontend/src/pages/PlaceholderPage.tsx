import { Bell, Bot, Coins, FlaskConical, Sparkles } from 'lucide-react'

const details = {
  payroll: { title: 'Payroll', text: 'Salary breakdowns, upcoming changes, acknowledgements, and corrections will live here.', icon: Coins, api: 'GET /payroll/me' },
  onboarding: { title: 'Onboarding', text: 'Checklists, task progress, buddy assignments, and knowledge links will live here.', icon: Sparkles, api: 'GET /onboarding/me' },
  recognition: { title: 'Recognition', text: 'Points history, earned badges, voting, and the opt-in leaderboard will live here.', icon: Coins, api: 'GET /gamification/leaderboard' },
  simulation: { title: 'Simulation', text: 'HR will run leave and resignation impact scenarios and review history here.', icon: FlaskConical, api: 'POST /simulation/run' },
  chatbot: { title: 'Chatbot', text: 'HR will create sessions and ask workforce questions with streamed responses here.', icon: Bot, api: 'POST /chatbot/message' },
  notifications: { title: 'Notifications', text: 'In-app alerts, read state, and delivery preferences will live here.', icon: Bell, api: 'GET /notifications/me' },
} as const

export function PlaceholderPage({ page }: { page: keyof typeof details }) {
  const item = details[page]
  const Icon = item.icon
  return <><div className="page-heading"><div><p className="eyebrow">Planned module</p><h1>{item.title}</h1><p>{item.text}</p></div></div><div className="placeholder-panel"><Icon size={24} /><div><strong>Navigation is ready</strong><p>This module is intentionally a placeholder until its backend workflow and response schemas are available.</p><code>{item.api}</code></div></div></>
}
