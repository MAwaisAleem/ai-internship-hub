import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Assessment from "./pages/Assessment";
import Result from "./pages/Result";
import PortfolioPage from "./pages/PortfolioPage";
import Tasks from "./pages/Tasks";
import TasksPage from "./pages/TasksPage";
import TaskSubmitPage from "./pages/TaskSubmitPage";
import MentorDashboard from "./pages/MentorDashboard";
import MentorStudentDetail from "./pages/MentorStudentDetail";
import MentorReviewPage from "./pages/MentorReviewPage";
<<<<<<< HEAD
import StudentAnalyticsPage from "./pages/analytics/StudentAnalyticsPage";
import MentorAnalyticsPage from "./pages/analytics/MentorAnalyticsPage";
import AdminAnalyticsPage from "./pages/analytics/AdminAnalyticsPage";
=======
import AdminOverview from "./pages/admin/AdminOverview";
import AdminUsersPage from "./pages/admin/AdminUsersPage";
import AdminTasksPage from "./pages/admin/AdminTasksPage";
import AdminSubmissionsPage from "./pages/admin/AdminSubmissionsPage";
import AdminSubmissionDetailPage from "./pages/admin/AdminSubmissionDetailPage";
import AdminRosterPage from "./pages/admin/AdminRosterPage";
>>>>>>> a36fdcbf362d96dd9834ae691373adf330fa6c4b

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/assessment"
          element={
            <ProtectedRoute roles={["Student"]}>
              <Assessment />
            </ProtectedRoute>
          }
        />
        <Route
          path="/result"
          element={
            <ProtectedRoute roles={["Student"]}>
              <Result />
            </ProtectedRoute>
          }
        />
        <Route
          path="/portfolio"
          element={
            <ProtectedRoute roles={["Student"]}>
              <PortfolioPage />
            </ProtectedRoute>
          }
        />
        <Route
<<<<<<< HEAD
          path="/tasks"
          element={
            <ProtectedRoute roles={["Student"]}>
              <Tasks />
=======
          path="/tasks/:assignmentId/submit"
          element={
            <ProtectedRoute roles={["Student"]}>
              <TaskSubmitPage />
>>>>>>> a36fdcbf362d96dd9834ae691373adf330fa6c4b
            </ProtectedRoute>
          }
        />
        <Route
          path="/tasks/my"
          element={
            <ProtectedRoute roles={["Student"]}>
              <TasksPage />
            </ProtectedRoute>
          }
        />
        <Route
<<<<<<< HEAD
          path="/tasks/:assignmentId/submit"
          element={
            <ProtectedRoute roles={["Student"]}>
              <TaskSubmitPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute roles={["Student"]}>
              <StudentAnalyticsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/mentor"
          element={
            <ProtectedRoute roles={["Mentor"]}>
              <MentorDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/mentor/students/:studentId"
          element={
            <ProtectedRoute roles={["Mentor"]}>
              <MentorStudentDetail />
=======
          path="/tasks"
          element={
            <ProtectedRoute roles={["Student"]}>
              <Tasks />
>>>>>>> a36fdcbf362d96dd9834ae691373adf330fa6c4b
            </ProtectedRoute>
          }
        />
        <Route
          path="/mentor/submissions/:submissionId"
          element={
            <ProtectedRoute roles={["Mentor"]}>
              <MentorReviewPage />
            </ProtectedRoute>
          }
        />
        <Route
<<<<<<< HEAD
          path="/mentor/analytics"
          element={
            <ProtectedRoute roles={["Mentor"]}>
              <MentorAnalyticsPage />
=======
          path="/mentor/students/:studentId"
          element={
            <ProtectedRoute roles={["Mentor"]}>
              <MentorStudentDetail />
>>>>>>> a36fdcbf362d96dd9834ae691373adf330fa6c4b
            </ProtectedRoute>
          }
        />
        <Route
<<<<<<< HEAD
          path="/admin/analytics"
          element={
            <ProtectedRoute roles={["Administrator"]}>
              <AdminAnalyticsPage />
=======
          path="/mentor"
          element={
            <ProtectedRoute roles={["Mentor"]}>
              <MentorDashboard />
            </ProtectedRoute>
          }
        />
        <Route path="/admin" element={<Navigate to="/admin/overview" replace />} />
        <Route
          path="/admin/overview"
          element={
            <ProtectedRoute roles={["Administrator"]}>
              <AdminOverview />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <ProtectedRoute roles={["Administrator"]}>
              <AdminUsersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/tasks"
          element={
            <ProtectedRoute roles={["Administrator"]}>
              <AdminTasksPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/submissions/:submissionId"
          element={
            <ProtectedRoute roles={["Administrator"]}>
              <AdminSubmissionDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/submissions"
          element={
            <ProtectedRoute roles={["Administrator"]}>
              <AdminSubmissionsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/roster"
          element={
            <ProtectedRoute roles={["Administrator"]}>
              <AdminRosterPage />
>>>>>>> a36fdcbf362d96dd9834ae691373adf330fa6c4b
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
