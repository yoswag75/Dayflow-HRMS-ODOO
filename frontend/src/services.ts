import { ApiError, type AttendanceRecord, type ChangeRequest, type Employee, type LeaderboardEntry, type LeaveRequest, type NotificationItem, type OnboardResult, type OnboardingTask, type Session, type UserRole } from './types'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '') || 'http://localhost:8000'
const SESSION_KEY = 'dayflow:session'

type JsonRecord = Record<string, unknown>

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function camelizeKey(key: string) {
  return key.replace(/_([a-z])/g, (_, letter: string) => letter.toUpperCase())
}

function snakeizeKey(key: string) {
  return key.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`)
}

function camelize(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(camelize)
  if (!isRecord(value)) return value
  return Object.fromEntries(Object.entries(value).map(([key, item]) => [camelizeKey(key), camelize(item)]))
}

function snakeize(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(snakeize)
  if (!isRecord(value)) return value
  return Object.fromEntries(Object.entries(value).map(([key, item]) => [snakeizeKey(key), snakeize(item)]))
}

function storedToken() {
  try {
    const session = JSON.parse(sessionStorage.getItem(SESSION_KEY) || 'null') as Session | null
    return session?.token
  } catch {
    return undefined
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = storedToken()
  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')
  if (init.body) headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers })
  } catch {
    throw new ApiError(0, `Cannot reach the Dayflow API at ${API_BASE_URL}.`)
  }

  const contentType = response.headers.get('content-type') || ''
  const raw = response.status === 204
    ? undefined
    : contentType.includes('application/json')
      ? await response.json()
      : await response.text()

  const payload = camelize(raw)
  if (!response.ok) {
    const details = isRecord(payload) ? payload : undefined
    const message = typeof details?.detail === 'string'
      ? details.detail
      : typeof details?.message === 'string'
        ? details.message
        : typeof payload === 'string' && payload
          ? payload
          : `The API request failed with status ${response.status}.`
    throw new ApiError(response.status, message)
  }

  return payload as T
}

function jsonRequest(method: string, value?: unknown): RequestInit {
  return { method, body: value === undefined ? undefined : JSON.stringify(snakeize(value)) }
}

function firstRecord(value: unknown, keys: string[]): JsonRecord {
  if (!isRecord(value)) return {}
  for (const key of keys) {
    if (isRecord(value[key])) return value[key]
  }
  return value
}

function listFrom<T>(value: unknown, keys: string[]): T[] {
  if (Array.isArray(value)) return value as T[]
  if (!isRecord(value)) return []
  for (const key of keys) {
    if (Array.isArray(value[key])) return value[key] as T[]
  }
  return []
}

function numberValue(...values: unknown[]) {
  const value = values.find((item) => typeof item === 'number' || (typeof item === 'string' && item.trim() !== ''))
  return value === undefined ? 0 : Number(value)
}

function textValue(...values: unknown[]) {
  const value = values.find((item) => typeof item === 'string')
  return typeof value === 'string' ? value : ''
}

function decodeJwt(token: string): JsonRecord {
  try {
    const encoded = token.split('.')[1]
    if (!encoded) return {}
    const base64 = encoded.replace(/-/g, '+').replace(/_/g, '/')
    return camelize(JSON.parse(atob(base64))) as JsonRecord
  } catch {
    return {}
  }
}

function normalizeSession(value: unknown, loginId: string): Session {
  const root = firstRecord(value, ['data'])
  const user = firstRecord(root.user, ['data'])
  const employee = firstRecord(root.employee, ['data'])
  const token = textValue(root.accessToken, root.token, root.jwt)
  const claims = decodeJwt(token)
  const role = textValue(root.role, user.role, claims.role).toLowerCase() as UserRole
  const userId = numberValue(root.userId, user.id, claims.userId, claims.sub)
  const employeeId = numberValue(root.employeeId, user.employeeId, employee.id, claims.employeeId)

  if (!token || !userId || !['employee', 'hr', 'admin'].includes(role) || (role === 'employee' && !employeeId)) {
    throw new ApiError(502, 'The login response is missing the token, role, or employee identity required by the frontend.')
  }

  return {
    token,
    userId,
    employeeId,
    name: textValue(root.name, user.name, employee.name, claims.name, loginId),
    loginId: textValue(root.loginId, user.loginId, claims.loginId, loginId),
    role,
    mustChangePassword: Boolean(root.mustChangePassword ?? root.forcePasswordChange ?? user.mustChangePassword ?? user.forcePasswordChange ?? claims.mustChangePassword ?? claims.forcePasswordChange),
  }
}

function normalizeEmployee(value: unknown): Employee {
  const item = firstRecord(value, ['employee', 'data'])
  const user = firstRecord(item.user, ['data'])
  return {
    id: numberValue(item.id),
    userId: numberValue(item.userId, user.id),
    name: textValue(item.name, user.name) || [textValue(item.firstName), textValue(item.lastName)].filter(Boolean).join(' '),
    loginId: textValue(item.loginId, user.loginId, item.email),
    email: textValue(item.email, item.workEmail, item.personalEmail, user.email),
    phone: textValue(item.phone),
    department: textValue(item.department),
    designation: textValue(item.designation),
    manager: textValue(item.manager, item.managerName),
    location: textValue(item.location, item.address),
    status: textValue(item.status, 'active').toLowerCase() as Employee['status'],
    about: textValue(item.about),
    skills: Array.isArray(item.skills) ? item.skills.map(String) : [],
    joinedOn: textValue(item.joinedOn, item.doj, item.dateOfJoining),
  }
}

function normalizeAttendance(value: unknown): AttendanceRecord {
  const item = firstRecord(value, ['attendance', 'record', 'data'])
  const employee = firstRecord(item.employee, ['data'])
  return {
    id: numberValue(item.id),
    employeeId: numberValue(item.employeeId, employee.id),
    employeeName: textValue(item.employeeName, employee.name) || `Employee #${numberValue(item.employeeId, employee.id)}`,
    date: textValue(item.date),
    checkIn: textValue(item.checkIn, item.checkInTime) || null,
    checkOut: textValue(item.checkOut, item.checkOutTime) || null,
    workHours: numberValue(item.workHours) || hoursBetween(textValue(item.checkIn), textValue(item.checkOut)),
    status: textValue(item.status).toLowerCase().replace('on_leave', 'leave') as AttendanceRecord['status'],
  }
}

function normalizeLeave(value: unknown): LeaveRequest {
  const item = firstRecord(value, ['leave', 'request', 'data'])
  const employee = firstRecord(item.employee, ['data'])
  return {
    id: numberValue(item.id),
    employeeId: numberValue(item.employeeId, employee.id),
    employeeName: textValue(item.employeeName, employee.name) || `Employee #${numberValue(item.employeeId, employee.id)}`,
    type: textValue(item.type, item.leaveType).toLowerCase() as LeaveRequest['type'],
    startDate: textValue(item.startDate),
    endDate: textValue(item.endDate),
    remarks: textValue(item.remarks, item.reason),
    status: textValue(item.status).toLowerCase() as LeaveRequest['status'],
  }
}

function hoursBetween(start: string, end: string) {
  if (!start || !end) return 0
  const milliseconds = new Date(end).getTime() - new Date(start).getTime()
  return milliseconds > 0 ? Math.round(milliseconds / 36000) / 100 : 0
}

function normalizeChange(value: unknown): ChangeRequest {
  const item = firstRecord(value, ['changeRequest', 'request', 'data'])
  const employee = firstRecord(item.employee, ['data'])
  return {
    id: numberValue(item.id),
    employeeId: numberValue(item.employeeId, item.entityId, employee.id),
    employeeName: textValue(item.employeeName, employee.name),
    field: textValue(item.field, item.fieldName),
    oldValue: textValue(item.oldValue),
    newValue: textValue(item.newValue),
    reason: textValue(item.reason),
    status: textValue(item.status).toLowerCase() as ChangeRequest['status'],
  }
}

export const authService = {
  setupStatus: async () => Boolean(firstRecord(await request('/auth/setup-status'), ['data']).required),
  setup: async (email: string, password: string) => normalizeSession(await request('/auth/setup', jsonRequest('POST', { email, password })), email),
  login: async (email: string, password: string) => {
    const payload = await request<unknown>('/auth/login', jsonRequest('POST', { email, password }))
    return normalizeSession(payload, email)
  },
  changePassword: async (session: Session, password: string) => {
    const payload = await request<unknown>('/auth/change-password', jsonRequest('POST', { password }))
    return Object.keys(firstRecord(payload, ['data'])).length
      ? normalizeSession(payload, session.loginId)
      : { ...session, mustChangePassword: false }
  },
}

export const employeeService = {
  list: async () => listFrom<unknown>(await request('/employees'), ['employees', 'items', 'data']).map(normalizeEmployee),
  get: async (id: number) => normalizeEmployee(await request(`/employees/${id}`)),
  create: async (input: Omit<Employee, 'id' | 'userId' | 'status' | 'about' | 'skills'>): Promise<OnboardResult> => {
    const [firstName, ...lastNameParts] = input.name.trim().split(/\s+/)
    const payload = await request<unknown>('/employees', jsonRequest('POST', {
      firstName,
      lastName: lastNameParts.join(' ') || '-',
      email: input.email,
      department: input.department || undefined,
      designation: input.designation || undefined,
      dateOfJoining: input.joinedOn || undefined,
    }))
    const root = firstRecord(payload, ['data'])
    return { employee: normalizeEmployee(root.employee), temporaryPassword: textValue(root.tempPassword) }
  },
  update: async (_id: number, _updates: Partial<Employee>) => { throw new ApiError(501, 'Profile editing is not available in the current backend.') },
  changes: async () => { throw new ApiError(501, 'Employee change requests are not available in the current backend.') },
  resolveChange: async (_id: number, _status: 'approved' | 'rejected') => { throw new ApiError(501, 'Employee change requests are not available in the current backend.') },
}

export const attendanceService = {
  list: async (employeeId?: number) => listFrom<unknown>(await request(employeeId ? '/attendance/me' : '/attendance'), ['attendance', 'records', 'items', 'data']).map(normalizeAttendance),
  checkIn: async (_employee: Employee) => normalizeAttendance(await request('/attendance/check-in', jsonRequest('POST'))),
  checkOut: async (_employeeId: number) => normalizeAttendance(await request('/attendance/check-out', jsonRequest('POST'))),
}

export const leaveService = {
  list: async (employeeId?: number) => listFrom<unknown>(await request(employeeId ? '/leave/me' : '/leave'), ['leaveRequests', 'requests', 'items', 'data']).map(normalizeLeave),
  apply: async (input: Omit<LeaveRequest, 'id' | 'status'>) => normalizeLeave(await request('/leave/apply', jsonRequest('POST', {
    employeeId: input.employeeId,
    leaveType: input.type.toUpperCase(),
    startDate: input.startDate,
    endDate: input.endDate,
    reason: input.remarks,
  }))),
  resolve: async (id: number, status: 'approved' | 'rejected') => normalizeLeave(await request(`/leave/${id}/${status === 'approved' ? 'approve' : 'reject'}`, jsonRequest('POST'))),
}

export const onboardingService = {
  mine: async () => listFrom<unknown>(await request('/onboarding/me'), ['items', 'data']).map((item) => {
    const record = firstRecord(item, ['data'])
    return { id: numberValue(record.id), employeeId: numberValue(record.employeeId), taskName: textValue(record.taskName), status: textValue(record.status).toLowerCase() as OnboardingTask['status'], dueDate: textValue(record.dueDate) }
  }),
  complete: async (id: number) => request(`/onboarding/tasks/${id}`, jsonRequest('PATCH')),
}

export const recognitionService = {
  leaderboard: async () => listFrom<LeaderboardEntry>(await request('/gamification/leaderboard'), ['items', 'data']),
  points: async () => listFrom<JsonRecord>(await request('/gamification/me/points'), ['items', 'data']),
  badges: async () => listFrom<JsonRecord>(await request('/gamification/me/badges'), ['items', 'data']),
}

export const notificationService = {
  list: async () => listFrom<NotificationItem>(await request('/notifications/me'), ['items', 'data']),
  markRead: async (id: number) => request(`/notifications/${id}/read`, jsonRequest('POST')),
}

export const simulationService = {
  runHeadcount: async (department: string, delta: number, averageSalary: number) => request<{ summary: string; impact: Record<string, unknown>; warnings: string[] }>('/simulation/run', jsonRequest('POST', {
    scenarioType: 'HEADCOUNT_CHANGE',
    params: { department, delta, avgSalaryForNewHires: averageSalary },
  })),
}

export const chatbotService = {
  createSession: async () => firstRecord(await request('/chatbot/session', jsonRequest('POST')), ['data']),
  sendMessage: async (sessionId: number, message: string) => request<string>('/chatbot/message', jsonRequest('POST', { sessionId, message })),
}
