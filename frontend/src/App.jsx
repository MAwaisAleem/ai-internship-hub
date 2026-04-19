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
import StudentAnalyticsPage from "./pages/analytics/StudentAnalyticsPage";
import MentorAnalyticsPage from "./pages/analytics/MentorAnalyticsPage";
import AdminAnalyticsPage from "./pages/analytics/AdminAnalyticsPage";

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
          path="/tasks"
          element={
            <ProtectedRoute roles={["Student"]}>
              <Tasks />
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
          path="/mentor/analytics"
          element={
            <ProtectedRoute roles={["Mentor"]}>
              <MentorAnalyticsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/analytics"
          element={
            <ProtectedRoute roles={["Administrator"]}>
              <AdminAnalyticsPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
