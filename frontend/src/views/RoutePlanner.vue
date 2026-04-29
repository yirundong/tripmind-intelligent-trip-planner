<template>
  <div>
    <div class="page-toolbar">
      <div>
        <div class="page-kicker">ROUTE</div>
        <h1 class="page-title-modern">路线规划</h1>
        <p class="page-description">调用真实地图路线服务，查询两地之间的距离、耗时和交通描述。</p>
      </div>
    </div>

    <div class="route-layout">
      <section class="content-panel">
        <h2 class="section-title-modern">路线参数</h2>
        <a-form layout="vertical" :model="form" @finish="submit">
          <a-form-item label="起点" name="origin_address" :rules="[{ required: true, message: '请输入起点' }]">
            <a-input v-model:value="form.origin_address" placeholder="例如：故宫博物院" />
          </a-form-item>
          <a-form-item label="终点" name="destination_address" :rules="[{ required: true, message: '请输入终点' }]">
            <a-input v-model:value="form.destination_address" placeholder="例如：天坛公园" />
          </a-form-item>

          <a-row :gutter="14">
            <a-col :span="12">
              <a-form-item label="起点城市">
                <a-input v-model:value="form.origin_city" placeholder="北京" />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="终点城市">
                <a-input v-model:value="form.destination_city" placeholder="北京" />
              </a-form-item>
            </a-col>
          </a-row>

          <a-form-item label="交通方式">
            <a-segmented
              v-model:value="form.route_type"
              block
              :options="[
                { label: '步行', value: 'walking' },
                { label: '驾车', value: 'driving' },
                { label: '公交', value: 'transit' }
              ]"
            />
          </a-form-item>

          <a-button type="primary" html-type="submit" block size="large" :loading="loading">规划路线</a-button>
        </a-form>
      </section>

      <section class="content-panel result-panel">
        <h2 class="section-title-modern">规划结果</h2>
        <template v-if="route">
          <div class="route-summary">
            <div class="route-metric">
              <span class="metric-label">距离</span>
              <strong>{{ formatDistance(route.distance) }}</strong>
            </div>
            <div class="route-metric">
              <span class="metric-label">耗时</span>
              <strong>{{ formatDuration(route.duration) }}</strong>
            </div>
            <div class="route-metric">
              <span class="metric-label">方式</span>
              <strong>{{ routeTypeText(route.route_type) }}</strong>
            </div>
          </div>

          <a-divider />
          <div class="route-path">
            <div class="path-point start">起</div>
            <div>
              <div class="path-title">{{ form.origin_address }}</div>
              <div class="path-subtitle">{{ form.origin_city || '未指定城市' }}</div>
            </div>
            <div class="path-line"></div>
            <div class="path-point end">终</div>
            <div>
              <div class="path-title">{{ form.destination_address }}</div>
              <div class="path-subtitle">{{ form.destination_city || form.origin_city || '未指定城市' }}</div>
            </div>
          </div>

          <a-divider />
          <div class="route-description">{{ route.description }}</div>
        </template>

        <div v-else class="empty-state">输入起点和终点后开始规划路线。</div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { planRoute } from '@/services/api'
import type { RouteInfo, RouteRequest } from '@/types'

const loading = ref(false)
const route = ref<RouteInfo | null>(null)

const form = reactive<RouteRequest>({
  origin_address: '故宫博物院',
  destination_address: '天坛公园',
  origin_city: '北京',
  destination_city: '北京',
  route_type: 'driving'
})

const routeTypeText = (type: string) => {
  const map: Record<string, string> = {
    walking: '步行',
    driving: '驾车',
    transit: '公交'
  }
  return map[type] || type
}

const formatDistance = (meters: number) => {
  if (meters >= 1000) return `${(meters / 1000).toFixed(1)} km`
  return `${Math.round(meters)} m`
}

const formatDuration = (seconds: number) => {
  const minutes = Math.round(seconds / 60)
  if (minutes >= 60) {
    const hours = Math.floor(minutes / 60)
    const rest = minutes % 60
    return rest ? `${hours}小时${rest}分钟` : `${hours}小时`
  }
  return `${minutes}分钟`
}

const submit = async () => {
  loading.value = true
  route.value = null
  try {
    const response = await planRoute({
      ...form,
      destination_city: form.destination_city || form.origin_city
    })
    if (!response.success || !response.data) {
      message.warning(response.message || '未查询到可用路线')
      return
    }
    route.value = response.data
    message.success('路线规划成功')
  } catch (error: any) {
    message.error(error.response?.data?.detail || error.message || '路线规划失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.route-layout {
  display: grid;
  grid-template-columns: 420px minmax(0, 1fr);
  gap: 18px;
}

.result-panel {
  min-height: 520px;
}

.route-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.route-metric {
  padding: 18px;
  border-radius: 8px;
  background: #eef7f6;
}

.route-metric .metric-label {
  display: block;
  margin-bottom: 8px;
}

.route-metric strong {
  color: #0f766e;
  font-size: 26px;
}

.route-path {
  display: grid;
  grid-template-columns: 34px 1fr;
  gap: 8px 14px;
  align-items: center;
}

.path-point {
  width: 34px;
  height: 34px;
  border-radius: 4px;
  display: grid;
  place-items: center;
  color: #ffffff;
  font-weight: 800;
}

.path-point.start {
  background: #0f766e;
}

.path-point.end {
  background: #2563eb;
}

.path-line {
  width: 2px;
  height: 52px;
  margin-left: 16px;
  background: #cde7e3;
}

.path-title {
  color: #17202a;
  font-weight: 750;
}

.path-subtitle {
  margin-top: 4px;
  color: #667085;
  font-size: 13px;
}

.route-description {
  padding: 18px;
  border-radius: 8px;
  background: #f9fbfd;
  color: #344054;
  line-height: 1.8;
  white-space: pre-wrap;
}

@media (max-width: 980px) {
  .route-layout {
    grid-template-columns: 1fr;
  }

  .route-summary {
    grid-template-columns: 1fr;
  }
}
</style>
