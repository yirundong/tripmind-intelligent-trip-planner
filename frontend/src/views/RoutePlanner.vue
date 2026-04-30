<template>
  <div>
    <div class="page-toolbar">
      <div>
        <div class="page-kicker">ROUTE</div>
        <h1 class="page-title-modern">路线规划</h1>
        <p class="page-description">调用真实地图路线服务，查询两地之间的距离、耗时，并在地图上展示路径。</p>
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
        </template>

        <div class="route-map-card" :class="{ 'is-empty': !route }">
          <div id="route-map" class="route-map"></div>
          <div v-if="mapError || !route" class="map-tip">
            {{ mapError || '输入起点和终点后，系统会在这里展示路线地图。' }}
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import { planRoute } from '@/services/api'
import type { RouteInfo, RouteRequest } from '@/types'

declare global {
  interface Window {
    _AMapSecurityConfig?: {
      securityJsCode: string
    }
  }
}

const loading = ref(false)
const route = ref<RouteInfo | null>(null)
const mapError = ref('')

const form = reactive<RouteRequest>({
  origin_address: '故宫博物院',
  destination_address: '天坛公园',
  origin_city: '北京',
  destination_city: '北京',
  route_type: 'driving'
})

let map: any = null
let AMapRef: any = null
let routePlanner: any = null

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

const initMap = async () => {
  if (map && AMapRef) return true

  const jsApiKey = import.meta.env.VITE_AMAP_WEB_JS_KEY?.trim()
  const securityJsCode = import.meta.env.VITE_AMAP_SECURITY_JS_CODE?.trim()
  if (!jsApiKey) {
    mapError.value = '未配置高德 JS API Key，暂时无法显示路线地图'
    return false
  }

  if (securityJsCode) {
    window._AMapSecurityConfig = { securityJsCode }
  }

  AMapRef = await AMapLoader.load({
    key: jsApiKey,
    version: '2.0',
    plugins: ['AMap.Driving', 'AMap.Walking', 'AMap.Transfer']
  })

  map = new AMapRef.Map('route-map', {
    zoom: 12,
    center: [116.397128, 39.916527],
    resizeEnable: true,
    viewMode: '3D'
  })
  return true
}

const clearRouteMap = () => {
  if (routePlanner?.clear) {
    routePlanner.clear()
  }
  routePlanner = null
  mapError.value = ''
}

const renderRouteMap = async () => {
  await nextTick()
  clearRouteMap()
  const available = await initMap()
  if (!available || !map || !AMapRef) return

  map.resize()
  const origin = {
    keyword: form.origin_address,
    city: form.origin_city || undefined
  }
  const destination = {
    keyword: form.destination_address,
    city: form.destination_city || form.origin_city || undefined
  }

  const callback = (status: string, result: any) => {
    if (status !== 'complete') {
      console.warn('高德路线地图绘制失败:', result)
      mapError.value = '路线数据已返回，但地图暂时无法绘制，请检查地点名称或城市。'
    }
  }

  if (form.route_type === 'transit') {
    routePlanner = new AMapRef.Transfer({
      map,
      city: form.origin_city || form.destination_city || '',
      cityd: form.destination_city || form.origin_city || ''
    })
  } else if (form.route_type === 'walking') {
    routePlanner = new AMapRef.Walking({ map })
  } else {
    routePlanner = new AMapRef.Driving({ map })
  }

  routePlanner.search([origin, destination], callback)
}

const submit = async () => {
  loading.value = true
  route.value = null
  clearRouteMap()
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
    await renderRouteMap()
    message.success('路线规划成功')
  } catch (error: any) {
    message.error(error.response?.data?.detail || error.message || '路线规划失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  nextTick(initMap)
})
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

.route-map-card {
  margin-top: 18px;
  border: 1px solid #e5eaf1;
  border-radius: 8px;
  overflow: hidden;
  background: #f9fbfd;
}

.route-map {
  width: 100%;
  height: 420px;
}

.route-map-card.is-empty .route-map {
  background: linear-gradient(135deg, #eef7f6 0%, #f8fafc 100%);
}

.map-tip {
  padding: 12px 16px;
  border-top: 1px solid #e5eaf1;
  color: #667085;
  background: #ffffff;
  font-size: 14px;
}

@media (max-width: 980px) {
  .route-layout {
    grid-template-columns: 1fr;
  }

  .route-summary {
    grid-template-columns: 1fr;
  }

  .route-map {
    height: 360px;
  }
}
</style>
