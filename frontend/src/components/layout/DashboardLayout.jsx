import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: '⌂' },
  { path: '/mentor', label: 'Mentor', icon: '◆', roles: ['Mentor'] },
  { path: '/tasks', label: 'Tasks', icon: '▤', roles: ['Student'] },
  { path: '/portfolio', label: 'Portfolio', icon: '◈', roles: ['Student'] },
  { path: '/assessment', label: 'Assessment', icon: '◇', roles: ['Student'] },
  { path: '/result', label: 'Result', icon: '▣', roles: ['Student'] },
]

export default function DashboardLayout({ children, title, subtitle, showSearch = true }) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchValue, setSearchValue] = useState('')

  const visibleNavItems = navItems.filter(
    (item) => !item.roles || item.roles.includes(user?.role)
  )

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen">
      <aside
        className={`fixed left-0 top-0 bottom-0 z-[100] flex w-sidebar min-w-sidebar flex-col bg-mint transition-transform duration-200 ease-out max-md:-translate-x-full ${
          sidebarOpen ? 'max-md:translate-x-0' : ''
        }`}
      >
        <div className="flex items-center gap-2 border-b border-borderLight p-3">
          <button
            type="button"
            className="hidden bg-transparent border-0 text-lg text-content p-1 max-md:block"
            onClick={() => setSidebarOpen((o) => !o)}
            aria-label="Toggle menu"
          >
            ☰
          </button>
          <span className="text-base font-semibold text-content">Menu</span>
        </div>
        <nav className="flex flex-1 flex-col gap-1 p-2">
          {visibleNavItems.map((item) => {
            const isActive =
              location.pathname === item.path ||
              (item.path === '/tasks' && location.pathname.startsWith('/tasks')) ||
              (item.path === '/portfolio' && location.pathname.startsWith('/portfolio')) ||
              (item.path === '/mentor' && location.pathname.startsWith('/mentor'))
            return (
              <Link
                key={`${item.path}-${item.label}`}
                to={item.path}
                className={`flex items-center gap-2 rounded-card px-3 py-2 text-sm font-medium no-underline transition-colors duration-150 ${
                  isActive
                    ? 'bg-mint-active text-onMint'
                    : 'text-contentSecondary hover:bg-white/40 hover:text-content'
                }`}
                onClick={() => setSidebarOpen(false)}
              >
                <span className="text-lg opacity-90">{item.icon}</span>
                {item.label}
              </Link>
            )
          })}
        </nav>
        <div className="border-t border-borderLight p-2">
          <button
            type="button"
            className="flex w-full items-center justify-start gap-2 rounded-card bg-transparent border-0 px-3 py-2 text-left text-sm font-medium text-contentSecondary cursor-pointer hover:bg-white/40 hover:text-content"
            onClick={handleLogout}
          >
            <span className="text-lg opacity-90">⎋</span>
            Log out
          </button>
        </div>
      </aside>

      <div className="flex flex-1 min-w-0 ml-[220px] max-md:ml-0">
        <main className="flex-1 min-h-screen p-4 bg-main">
          <header className="flex flex-wrap justify-between items-start gap-3 mb-4">
            <div>
              <h1 className="text-2xl font-bold text-content mb-1">{title}</h1>
              {subtitle && <p className="text-sm text-contentSecondary">{subtitle}</p>}
            </div>
            {showSearch && (
              <div className="flex items-center bg-card border border-borderInput rounded-card py-2 px-3 min-w-[240px] max-md:min-w-0 shadow-soft">
                <span className="text-lg text-contentMuted mr-2">⌕</span>
                <input
                  type="text"
                  placeholder="Search any keyword"
                  value={searchValue}
                  onChange={(e) => setSearchValue(e.target.value)}
                  className="flex-1 border-0 bg-transparent text-sm text-content placeholder:text-contentMuted focus:outline-none"
                />
              </div>
            )}
          </header>
          <div className="flex flex-col gap-4">{children}</div>
        </main>

        <aside className="hidden lg:flex w-sidebar-right min-w-sidebar-right flex-col gap-3 bg-mint p-4">
          <div className="bg-card rounded-card shadow-card border border-borderLight p-4">
            <div className="text-center">
              <div className="w-16 h-16 rounded-full bg-mint-active text-onMint flex items-center justify-center text-xl font-bold mx-auto mb-2">
                {(user?.name || user?.email || '?').charAt(0).toUpperCase()}
              </div>
              <div className="font-semibold text-content mb-1">{user?.name || user?.email}</div>
              <div className="text-xs text-contentSecondary mb-2">{user?.email}</div>
            </div>
          </div>
          <div className="bg-card rounded-card shadow-card border border-borderLight p-4">
            <h3 className="text-sm font-semibold text-content mb-2">Quick actions</h3>
            {user?.role === 'Student' && (
              <div className="flex flex-col gap-2">
                <Link to="/tasks" className="text-sm text-mint-active no-underline hover:underline">
                  Recommended Tasks
                </Link>
                <Link to="/portfolio" className="text-sm text-mint-active no-underline hover:underline">
                  My portfolio
                </Link>
                <Link to="/assessment" className="text-sm text-mint-active no-underline hover:underline">
                  Start Assessment
                </Link>
                <Link to="/tasks" className="text-sm text-mint-active no-underline hover:underline">
                  My tasks
                </Link>
                <Link to="/result" className="text-sm text-mint-active no-underline hover:underline">
                  View Last Result
                </Link>
              </div>
            )}
            {user?.role === 'Mentor' && (
              <div className="flex flex-col gap-2">
                <Link to="/mentor" className="text-sm text-mint-active no-underline hover:underline">
                  Mentor dashboard
                </Link>
                <Link
                  to="/mentor?tab=pending"
                  className="text-sm text-mint-active no-underline hover:underline"
                >
                  Pending reviews
                </Link>
              </div>
            )}
          </div>
        </aside>
      </div>

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-[99] bg-black/30 hidden max-md:block"
          onClick={() => setSidebarOpen(false)}
          aria-hidden
        />
      )}
    </div>
  )
}
