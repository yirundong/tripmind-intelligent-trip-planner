<template>
  <div>
    <div class="page-toolbar">
      <div>
        <div class="page-kicker">FAVORITES</div>
        <h1 class="page-title-modern">地点收藏夹</h1>
        <p class="page-description">选择收藏地点后，可以带到规划页作为本次行程的候选输入。</p>
      </div>
      <div class="toolbar-actions">
        <a-button :disabled="selectedIds.length === 0" @click="planWithSelected">加入本次规划</a-button>
        <a-button type="primary" @click="showCreate = true">手动添加</a-button>
      </div>
    </div>

    <a-spin :spinning="loading">
      <div v-if="items.length" class="favorite-summary">
        <div>
          <strong>已选择 {{ selectedIds.length }} 个地点</strong>
          <span>Agent 会结合城市、地址、类型和备注判断是否放入行程。</span>
        </div>
        <a-button type="link" :disabled="selectedIds.length === 0" @click="clearSelected">清空选择</a-button>
      </div>

      <div v-if="items.length" class="trip-grid">
        <div v-for="item in items" :key="item.id" class="trip-card favorite-card" :class="{ selected: selectedIds.includes(item.id) }">
          <div class="favorite-card-head">
            <a-checkbox
              :checked="selectedIds.includes(item.id)"
              @change="(event: any) => toggleSelected(item.id, event.target.checked)"
            >
              用于规划
            </a-checkbox>
          </div>
          <div class="trip-card-title">{{ item.name }}</div>
          <div class="trip-card-meta">
            <div>{{ item.city || '未设置城市' }} · {{ item.category }}</div>
            <div>{{ item.address || '暂无地址' }}</div>
            <div v-if="item.notes">{{ item.notes }}</div>
          </div>
          <a-divider style="margin: 14px 0" />
          <div class="card-actions">
            <a-button size="small" type="primary" @click="planAround(item)">围绕此地规划</a-button>
            <a-popconfirm title="删除这个收藏？" @confirm="remove(item.id)">
              <a-button size="small" danger>删除</a-button>
            </a-popconfirm>
          </div>
        </div>
      </div>
      <div v-else class="content-panel empty-state">
        <p>还没有收藏地点。</p>
        <a-button type="primary" @click="router.push('/explore')">去探索地点</a-button>
      </div>
    </a-spin>

    <a-modal v-model:open="showCreate" title="添加收藏地点" @ok="create">
      <a-form layout="vertical">
        <a-form-item label="名称"><a-input v-model:value="form.name" /></a-form-item>
        <a-form-item label="城市"><a-input v-model:value="form.city" /></a-form-item>
        <a-form-item label="地址"><a-input v-model:value="form.address" /></a-form-item>
        <a-form-item label="类型"><a-input v-model:value="form.category" /></a-form-item>
        <a-form-item label="备注"><a-textarea v-model:value="form.notes" /></a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { createFavorite, deleteFavorite, fetchFavorites } from '@/services/api'
import type { FavoritePlace } from '@/types'

const FAVORITE_PLANNING_KEY = 'tripPlanningFavorites'

const router = useRouter()
const loading = ref(false)
const showCreate = ref(false)
const items = ref<FavoritePlace[]>([])
const selectedIds = ref<number[]>([])
const form = reactive({
  name: '',
  city: '',
  address: '',
  category: '景点',
  longitude: '',
  latitude: '',
  notes: ''
})

const selectedFavorites = computed(() => {
  return items.value.filter(item => selectedIds.value.includes(item.id))
})

const load = async () => {
  loading.value = true
  try {
    items.value = await fetchFavorites()
    selectedIds.value = selectedIds.value.filter(id => items.value.some(item => item.id === id))
  } finally {
    loading.value = false
  }
}

const create = async () => {
  await createFavorite(form)
  showCreate.value = false
  message.success('已添加收藏')
  load()
}

const toggleSelected = (id: number, checked: boolean) => {
  if (checked) {
    selectedIds.value = Array.from(new Set([...selectedIds.value, id]))
  } else {
    selectedIds.value = selectedIds.value.filter(item => item !== id)
  }
}

const clearSelected = () => {
  selectedIds.value = []
}

const writePlanningContext = (favorites: FavoritePlace[], mode: 'selected' | 'focus') => {
  sessionStorage.setItem(FAVORITE_PLANNING_KEY, JSON.stringify({
    mode,
    favorites,
    created_at: new Date().toISOString()
  }))
}

const planWithSelected = () => {
  if (!selectedFavorites.value.length) {
    message.warning('请先选择要用于规划的收藏地点')
    return
  }

  writePlanningContext(selectedFavorites.value, 'selected')
  message.success('已带入规划页')
  router.push('/')
}

const planAround = (item: FavoritePlace) => {
  writePlanningContext([item], 'focus')
  message.success('已带入规划页')
  router.push('/')
}

const remove = async (id: number) => {
  await deleteFavorite(id)
  message.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar-actions,
.card-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.favorite-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  padding: 14px 16px;
  border: 1px solid #e5eaf1;
  border-radius: 8px;
  background: #ffffff;
}

.favorite-summary div {
  display: flex;
  gap: 10px;
  align-items: baseline;
  flex-wrap: wrap;
}

.favorite-summary span,
.empty-state p {
  margin: 0;
  color: #667085;
}

.favorite-card {
  position: relative;
}

.favorite-card.selected {
  border-color: #0f766e;
  background: #f7fcfb;
}

.favorite-card-head {
  margin-bottom: 12px;
}

.card-actions {
  justify-content: space-between;
}

@media (max-width: 720px) {
  .page-toolbar,
  .favorite-summary {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
