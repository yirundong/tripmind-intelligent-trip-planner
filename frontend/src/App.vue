<template>
  <div id="app" class="app-shell">
    <template v-if="isAuthPage">
      <router-view />
    </template>

    <template v-else-if="isAdminPage">
      <header class="admin-header">
        <RouterLink class="brand" to="/admin">
          <span class="brand-mark">T</span>
          <span>TripMind Admin</span>
        </RouterLink>

        <a-space>
          <span style="color: #667085">{{ userName }}</span>
          <a-button @click="logout">退出</a-button>
        </a-space>
      </header>

      <main class="app-main admin-main">
        <router-view />
      </main>
    </template>

    <template v-else>
      <header class="app-header">
        <RouterLink class="brand" to="/dashboard">
          <span class="brand-mark">T</span>
          <span>TripMind</span>
        </RouterLink>

        <nav class="app-nav">
          <RouterLink class="nav-link" to="/dashboard">工作台</RouterLink>
          <RouterLink class="nav-link" to="/">规划</RouterLink>
          <RouterLink class="nav-link" to="/trips">我的行程</RouterLink>
          <RouterLink class="nav-link" to="/favorites">收藏</RouterLink>
          <RouterLink class="nav-link" to="/explore">探索</RouterLink>
          <RouterLink class="nav-link" to="/route-planner">路线</RouterLink>
          <RouterLink class="nav-link" to="/profile">个人中心</RouterLink>
          <RouterLink v-if="isAdmin" class="nav-link" to="/admin">管理</RouterLink>
        </nav>

        <a-space>
          <span style="color: #667085">{{ userName }}</span>
          <a-button @click="logout">退出</a-button>
        </a-space>
      </header>

      <main class="app-main">
        <router-view />
      </main>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { clearAuthSession, getStoredUser } from '@/services/api'

const route = useRoute()
const router = useRouter()

const isAuthPage = computed(() => route.path === '/login' || route.path === '/register')
const isAdminPage = computed(() => route.path.startsWith('/admin'))
const userName = computed(() => {
  route.fullPath
  const user = getStoredUser()
  if (user?.is_admin) {
    return '系统管理员'
  }
  return user?.username || '旅行者'
})
const isAdmin = computed(() => {
  route.fullPath
  return Boolean(getStoredUser()?.is_admin)
})

const logout = () => {
  clearAuthSession()
  router.push('/login')
}
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif;
}
</style>
