import axios from "axios";

const API_BASE = "/api";

const client = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

// Attach token from localStorage to requests
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // Let the runtime set multipart boundary for FormData (AxiosHeaders-safe)
  if (config.data instanceof FormData && config.headers) {
    if (typeof config.headers.delete === "function") {
      config.headers.delete("Content-Type");
    } else {
      delete config.headers["Content-Type"];
    }
  }
  return config;
});

// Handle 401 - clear token and redirect to login
client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  },
);

export const authApi = {
  register: (data) => client.post("/auth/register", data),
  login: (data) => client.post("/auth/login", data),
  logout: () => client.post("/auth/logout"),
  profile: () => client.get("/auth/profile"),
};

export const assessmentApi = {
  getQuestions: () => client.get("/assessment/questions"),
  submit: (answers) => client.post("/assessment/submit", { answers }),
  getResult: () => client.get("/assessment/result"),
};

/** FR6: student portfolio (GET /api/portfolio/me) */
export const portfolioApi = {
  getMe: () => client.get("/portfolio/me"),
};

/** FR3: student task catalog & claim */
export const tasksApi = {
  getRecommended: (limit = 20) =>
    client.get("/tasks/recommended", { params: { limit } }),
  getMyAssignments: () => client.get("/tasks/assignments/me"),
  claimTask: (taskId) => client.post(`/tasks/${taskId}/claim`),
};

/** FR3/FR4: student assignments (read) */
export const assignmentsApi = {
  list: () => client.get("/assignments"),
  get: (assignmentId) => client.get(`/assignments/${assignmentId}`),
};

/** FR4: submissions */
export const submissionsApi = {
  submitWriting: (body) => client.post("/submissions/writing", body),
  submitProgramming: (body) => client.post("/submissions/programming", body),
  submitDesign: (assignmentId, file, studentNotes) => {
    const fd = new FormData();
    fd.append("assignment_id", assignmentId);
    fd.append("file", file);
    if (studentNotes) fd.append("student_notes", studentNotes);
    return client.post("/submissions/design", fd);
  },
  get: (submissionId) => client.get(`/submissions/${submissionId}`),
  getLatestForAssignment: (assignmentId) =>
    client.get(`/submissions/assignment/${assignmentId}/latest`),
};

/** FR5: mentor */
export const mentorApi = {
  getStudents: () => client.get("/mentor/students"),
  getPendingSubmissions: (limit = 50) =>
    client.get("/mentor/submissions/pending", { params: { limit } }),
  getFeedbackHistory: (params) => client.get("/mentor/reviews/history", { params }),
  getStudentProgress: (studentId) =>
    client.get(`/mentor/students/${studentId}/progress`),
  getSubmission: (submissionId) => client.get(`/mentor/submissions/${submissionId}`),
  submitFeedback: (submissionId, feedback) =>
    client.post(`/mentor/submissions/${submissionId}/feedback`, { feedback }),
};

/** FR8: admin panel */
export const adminApi = {
  getOverview: () => client.get("/admin/overview"),
  getReportsSummary: () => client.get("/admin/reports/summary"),
  listUsers: (params) => client.get("/admin/users", { params }),
  getUser: (id) => client.get(`/admin/users/${id}`),
  patchUser: (id, body) => client.patch(`/admin/users/${id}`, body),
  listRoster: (params) => client.get("/admin/roster", { params }),
  createRoster: (body) => client.post("/admin/roster", body),
  patchRoster: (id, body) => client.patch(`/admin/roster/${id}`, body),
  listTasks: (params) => client.get("/admin/tasks", { params }),
  createTask: (body) => client.post("/admin/tasks", body),
  patchTask: (id, body) => client.patch(`/admin/tasks/${id}`, body),
  listSubmissions: (params) => client.get("/admin/submissions", { params }),
  getSubmission: (id) => client.get(`/admin/submissions/${id}`),
};

export default client;
