import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import './styles/app.css'
import App from './App.vue'
import { getStoredUser, getToken } from '@/services/api'

const Home = () => import('./views/Home.vue')
const Result = () => import('./views/Result.vue')
const Dashboard = () => import('./views/Dashboard.vue')
const Login = () => import('./views/Login.vue')
const Register = () => import('./views/Register.vue')
const MyTrips = () => import('./views/MyTrips.vue')
const TripDetail = () => import('./views/TripDetail.vue')
const Favorites = () => import('./views/Favorites.vue')
const Explore = () => import('./views/Explore.vue')
const RoutePlanner = () => import('./views/RoutePlanner.vue')
const Profile = () => import('./views/Profile.vue')
const Admin = () => import('./views/Admin.vue')
const Forbidden = () => import('./views/Forbidden.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
      meta: { requiresAuth: true }
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: Dashboard,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'Login',
      component: Login,
      meta: { publicOnly: true }
    },
    {
      path: '/register',
      name: 'Register',
      component: Register,
      meta: { publicOnly: true }
    },
    {
      path: '/result',
      name: 'Result',
      component: Result,
      meta: { requiresAuth: true }
    },
    {
      path: '/trips',
      name: 'MyTrips',
      component: MyTrips,
      meta: { requiresAuth: true }
    },
    {
      path: '/trips/:id',
      name: 'TripDetail',
      component: TripDetail,
      meta: { requiresAuth: true }
    },
    {
      path: '/favorites',
      name: 'Favorites',
      component: Favorites,
      meta: { requiresAuth: true }
    },
    {
      path: '/explore',
      name: 'Explore',
      component: Explore,
      meta: { requiresAuth: true }
    },
    {
      path: '/route-planner',
      name: 'RoutePlanner',
      component: RoutePlanner,
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'Profile',
      component: Profile,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'Admin',
      component: Admin,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/403',
      name: 'Forbidden',
      component: Forbidden,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to) => {
  const token = getToken()
  if (to.meta.requiresAuth && !token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.meta.requiresAdmin && !getStoredUser()?.is_admin) {
    return '/403'
  }
  if (to.meta.publicOnly && token) {
    return '/dashboard'
  }
})

const app = createApp(App)

app.use(router)
app.use(Antd)

app.mount('#app')
