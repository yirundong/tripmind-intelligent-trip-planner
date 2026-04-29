<template>
  <div>
    <div class="page-toolbar">
      <div>
        <div class="page-kicker">EXPLORE</div>
        <h1 class="page-title-modern">目的地探索</h1>
        <p class="page-description">搜索真实地图 POI，查看位置、类型和坐标，并把合适的地点加入收藏。</p>
      </div>
    </div>

    <div class="explore-shell">
      <section class="explore-sidebar">
        <div class="search-panel">
          <a-form layout="vertical" @finish="search">
            <a-form-item label="城市">
              <a-input v-model:value="query.city" placeholder="例如 北京" />
            </a-form-item>
            <a-form-item label="关键词">
              <a-input-search
                v-model:value="query.keywords"
                placeholder="景点 / 美食 / 酒店 / 商圈"
                enter-button="搜索"
                :loading="loading"
                @search="search"
              />
            </a-form-item>
            <div class="quick-tags">
              <a-button v-for="keyword in quickKeywords" :key="keyword" size="small" @click="quickSearch(keyword)">
                {{ keyword }}
              </a-button>
            </div>
          </a-form>
        </div>

        <a-spin :spinning="loading">
          <div v-if="results.length" class="poi-list">
            <button
              v-for="(item, index) in results"
              :key="item.id || `${item.name}-${index}`"
              class="poi-item"
              :class="{ active: selectedIndex === index }"
              @click="focusPoi(item, index)"
            >
              <span class="poi-rank">{{ index + 1 }}</span>
              <span class="poi-main">
                <span class="poi-name">{{ item.name }}</span>
                <span class="poi-meta">{{ item.type || '地点' }}</span>
                <span class="poi-address">{{ item.address || '暂无地址' }}</span>
              </span>
            </button>
          </div>
          <div v-else class="empty-state">输入城市和关键词后开始探索。</div>
        </a-spin>
      </section>

      <section class="map-panel">
        <div id="explore-map" class="explore-map"></div>
        <aside v-if="selectedPoi" class="poi-detail">
          <div class="poi-detail-kicker">SELECTED PLACE</div>
          <h2>{{ selectedPoi.name }}</h2>
          <p>{{ selectedPoi.address || '暂无地址' }}</p>
          <a-descriptions :column="1" size="small" bordered>
            <a-descriptions-item label="类型">{{ selectedPoi.type || '地点' }}</a-descriptions-item>
            <a-descriptions-item label="经度">{{ selectedPoi.location?.longitude || '-' }}</a-descriptions-item>
            <a-descriptions-item label="纬度">{{ selectedPoi.location?.latitude || '-' }}</a-descriptions-item>
          </a-descriptions>
          <a-button type="primary" block style="margin-top: 14px" @click="favorite(selectedPoi)">加入收藏</a-button>
        </aside>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import apiClient, { createFavorite } from '@/services/api'

declare global {
  interface Window {
    _AMapSecurityConfig?: {
      securityJsCode: string
    }
  }
}

type PoiItem = {
  id?: string
  name: string
  type?: string
  address?: string
  location?: {
    longitude: number
    latitude: number
  }
}

const loading = ref(false)
const mapReady = ref(false)
const selectedIndex = ref(-1)
const selectedPoi = ref<PoiItem | null>(null)
const results = ref<PoiItem[]>([])
const quickKeywords = ['景点', '博物馆', '美食', '酒店', '商圈', '公园']
const query = reactive({
  city: '北京',
  keywords: '博物馆'
})

let map: any = null
let AMapRef: any = null
let markers: any[] = []
let infoWindow: any = null

const initMap = async () => {
  if (mapReady.value) return

  const jsApiKey = import.meta.env.VITE_AMAP_WEB_JS_KEY?.trim()
  const securityJsCode = import.meta.env.VITE_AMAP_SECURITY_JS_CODE?.trim()
  if (!jsApiKey) {
    message.warning('未配置高德 JS API Key，地图区域暂不可用')
    return
  }

  if (securityJsCode) {
    window._AMapSecurityConfig = { securityJsCode }
  }

  AMapRef = await AMapLoader.load({
    key: jsApiKey,
    version: '2.0',
    plugins: ['AMap.Marker', 'AMap.InfoWindow']
  })
  map = new AMapRef.Map('explore-map', {
    zoom: 12,
    center: [116.397128, 39.916527],
    viewMode: '3D'
  })
  infoWindow = new AMapRef.InfoWindow({ offset: new AMapRef.Pixel(0, -28) })
  mapReady.value = true
}

const clearMarkers = () => {
  if (map && markers.length) {
    map.remove(markers)
  }
  markers = []
}

const renderMarkers = async () => {
  await nextTick()
  await initMap()
  if (!map || !AMapRef) return

  clearMarkers()
  const validPois = results.value.filter(item => item.location?.longitude && item.location?.latitude)
  markers = validPois.map((item, index) => {
    const marker = new AMapRef.Marker({
      position: [item.location!.longitude, item.location!.latitude],
      title: item.name,
      label: {
        content: `<div class="map-label">${index + 1}</div>`,
        offset: new AMapRef.Pixel(0, -30)
      }
    })
    marker.on('click', () => focusPoi(item, results.value.indexOf(item)))
    return marker
  })

  if (markers.length) {
    map.add(markers)
    map.setFitView(markers)
  }
}

const search = async () => {
  if (!query.city.trim() || !query.keywords.trim()) {
    message.warning('请输入城市和关键词')
    return
  }

  loading.value = true
  selectedIndex.value = -1
  selectedPoi.value = null
  try {
    const response = await apiClient.get('/api/map/poi', { params: query })
    results.value = response.data.data || []
    if (!results.value.length) {
      message.info('没有搜索到匹配地点')
    }
    await renderMarkers()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '搜索失败')
  } finally {
    loading.value = false
  }
}

const quickSearch = (keyword: string) => {
  query.keywords = keyword
  search()
}

const focusPoi = async (item: PoiItem, index: number) => {
  selectedIndex.value = index
  selectedPoi.value = item
  await initMap()
  if (!map || !AMapRef || !item.location) return

  const position = [item.location.longitude, item.location.latitude]
  map.setZoomAndCenter(15, position)
  infoWindow?.setContent(`
    <div style="min-width:180px;padding:6px 2px;">
      <strong>${item.name}</strong>
      <div style="margin-top:6px;color:#667085;">${item.type || '地点'}</div>
      <div style="margin-top:4px;color:#667085;">${item.address || ''}</div>
    </div>
  `)
  infoWindow?.open(map, position)
}

const favorite = async (item: PoiItem) => {
  await createFavorite({
    name: item.name,
    city: query.city,
    address: item.address || '',
    category: item.type || '景点',
    longitude: String(item.location?.longitude || ''),
    latitude: String(item.location?.latitude || ''),
    notes: ''
  })
  message.success('已加入收藏')
}

onMounted(() => {
  initMap().catch(error => {
    console.error('探索页地图初始化失败:', error)
  })
})
</script>

<style scoped>
.explore-shell {
  display: grid;
  grid-template-columns: 380px minmax(0, 1fr);
  gap: 18px;
  min-height: calc(100vh - 180px);
}

.explore-sidebar,
.map-panel,
.search-panel {
  border: 1px solid #e5eaf1;
  border-radius: 8px;
  background: #ffffff;
}

.explore-sidebar {
  overflow: hidden;
}

.search-panel {
  border: 0;
  border-bottom: 1px solid #e5eaf1;
  border-radius: 8px 8px 0 0;
  padding: 18px;
}

.quick-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.poi-list {
  max-height: calc(100vh - 390px);
  overflow: auto;
  padding: 10px;
}

.poi-item {
  width: 100%;
  display: flex;
  gap: 12px;
  padding: 14px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.poi-item:hover,
.poi-item.active {
  background: #eef7f6;
  border-color: #cde7e3;
}

.poi-rank {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  background: #0f766e;
  color: #ffffff;
  font-weight: 700;
}

.poi-main {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.poi-name {
  color: #17202a;
  font-weight: 750;
}

.poi-meta,
.poi-address {
  color: #667085;
  font-size: 12px;
  line-height: 1.5;
}

.map-panel {
  position: relative;
  overflow: hidden;
  min-height: 620px;
}

.explore-map {
  width: 100%;
  height: 100%;
  min-height: 620px;
}

.poi-detail {
  position: absolute;
  right: 18px;
  bottom: 18px;
  width: 320px;
  padding: 18px;
  border: 1px solid #e5eaf1;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 8px 22px rgba(15, 23, 42, 0.1);
  backdrop-filter: blur(12px);
}

.poi-detail h2 {
  margin: 6px 0 8px;
  font-size: 20px;
}

.poi-detail p {
  color: #667085;
  line-height: 1.6;
}

.poi-detail-kicker {
  color: #0f766e;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.06em;
}

:deep(.map-label) {
  min-width: 24px;
  height: 24px;
  padding: 0 7px;
  border-radius: 4px;
  display: grid;
  place-items: center;
  background: #0f766e;
  color: #ffffff;
  font-weight: 800;
  box-shadow: 0 4px 10px rgba(15, 118, 110, 0.22);
}

@media (max-width: 980px) {
  .explore-shell {
    grid-template-columns: 1fr;
  }

  .map-panel,
  .explore-map {
    min-height: 460px;
  }

  .poi-list {
    max-height: none;
  }
}
</style>
