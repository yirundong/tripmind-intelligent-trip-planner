// 类型定义

export interface Location {
  longitude: number
  latitude: number
}

export interface Attraction {
  name: string
  address: string
  location: Location
  visit_duration: number
  description: string
  category?: string
  rating?: number
  image_url?: string
  ticket_price?: number
}

export interface Meal {
  type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  name: string
  address?: string
  location?: Location
  description?: string
  estimated_cost?: number
}

export interface Hotel {
  name: string
  address: string
  location?: Location
  price_range: string
  rating: string
  distance: string
  type: string
  estimated_cost?: number
}

export interface Budget {
  total_attractions: number
  total_hotels: number
  total_meals: number
  total_transportation: number
  total: number
}

export interface DayPlan {
  date: string
  day_index: number
  description: string
  transportation: string
  accommodation: string
  hotel?: Hotel
  attractions: Attraction[]
  meals: Meal[]
}

export interface WeatherInfo {
  date: string
  day_weather: string
  night_weather: string
  day_temp: number
  night_temp: number
  wind_direction: string
  wind_power: string
}

export interface TripPlan {
  city: string
  start_date: string
  end_date: string
  days: DayPlan[]
  weather_info: WeatherInfo[]
  overall_suggestions: string
  budget?: Budget
}

export interface TripFormData {
  city: string
  start_date: string
  end_date: string
  travel_days: number
  attractions_per_day: number
  transportation: string
  accommodation: string
  preferences: string[]
  free_text_input: string
}

export interface TripPlanResponse {
  success: boolean
  message: string
  data?: TripPlan
  trip_id?: number
}

export interface TripPlanTask {
  id: number
  status: 'queued' | 'running' | 'succeeded' | 'failed' | string
  progress: number
  stage: string
  city: string
  trip_id?: number
  error_message: string
  created_at: string
  updated_at: string
}

export interface UserProfile {
  id: number
  email: string
  username: string
  avatar_url: string
  default_city: string
  default_transportation: string
  default_accommodation: string
  default_preferences: string[]
  is_admin: boolean
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: UserProfile
}

export interface SavedTripSummary {
  id: number
  title: string
  city: string
  start_date: string
  end_date: string
  travel_days: number
  status: string
  notes: string
  created_at: string
  updated_at: string
}

export interface SavedTripDetail extends SavedTripSummary {
  request_data: Record<string, any>
  plan_data: TripPlan
}

export interface FavoritePlace {
  id: number
  name: string
  city: string
  address: string
  category: string
  longitude: string
  latitude: string
  notes: string
  created_at: string
}

export interface DashboardStats {
  trip_count: number
  favorite_count: number
  city_count: number
  latest_trips: SavedTripSummary[]
}

export interface RouteRequest {
  origin_address: string
  destination_address: string
  origin_city?: string
  destination_city?: string
  route_type: 'walking' | 'driving' | 'transit' | string
}

export interface RouteInfo {
  distance: number
  duration: number
  route_type: string
  description: string
}

export interface RouteResponse {
  success: boolean
  message: string
  data?: RouteInfo
}

export interface AdminStats {
  user_count: number
  trip_count: number
  favorite_count: number
  task_count: number
  succeeded_task_count: number
  failed_task_count: number
  running_task_count: number
  success_rate: number
  avg_task_progress: number
  recent_7d_task_count: number
  popular_cities: AdminCityStat[]
}

export interface AdminCityStat {
  city: string
  count: number
}

export interface AdminTaskSummary {
  id: number
  user_id: number
  username: string
  city: string
  status: string
  progress: number
  stage: string
  trip_id?: number
  error_message: string
  created_at: string
  updated_at: string
}

export interface AdminUserSummary {
  id: number
  email: string
  username: string
  is_admin: boolean
  is_active: boolean
  trip_count: number
  created_at: string
}
