import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'

const ROLES = ['Student', 'Mentor', 'Administrator']

export default function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [name, setName] = useState('')
  const [role, setRole] = useState('Student')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register, login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }
    setLoading(true)
    try {
      await register(email, password, role, name || email.split('@')[0])
      await login(email, password)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-primary">
      <Card className="w-full max-w-[400px] !p-5">
        <h1 className="text-2xl font-bold text-content mb-1">Create Account</h1>
        <p className="text-sm text-contentSecondary mb-4">AI-Supported Virtual Internship Hub</p>
        {error && <div className="text-sm text-error mb-2">{error}</div>}
        <form onSubmit={handleSubmit} className="flex flex-col">
          <Input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mb-2"
            required
          />
          <Input
            type="text"
            placeholder="Name (optional)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mb-2"
          />
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full py-2 px-3 border border-borderInput rounded-md text-base bg-card text-content focus:outline-none focus:border-mint-active focus:ring-2 focus:ring-focus mb-2"
          >
            {ROLES.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mb-2"
            required
          />
          <Input
            type="password"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="mb-2"
            required
          />
          <Button type="submit" disabled={loading} className="w-full mt-2">
            {loading ? 'Registering...' : 'Register'}
          </Button>
        </form>
        <p className="text-center text-sm text-contentSecondary mt-4">
          Already have an account? <Link to="/login">Sign In</Link>
        </p>
        <p className="text-center text-sm text-contentSecondary mt-2">
          <Link to="/">← Back to Home</Link>
        </p>
      </Card>
    </div>
  )
}
