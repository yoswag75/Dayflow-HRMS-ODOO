import type { AttendanceRecord, ChangeRequest, Employee, LeaveRequest, Session } from './types'

export const demoSessions: Record<string, { password: string; session: Session }> = {
  HRDEMO001: {
    password: 'Dayflow123!',
    session: { token: 'mock-hr-token', userId: 1, employeeId: 1, name: 'Mira Patel', loginId: 'HRDEMO001', role: 'hr', mustChangePassword: false },
  },
  EMPDEMO001: {
    password: 'Dayflow123!',
    session: { token: 'mock-employee-token', userId: 2, employeeId: 2, name: 'Ava Rao', loginId: 'EMPDEMO001', role: 'employee', mustChangePassword: false },
  },
  NEWEMP001: {
    password: 'Dayflow123!',
    session: { token: 'mock-new-token', userId: 5, employeeId: 5, name: 'Noah Bose', loginId: 'NEWEMP001', role: 'employee', mustChangePassword: true },
  },
}

export const employees: Employee[] = [
  { id: 1, userId: 1, name: 'Mira Patel', loginId: 'HRDEMO001', email: 'mira@dayflow.local', phone: '+91 98765 20001', department: 'People', designation: 'HR Lead', manager: '—', location: 'Mumbai', status: 'present', about: 'Building dependable people systems.', skills: ['Hiring', 'Policy', 'Coaching'], joinedOn: '2022-04-11' },
  { id: 2, userId: 2, name: 'Ava Rao', loginId: 'EMPDEMO001', email: 'ava@dayflow.local', phone: '+91 98765 20002', department: 'Design', designation: 'Product Designer', manager: 'Mira Patel', location: 'Bengaluru', status: 'present', about: 'Designing calm, useful workplace tools.', skills: ['Research', 'Prototyping', 'Systems'], joinedOn: '2024-01-15' },
  { id: 3, userId: 3, name: 'Dev Shah', loginId: 'ENGDEMO003', email: 'dev@dayflow.local', phone: '+91 98765 20003', department: 'Engineering', designation: 'Backend Engineer', manager: 'Ishaan Mehta', location: 'Pune', status: 'leave', about: 'Working on resilient APIs and data systems.', skills: ['Python', 'PostgreSQL', 'FastAPI'], joinedOn: '2023-08-21' },
  { id: 4, userId: 4, name: 'Sara Khan', loginId: 'OPSDEMO004', email: 'sara@dayflow.local', phone: '+91 98765 20004', department: 'Operations', designation: 'Operations Analyst', manager: 'Mira Patel', location: 'Delhi', status: 'half_day', about: 'Turning complex operations into clear routines.', skills: ['Planning', 'Analytics', 'Process'], joinedOn: '2025-02-03' },
  { id: 5, userId: 5, name: 'Noah Bose', loginId: 'NEWEMP001', email: 'noah@dayflow.local', phone: '+91 98765 20005', department: 'Engineering', designation: 'Frontend Engineer', manager: 'Ishaan Mehta', location: 'Kolkata', status: 'absent', about: 'New team member.', skills: ['React', 'TypeScript'], joinedOn: '2026-08-22' },
]

export const attendance: AttendanceRecord[] = [
  { id: 1, employeeId: 1, employeeName: 'Mira Patel', date: '2026-08-22', checkIn: '09:02', checkOut: null, workHours: 0, status: 'present' },
  { id: 2, employeeId: 2, employeeName: 'Ava Rao', date: '2026-08-22', checkIn: '09:11', checkOut: null, workHours: 0, status: 'present' },
  { id: 3, employeeId: 3, employeeName: 'Dev Shah', date: '2026-08-22', checkIn: null, checkOut: null, workHours: 0, status: 'leave' },
  { id: 4, employeeId: 4, employeeName: 'Sara Khan', date: '2026-08-22', checkIn: '09:40', checkOut: '13:20', workHours: 3.7, status: 'half_day' },
]

export const leaveRequests: LeaveRequest[] = [
  { id: 1, employeeId: 2, employeeName: 'Ava Rao', type: 'paid', startDate: '2026-09-03', endDate: '2026-09-05', remarks: 'Family event', status: 'pending' },
  { id: 2, employeeId: 3, employeeName: 'Dev Shah', type: 'sick', startDate: '2026-08-22', endDate: '2026-08-22', remarks: 'Rest and recovery', status: 'approved' },
  { id: 3, employeeId: 4, employeeName: 'Sara Khan', type: 'emergency', startDate: '2026-08-25', endDate: '2026-08-25', remarks: 'Urgent appointment', status: 'provisional' },
]

export const changeRequests: ChangeRequest[] = [
  { id: 1, employeeId: 2, employeeName: 'Ava Rao', field: 'Phone', oldValue: '+91 98765 20002', newValue: '+91 99887 70012', reason: 'New primary number', status: 'pending' },
  { id: 2, employeeId: 4, employeeName: 'Sara Khan', field: 'Address', oldValue: 'South Delhi', newValue: 'Gurugram', reason: 'Moved closer to office', status: 'pending' },
]
