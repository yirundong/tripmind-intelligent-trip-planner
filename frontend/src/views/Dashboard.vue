<template>
  <div>
    <div class="page-toolbar">
      <div>
        <div class="page-kicker">DASHBOARD</div>
        <h1 class="page-title-modern">旅行工作台</h1>
        <p class="page-description">查看最近行程、收藏数据和下一次规划入口。</p>
      </div>
      <a-space>
        <RouterLink to="/">
          <a-button type="primary" size="large">创建新行程</a-button>
        </RouterLink>
        <RouterLink to="/explore">
          <a-button size="large">探索目的地</a-button>
        </RouterLink>
      </a-space>
    </div>

    <a-spin :spinning="loading">
      <div class="metric-grid">
        <div class="metric-card">
          <div class="metric-label">已保存行程</div>
          <div class="metric-value">{{ stats?.trip_count || 0 }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">收藏地点</div>
          <div class="metric-value">{{ stats?.favorite_count || 0 }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">探索城市</div>
          <div class="metric-value">{{ stats?.city_count || 0 }}</div>
        </div>
      </div>

      <div class="content-panel">
        <h2 class="section-title-modern">最近行程</h2>
        <div v-if="stats?.latest_trips.length" class="trip-grid">
          <RouterLink v-for="trip in stats.latest_trips" :key="trip.id" class="trip-card" :to="`/trips/${trip.id}`">
            <div class="trip-card-title">{{ trip.title }}</div>
            <div class="trip-card-meta">
              <div>{{ trip.city }} · {{ trip.travel_days }}天</div>
              <div>{{ trip.start_date }} 至 {{ trip.end_date }}</div>
              <span class="status-pill">{{ statusText(trip.status) }}</span>
            </div>
          </RouterLink>
        </div>
        <div v-else class="empty-state">还没有保存的行程，先创建一份新的旅行计划吧。</div>
      </div>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { message } from 'ant-design-vue'
import { fetchDashboard } from '@/services/api'
import type { DashboardStats } from '@/types'

const loading = ref(false)
const stats = ref<DashboardStats | null>(null)

const statusText = (status: string) => {
  const map: Record<string, string> = { saved: '已保存', draft: '草稿', archived: '归档' }
  return map[status] || status
}

onMounted(async () => {
  loading.value = true
  try {
    stats.value = await fetchDashboard()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '仪表盘加载失败')
  } finally {
    loading.value = false
  }
})
</script>
