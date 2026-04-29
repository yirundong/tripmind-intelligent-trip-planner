<template>
  <div>
    <div class="page-toolbar">
      <div>
        <div class="page-kicker">TRIPS</div>
        <h1 class="page-title-modern">我的行程</h1>
        <p class="page-description">管理已保存、草稿和复制出来的旅行计划。</p>
      </div>
      <RouterLink to="/">
        <a-button type="primary" size="large">新建规划</a-button>
      </RouterLink>
    </div>

    <div class="content-panel" style="margin-bottom: 16px">
      <a-space wrap>
        <a-input v-model:value="filters.city" placeholder="按城市搜索" allow-clear style="width: 220px" />
        <a-select v-model:value="filters.status" allow-clear placeholder="状态" style="width: 160px">
          <a-select-option value="saved">已保存</a-select-option>
          <a-select-option value="draft">草稿</a-select-option>
          <a-select-option value="archived">归档</a-select-option>
        </a-select>
        <a-button @click="loadTrips">筛选</a-button>
      </a-space>
    </div>

    <a-spin :spinning="loading">
      <div v-if="trips.length" class="trip-grid">
        <div v-for="trip in trips" :key="trip.id" class="trip-card">
          <RouterLink :to="`/trips/${trip.id}`">
            <div class="trip-card-title">{{ trip.title }}</div>
            <div class="trip-card-meta">
              <div>{{ trip.city }} · {{ trip.travel_days }}天</div>
              <div>{{ trip.start_date }} 至 {{ trip.end_date }}</div>
              <span class="status-pill">{{ statusText(trip.status) }}</span>
            </div>
          </RouterLink>
          <a-divider style="margin: 14px 0" />
          <a-space>
            <a-button size="small" @click="copyTrip(trip.id)">复制</a-button>
            <a-popconfirm title="确认删除这个行程？" @confirm="removeTrip(trip.id)">
              <a-button size="small" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </div>
      </div>
      <div v-else class="content-panel empty-state">暂无行程记录。</div>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { deleteTrip, duplicateTrip, fetchTrips } from '@/services/api'
import type { SavedTripSummary } from '@/types'

const router = useRouter()
const loading = ref(false)
const trips = ref<SavedTripSummary[]>([])
const filters = reactive<{ city?: string; status?: string }>({})

const statusText = (status: string) => {
  const map: Record<string, string> = { saved: '已保存', draft: '草稿', archived: '归档' }
  return map[status] || status
}

const loadTrips = async () => {
  loading.value = true
  try {
    trips.value = await fetchTrips(filters)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '行程加载失败')
  } finally {
    loading.value = false
  }
}

const copyTrip = async (id: number) => {
  const copied = await duplicateTrip(id)
  message.success('已复制为草稿')
  router.push(`/trips/${copied.id}`)
}

const removeTrip = async (id: number) => {
  await deleteTrip(id)
  message.success('已删除')
  loadTrips()
}

onMounted(loadTrips)
</script>
