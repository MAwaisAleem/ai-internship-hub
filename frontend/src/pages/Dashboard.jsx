import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import DashboardLayout from "../components/layout/DashboardLayout";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Badge from "../components/ui/Badge";

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good Morning";
  if (h < 17) return "Good Afternoon";
  return "Good Evening";
}

export default function Dashboard() {
  const { user } = useAuth();
  const name = user?.name || user?.email || "User";
  const title = `${getGreeting()}, ${name.split(" ")[0] || name}!`;
  const subtitle = "Track your progress and grow your freelancing skills.";

  return (
    <DashboardLayout title={title} subtitle={subtitle}>
      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold text-content mb-1">Essentials</h2>
        <Card>
          <div className="flex items-center justify-between gap-2 mb-2">
            <h3 className="text-lg font-semibold text-content">Dashboard</h3>
            <Badge active>{user?.role}</Badge>
          </div>
          <p className="text-sm text-contentSecondary mb-2">
            Role: <strong>{user?.role}</strong>
          </p>

          {user?.role === "Student" && (
            <>
              <p className="text-sm text-contentSecondary mb-2">
                Take the skill assessment to get your recommended freelancing
                domain.
              </p>
              <div className="flex items-center gap-3 mt-3 flex-wrap">
                <Link to="/portfolio">
                  <Button>My portfolio</Button>
                </Link>
                <Link to="/tasks">
                  <Button variant="secondary">Browse Tasks</Button>
                </Link>
                <Link to="/tasks/my">
                  <Button variant="secondary">My Assignments</Button>
                </Link>
                <Link to="/analytics">
                  <Button variant="secondary">Analytics</Button>
                </Link>
                <Link to="/assessment">
                  <Button variant="secondary">Start Assessment</Button>
                </Link>
                <Link
                  to="/result"
                  className="text-sm text-mint-active no-underline hover:underline"
                >
                  View Last Result
                </Link>
              </div>
            </>
          )}

          {user?.role === "Mentor" && (
            <div className="flex flex-wrap items-center gap-3 mt-3">
              <Link to="/mentor">
                <Button variant="secondary">Mentor dashboard</Button>
              </Link>
              <Link to="/mentor/analytics">
                <Button variant="secondary">Mentor analytics</Button>
              </Link>
            </div>
          )}

          {user?.role === "Administrator" && (
            <div className="flex flex-wrap items-center gap-3 mt-3">
              <Link to="/admin/analytics">
                <Button variant="secondary">Platform analytics</Button>
              </Link>
            </div>
          )}
        </Card>
      </section>
    </DashboardLayout>
  );
}
