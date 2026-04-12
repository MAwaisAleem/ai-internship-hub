import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="min-h-screen bg-primary">
      <header className="flex items-center justify-between py-3 px-4 bg-gradient-to-r from-mint-active to-mint shadow-soft max-[600px]:flex-col max-[600px]:gap-2">
        <div className="flex items-center gap-2">
          <span className="text-2xl text-onMint opacity-95" aria-hidden>◆</span>
          <span className="text-xl font-bold text-onMint">AI Virtual Internship Hub</span>
        </div>
        <nav className="flex items-center gap-2">
          <Link
            to="/register"
            className="inline-flex items-center gap-1 py-2 px-3 rounded-md text-sm font-semibold no-underline transition-[filter] duration-150 bg-white/90 text-content hover:brightness-95"
          >
            <span className="text-base">👤</span>
            Register
          </Link>
          <Link
            to="/login"
            className="inline-flex items-center gap-1 py-2 px-3 rounded-md text-sm font-semibold no-underline transition-[filter] duration-150 bg-card text-content hover:brightness-[0.98]"
          >
            <span className="text-base">→</span>
            Login
          </Link>
        </nav>
      </header>

      <main className="py-6 px-4 max-w-[1200px] mx-auto">
        <section className="bg-card rounded-card shadow-card border border-borderLight p-6 text-center mb-6">
          <div className="text-5xl text-mint-active mb-3" aria-hidden>◆</div>
          <h1 className="text-2xl max-[600px]:text-xl font-bold text-content mb-2 leading-tight">
            Welcome to AI Virtual Internship Hub
          </h1>
          <p className="text-base text-contentSecondary mb-5 max-w-[480px] mx-auto">
            Discover your perfect internship path and accelerate your career growth
          </p>
          <div className="flex flex-wrap gap-3 justify-center">
            <Link
              to="/register"
              className="inline-flex items-center gap-2 py-2 px-4 rounded-md text-base font-semibold no-underline transition-[filter] duration-150 bg-mint-active text-onMint hover:brightness-105"
            >
              <span className="text-lg">👤</span>
              Register Now
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center gap-2 py-2 px-4 rounded-md text-base font-semibold no-underline transition-[filter] duration-150 bg-mint text-content hover:brightness-105"
            >
              <span className="text-lg">→</span>
              Login
            </Link>
          </div>
        </section>

        <section className="grid gap-4 grid-cols-[repeat(auto-fit,minmax(260px,1fr))]">
          <div className="bg-card rounded-card shadow-card border border-borderLight p-4 text-center">
            <div className="text-[56px] mb-2 text-mint-active" aria-hidden>📖</div>
            <h2 className="text-lg font-bold text-content mb-2">Learn</h2>
            <p className="text-sm text-contentSecondary text-center leading-normal">
              Access curated learning materials and resources tailored to your skills and career goals
            </p>
          </div>
          <div className="bg-card rounded-card shadow-card border border-borderLight p-4 text-center">
            <div className="text-[56px] mb-2 text-mint-active" aria-hidden>◎</div>
            <h2 className="text-lg font-bold text-content mb-2">Assess</h2>
            <p className="text-sm text-contentSecondary text-center leading-normal">
              Take skill assessments to identify your ideal domain and career path
            </p>
          </div>
          <div className="bg-card rounded-card shadow-card border border-borderLight p-4 text-center">
            <div className="text-[56px] mb-2 text-mint-active" aria-hidden>📈</div>
            <h2 className="text-lg font-bold text-content mb-2">Grow</h2>
            <p className="text-sm text-contentSecondary text-center leading-normal">
              Get mentorship and guidance from industry experts and experienced professionals
            </p>
          </div>
          <div className="bg-card rounded-card shadow-card border border-borderLight p-4 text-center">
            <div className="text-[56px] mb-2 text-mint-active" aria-hidden>💼</div>
            <h2 className="text-lg font-bold text-content mb-2">Internships</h2>
            <p className="text-sm text-contentSecondary text-center leading-normal">
              Explore AI-powered internship opportunities tailored to your skills and interests.
            </p>
          </div>
        </section>
      </main>
    </div>
  )
}
