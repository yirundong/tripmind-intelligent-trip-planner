<template>
  <div>
    <div class="page-toolbar">
      <div>
        <div class="page-kicker">TRIP DETAIL</div>
        <h1 class="page-title-modern">{{ detail?.title || '行程详情' }}</h1>
        <p v-if="detail" class="page-description">{{ detail.city }} · {{ detail.start_date }} 至 {{ detail.end_date }}</p>
      </div>
      <a-space>
        <a-button @click="$router.push('/trips')">返回列表</a-button>
        <a-button type="primary" @click="saveMeta" :loading="saving">保存信息</a-button>
      </a-space>
    </div>

    <a-spin :spinning="loading">
      <template v-if="detail">
        <div class="detail-layout">
          <section class="content-panel">
            <h2 class="section-title-modern">基础信息</h2>
            <a-form layout="vertical">
              <a-form-item label="标题">
                <a-input v-model:value="detail.title" />
              </a-form-item>
              <a-form-item label="状态">
                <a-select v-model:value="detail.status">
                  <a-select-option value="saved">已保存</a-select-option>
                  <a-select-option value="draft">草稿</a-select-option>
                  <a-select-option value="archived">归档</a-select-option>
                </a-select>
              </a-form-item>
              <a-form-item label="备注">
                <a-textarea v-model:value="detail.notes" :rows="4" placeholder="记录签证、交通、订票等补充信息" />
              </a-form-item>
            </a-form>
          </section>

          <section class="content-panel">
            <h2 class="section-title-modern">预算</h2>
            <a-descriptions v-if="detail.plan_data.budget" :column="1" bordered size="small">
              <a-descriptions-item label="景点">¥{{ detail.plan_data.budget.total_attractions }}</a-descriptions-item>
              <a-descriptions-item label="住宿">¥{{ detail.plan_data.budget.total_hotels }}</a-descriptions-item>
              <a-descriptions-item label="餐饮">¥{{ detail.plan_data.budget.total_meals }}</a-descriptions-item>
              <a-descriptions-item label="交通">¥{{ detail.plan_data.budget.total_transportation }}</a-descriptions-item>
              <a-descriptions-item label="总计">¥{{ detail.plan_data.budget.total }}</a-descriptions-item>
            </a-descriptions>
          </section>
        </div>

        <section class="content-panel" style="margin-top: 16px">
          <h2 class="section-title-modern">每日行程</h2>
          <a-collapse>
            <a-collapse-panel v-for="(day, index) in detail.plan_data.days" :key="index" :header="`第${index + 1}天 · ${day.date}`">
              <p>{{ day.description }}</p>
              <a-list :data-source="day.attractions" bordered>
                <template #renderItem="{ item }">
                  <a-list-item>
                    <a-list-item-meta :title="item.name" :description="`${item.address} · ${item.visit_duration}分钟`" />
                    <a-button size="small" @click="favorite(item)">收藏</a-button>
                  </a-list-item>
                </template>
              </a-list>
            </a-collapse-panel>
          </a-collapse>
        </section>
      </template>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { createFavorite, fetchTrip, updateTrip } from '@/services/api'
import type { Attraction, SavedTripDetail } from '@/types'

const route = useRoute()
const loading = ref(false)
const saving = ref(false)
const detail = ref<SavedTripDetail | null>(null)

const load = async () => {
  loading.value = true
  try {
    detail.value = await fetchTrip(Number(route.params.id))
  } catch (error: any) {
    message.error(error.response?.data?.detail || '行程详情加载失败')
  } finally {
    loading.value = false
  }
}

const saveMeta = async () => {
  if (!detail.value) return
  saving.value = true
  try {
    detail.value = await updateTrip(detail.value.id, {
      title: detail.value.title,
      status: detail.value.status,
      notes: detail.value.notes
    })
    message.success('已保存')
  } finally {
    saving.value = false
  }
}

const favorite = async (item: Attraction) => {
  if (!detail.value) return
  await createFavorite({
    name: item.name,
    city: detail.value.city,
    address: item.address,
    category: item.category || '景点',
    longitude: String(item.location?.longitude || ''),
    latitude: String(item.location?.latitude || ''),
    notes: item.description || ''
  })
  message.success('已加入收藏')
}

onMounted(load)
</script>

<style scoped>
.detail-layout {
  display: grid;
  grid-template-columns: 1.4fr 0.8fr;
  gap: 16px;
}

@media (max-width: 900px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
</style>
