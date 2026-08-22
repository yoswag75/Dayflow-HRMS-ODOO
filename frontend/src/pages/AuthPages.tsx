import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { Eye, EyeOff, LockKeyhole } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { roleLanding, useAuth } from '../auth'
import { InlineLoader } from '../components/Status'
import { ApiError } from '../types'

const loginSchema = z.object({ loginId: z.string().trim().min(1, 'Enter your login ID.'), password: z.string().min(1, 'Enter your password.') })
type LoginValues = z.infer<typeof loginSchema>

export function LoginPage() {
  const { session, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [visible, setVisible] = useState(false)
  const [serverError, setServerError] = useState('')
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginValues>({ resolver: zodResolver(loginSchema), defaultValues: { loginId: '', password: '' } })

  if (session) return <Navigate to={session.mustChangePassword ? '/change-password' : roleLanding(session)} replace />

  const submit = handleSubmit(async (values) => {
    setServerError('')
    try {
      const next = await login(values.loginId, values.password)
      const returnTo = new URLSearchParams(location.search).get('returnTo')
      navigate(next.mustChangePassword ? '/change-password' : returnTo || roleLanding(next), { replace: true })
    } catch (error) {
      setServerError(error instanceof ApiError ? error.message : 'Unable to sign in right now.')
    }
  })

  return (
    <div className="auth-page">
      <form className="auth-panel" onSubmit={submit} noValidate>
        <div className="auth-heading"><LockKeyhole size={20} aria-hidden="true" /><div><h1>Sign in</h1><p>Use your issued login ID to continue.</p></div></div>
        {serverError && <div className="form-alert" role="alert">{serverError}</div>}
        <label className="field"><span>Login ID</span><input autoComplete="username" autoFocus {...register('loginId')} aria-invalid={!!errors.loginId} />{errors.loginId && <small role="alert">{errors.loginId.message}</small>}</label>
        <label className="field"><span>Password</span><div className="password-field"><input type={visible ? 'text' : 'password'} autoComplete="current-password" {...register('password')} aria-invalid={!!errors.password} /><button type="button" aria-label={visible ? 'Hide password' : 'Show password'} onClick={() => setVisible((value) => !value)}>{visible ? <EyeOff /> : <Eye />}</button></div>{errors.password && <small role="alert">{errors.password.message}</small>}</label>
        <button className="button button-primary button-block" disabled={isSubmitting}>{isSubmitting ? <InlineLoader label="Signing in" /> : 'Sign in'}</button>
      </form>
    </div>
  )
}

const passwordSchema = z.object({ password: z.string().min(10, 'Use at least 10 characters.'), confirm: z.string() }).refine((value) => value.password === value.confirm, { path: ['confirm'], message: 'Passwords do not match.' })
type PasswordValues = z.infer<typeof passwordSchema>

export function ChangePasswordPage() {
  const { session, changePassword } = useAuth()
  const navigate = useNavigate()
  const [serverError, setServerError] = useState('')
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<PasswordValues>({ resolver: zodResolver(passwordSchema) })

  if (!session) return <Navigate to="/login" replace />
  if (!session.mustChangePassword) return <Navigate to={roleLanding(session)} replace />

  const submit = handleSubmit(async ({ password }) => {
    try {
      await changePassword(password)
      navigate(roleLanding({ ...session, mustChangePassword: false }), { replace: true })
    } catch (error) {
      setServerError(error instanceof ApiError ? error.message : 'Unable to update your password.')
    }
  })

  return <div className="auth-page"><form className="auth-panel" onSubmit={submit}><div className="auth-heading"><LockKeyhole size={20} /><div><h1>Choose a new password</h1><p>Your temporary password must be replaced.</p></div></div>{serverError && <div className="form-alert" role="alert">{serverError}</div>}<label className="field"><span>New password</span><input type="password" autoComplete="new-password" {...register('password')} />{errors.password && <small>{errors.password.message}</small>}</label><label className="field"><span>Confirm password</span><input type="password" autoComplete="new-password" {...register('confirm')} />{errors.confirm && <small>{errors.confirm.message}</small>}</label><button className="button button-primary button-block" disabled={isSubmitting}>{isSubmitting ? <InlineLoader label="Updating" /> : 'Update password'}</button></form></div>
}

export function ForbiddenPage() { return <SystemPage code="403" title="This page is restricted" message="Your account does not have permission to view this area." /> }
export function NotFoundPage() { return <SystemPage code="404" title="Page not found" message="The address may be outdated or the page may have moved." /> }

function SystemPage({ code, title, message }: { code: string; title: string; message: string }) {
  return <div className="system-page"><span>{code}</span><h1>{title}</h1><p>{message}</p><Link className="button button-primary" to="/">Return to your workspace</Link></div>
}
