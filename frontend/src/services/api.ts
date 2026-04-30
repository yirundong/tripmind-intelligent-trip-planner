import axios from 'axios'
import type {
  DashboardStats,
  FavoritePlace,
  AdminStats,
  AdminTaskSummary,
  AdminUserSummary,
  RouteRequest,
  RouteResponse,
  SavedTripDetail,
  SavedTripSummary,
  TokenResponse,
  TripFormData,
  TripPlan,
  TripPlanTask,
  UserProfile
} from '@/types'

// 为空时走 Vite 开发代理；部署时通过 VITE_API_BASE_URL 指向后端服务。
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const TOKEN_KEY = 'tripPlannerToken'
const USER_KEY = 'tripPlannerUser'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('响应错误:', error.response?.status, error.message)
    return Promise.reject(error)
  }
)

export function getToken(): string {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function getStoredUser(): UserProfile | null {
  const user = localStorage.getItem(USER_KEY)
  return user ? JSON.parse(user) : null
}

export function setAuthSession(payload: TokenResponse) {
  localStorage.setItem(TOKEN_KEY, payload.access_token)
  localStorage.setItem(USER_KEY, JSON.stringify(payload.user))
}

export function clearAuthSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export async function registerUser(data: { email: string; username: string; password: string }): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/api/auth/register', data)
  setAuthSession(response.data)
  return response.data
}

export async function loginUser(data: { identity: string; password: string }): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/api/auth/login', data)
  setAuthSession(response.data)
  return response.data
}

export async function fetchMe(): Promise<UserProfile> {
  const response = await apiClient.get<UserProfile>('/api/auth/me')
  localStorage.setItem(USER_KEY, JSON.stringify(response.data))
  return response.data
}

export async function updateMe(data: Partial<UserProfile>): Promise<UserProfile> {
  const response = await apiClient.put<UserProfile>('/api/auth/me', data)
  localStorage.setItem(USER_KEY, JSON.stringify(response.data))
  return response.data
}

export async function createTripPlanTask(formData: TripFormData): Promise<TripPlanTask> {
  const response = await apiClient.post<TripPlanTask>('/api/trip/tasks', formData)
  return response.data
}

export async function fetchTripPlanTask(taskId: number): Promise<TripPlanTask> {
  const response = await apiClient.get<TripPlanTask>(`/api/trip/tasks/${taskId}`)
  return response.data
}

export async function fetchDashboard(): Promise<DashboardStats> {
  const response = await apiClient.get<DashboardStats>('/api/dashboard')
  return response.data
}

export async function fetchTrips(params?: { city?: string; status?: string }): Promise<SavedTripSummary[]> {
  const response = await apiClient.get<SavedTripSummary[]>('/api/trips', { params })
  return response.data
}

export async function fetchTrip(id: number): Promise<SavedTripDetail> {
  const response = await apiClient.get<SavedTripDetail>(`/api/trips/${id}`)
  return response.data
}

export async function updateTrip(id: number, data: { title?: string; status?: string; notes?: string; plan_data?: TripPlan }): Promise<SavedTripDetail> {
  const response = await apiClient.put<SavedTripDetail>(`/api/trips/${id}`, data)
  return response.data
}

export async function duplicateTrip(id: number): Promise<SavedTripDetail> {
  const response = await apiClient.post<SavedTripDetail>(`/api/trips/${id}/duplicate`)
  return response.data
}

export async function deleteTrip(id: number): Promise<void> {
  await apiClient.delete(`/api/trips/${id}`)
}

export async function fetchFavorites(): Promise<FavoritePlace[]> {
  const response = await apiClient.get<FavoritePlace[]>('/api/favorites')
  return response.data
}

export async function createFavorite(data: Omit<FavoritePlace, 'id' | 'created_at'>): Promise<FavoritePlace> {
  const response = await apiClient.post<FavoritePlace>('/api/favorites', data)
  return response.data
}

export async function deleteFavorite(id: number): Promise<void> {
  await apiClient.delete(`/api/favorites/${id}`)
}

export async function planRoute(data: RouteRequest): Promise<RouteResponse> {
  const response = await apiClient.post<RouteResponse>('/api/map/route', data)
  return response.data
}

export async function fetchAdminStats(): Promise<AdminStats> {
  const response = await apiClient.get<AdminStats>('/api/admin/stats')
  return response.data
}

export async function fetchAdminTasks(params?: { status?: string; limit?: number }): Promise<AdminTaskSummary[]> {
  const response = await apiClient.get<AdminTaskSummary[]>('/api/admin/tasks', { params })
  return response.data
}

export async function fetchAdminUsers(params?: { limit?: number }): Promise<AdminUserSummary[]> {
  const response = await apiClient.get<AdminUserSummary[]>('/api/admin/users', { params })
  return response.data
}

export async function updateAdminUserRole(userId: number, isAdmin: boolean): Promise<AdminUserSummary> {
  const response = await apiClient.patch<AdminUserSummary>(`/api/admin/users/${userId}/role`, { is_admin: isAdmin })
  return response.data
}

/**
 * 健康检查
 */
export async function healthCheck(): Promise<any> {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error: any) {
    console.error('健康检查失败:', error)
    throw new Error(error.message || '健康检查失败')
  }
}

export default apiClient
