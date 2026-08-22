export type UserRole = 'employee' | 'hr' | 'admin'

export interface Session {
  token: string
  userId: number
  employeeId: number
  name: string
  loginId: string
  role: UserRole
  mustChangePassword: boolean
}

export type AttendanceStatus = 'present' | 'absent' | 'half_day' | 'leave'
export type LeaveStatus = 'pending' | 'provisional' | 'approved' | 'rejected'

export interface Employee {
  id: number
  userId: number
  name: string
  loginId: string
  email: string
  phone: string
  department: string
  designation: string
  manager: string
  location: string
  status: AttendanceStatus
  about: string
  skills: string[]
  joinedOn: string
}

export interface AttendanceRecord {
  id: number
  employeeId: number
  employeeName: string
  date: string
  checkIn: string | null
  checkOut: string | null
  workHours: number
  status: AttendanceStatus
}

export interface LeaveRequest {
  id: number
  employeeId: number
  employeeName: string
  type: 'paid' | 'sick' | 'unpaid' | 'emergency'
  startDate: string
  endDate: string
  remarks: string
  status: LeaveStatus
}

export interface ChangeRequest {
  id: number
  employeeId: number
  employeeName: string
  field: string
  oldValue: string
  newValue: string
  reason: string
  status: 'pending' | 'approved' | 'rejected'
}

export interface ApiErrorShape {
  status: number
  message: string
  fieldErrors?: Record<string, string>
}

export class ApiError extends Error implements ApiErrorShape {
  status: number
  fieldErrors?: Record<string, string>

  constructor(status: number, message: string, fieldErrors?: Record<string, string>) {
    super(message)
    this.status = status
    this.fieldErrors = fieldErrors
  }
}
