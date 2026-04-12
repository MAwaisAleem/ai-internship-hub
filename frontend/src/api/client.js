import axios from 'axios'

const API_BASE = '/api'

const client = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

// Attach token from localStorage to requests
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 - clear token and redirect to login
client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const authApi = {
  register: (data) => client.post('/auth/register', data),
  login: (data) => client.post('/auth/login', data),
  logout: () => client.post('/auth/logout'),
  profile: () => client.get('/auth/profile'),
}

export const assessmentApi = {
  getQuestions: () => client.get('/assessment/questions'),
  submit: (answers) => client.post('/assessment/submit', { answers }),
  getResult: () => client.get('/assessment/result'),
}

export const tasksApi = {
  getRecommended: (limit = 20) =>
    client.get('/tasks/recommended', { params: { limit } }),
  listTasks: (params) => client.get('/tasks', { params }),
  getTask: (id) => client.get(`/tasks/${id}`),
  claimTask: (id) => client.post(`/tasks/${id}/claim`),
  getMyAssignments: () => client.get('/tasks/assignments/me'),
}

export default client
