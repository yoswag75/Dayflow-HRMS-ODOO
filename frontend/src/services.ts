import { attendance, changeRequests, demoSessions, employees, leaveRequests } from './mockData'
import { ApiError, type AttendanceRecord, type ChangeRequest, type Employee, type LeaveRequest, type Session } from './types'

const wait = (ms = 420) => new Promise((resolve) => window.setTimeout(resolve, ms))
const clone = <T,>(value: T): T => structuredClone(value)

async function simulate<T>(factory: () => T, ms?: number): Promise<T> {
  await wait(ms)
  if (sessionStorage.getItem('dayflow:force-error') === 'true') {
    throw new ApiError(503, 'The mock service is temporarily unavailable.')
  }
  return clone(factory())
}

let employeeStore = clone(employees)
let attendanceStore = clone(attendance)
let leaveStore = clone(leaveRequests)
let changeRequestStore = clone(changeRequests)

export const authService = {
  login: async (loginId: string, password: string): Promise<Session> => {
    await wait(520)
    const fixture = demoSessions[loginId.toUpperCase()]
    if (!fixture || fixture.password !== password) throw new ApiError(401, 'The login ID or password is incorrect.')
    return clone(fixture.session)
  },
  changePassword: async (session: Session, password: string): Promise<Session> => {
    await wait()
    if (password.length < 10) throw new ApiError(422, 'Use at least 10 characters.', { password: 'Use at least 10 characters.' })
    return { ...session, mustChangePassword: false, token: `${session.token}-changed` }
  },
}

export const employeeService = {
  list: () => simulate(() => employeeStore),
  get: (id: number) => simulate(() => {
    const employee = employeeStore.find((item) => item.id === id)
    if (!employee) throw new ApiError(404, 'Employee not found.')
    return employee
  }),
  create: (input: Omit<Employee, 'id' | 'userId' | 'status' | 'about' | 'skills'>) => simulate(() => {
    const nextId = Math.max(...employeeStore.map((item) => item.id)) + 1
    const employee: Employee = { ...input, id: nextId, userId: nextId, status: 'absent', about: '', skills: [] }
    employeeStore = [employee, ...employeeStore]
    return employee
  }, 560),
  update: (id: number, updates: Partial<Employee>) => simulate(() => {
    const index = employeeStore.findIndex((item) => item.id === id)
    if (index < 0) throw new ApiError(404, 'Employee not found.')
    employeeStore[index] = { ...employeeStore[index], ...updates }
    return employeeStore[index]
  }),
  changes: () => simulate(() => changeRequestStore),
  resolveChange: (id: number, status: 'approved' | 'rejected') => simulate(() => {
    changeRequestStore = changeRequestStore.map((item) => item.id === id ? { ...item, status } : item)
    return changeRequestStore.find((item) => item.id === id)!
  }),
}

export const attendanceService = {
  list: (employeeId?: number) => simulate(() => employeeId ? attendanceStore.filter((item) => item.employeeId === employeeId) : attendanceStore),
  checkIn: (employee: Employee) => simulate(() => {
    const record: AttendanceRecord = { id: Date.now(), employeeId: employee.id, employeeName: employee.name, date: '2026-08-22', checkIn: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), checkOut: null, workHours: 0, status: 'present' }
    attendanceStore = [record, ...attendanceStore.filter((item) => !(item.employeeId === employee.id && item.date === record.date))]
    return record
  }),
  checkOut: (employeeId: number) => simulate(() => {
    const index = attendanceStore.findIndex((item) => item.employeeId === employeeId && item.date === '2026-08-22')
    if (index < 0 || !attendanceStore[index].checkIn) throw new ApiError(409, 'Check in before checking out.')
    attendanceStore[index] = { ...attendanceStore[index], checkOut: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), workHours: 8.1 }
    return attendanceStore[index]
  }),
}

export const leaveService = {
  list: (employeeId?: number) => simulate(() => employeeId ? leaveStore.filter((item) => item.employeeId === employeeId) : leaveStore),
  apply: (input: Omit<LeaveRequest, 'id' | 'status'>) => simulate(() => {
    const request: LeaveRequest = { ...input, id: Date.now(), status: input.type === 'emergency' ? 'provisional' : 'pending' }
    leaveStore = [request, ...leaveStore]
    return request
  }, 560),
  resolve: (id: number, status: 'approved' | 'rejected') => simulate(() => {
    leaveStore = leaveStore.map((item) => item.id === id ? { ...item, status } : item)
    return leaveStore.find((item) => item.id === id)!
  }),
}
