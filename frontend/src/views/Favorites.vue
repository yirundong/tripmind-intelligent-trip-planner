<template>
  <div>
    <div class="page-toolbar">
      <div>
        <div class="page-kicker">FAVORITES</div>
        <h1 class="page-title-modern">地点收藏夹</h1>
        <p class="page-description">把喜欢的景点、餐厅、酒店沉淀下来，后续可以作为行程生成依据。</p>
      </div>
      <a-button type="primary" @click="showCreate = true">手动添加</a-button>
    </div>

    <a-spin :spinning="loading">
      <div v-if="items.length" class="trip-grid">
        <div v-for="item in items" :key="item.id" class="trip-card">
          <div class="trip-card-title">{{ item.name }}</div>
          <div class="trip-card-meta">
            <div>{{ item.city || '未设置城市' }} · {{ item.category }}</div>
            <div>{{ item.address || '暂无地址' }}</div>
            <div v-if="item.notes">{{ item.notes }}</div>
          </div>
          <a-divider style="margin: 14px 0" />
          <a-popconfirm title="删除这个收藏？" @confirm="remove(item.id)">
            <a-button size="small" danger>删除</a-button>
          </a-popconfirm>
        </div>
      </div>
      <div v-else class="content-panel empty-state">还没有收藏地点。</div>
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
import { onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { createFavorite, deleteFavorite, fetchFavorites } from '@/services/api'
import type { FavoritePlace } from '@/types'

const loading = ref(false)
const showCreate = ref(false)
const items = ref<FavoritePlace[]>([])
const form = reactive({
  name: '',
  city: '',
  address: '',
  category: '景点',
  longitude: '',
  latitude: '',
  notes: ''
})

const load = async () => {
  loading.value = true
  try {
    items.value = await fetchFavorites()
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

const remove = async (id: number) => {
  await deleteFavorite(id)
  message.success('已删除')
  load()
}

onMounted(load)
</script>
