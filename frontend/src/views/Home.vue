<template>
  <div class="home-container">
    <div class="page-header">
      <div class="page-kicker">AI TRIP PLANNER</div>
      <h1 class="page-title">智能旅行规划</h1>
      <p class="page-subtitle">输入目的地、日期和偏好，系统会自动搜索景点、天气、住宿并生成可保存的结构化行程。</p>
    </div>

    <div class="planner-layout">
      <a-card class="form-card" :bordered="false">
        <a-form :model="formData" layout="vertical" @finish="handleSubmit">
          <div v-if="favoriteContext.favorites.length" class="favorite-context-panel">
            <div>
              <div class="context-title">
                {{ favoriteContext.mode === 'focus' ? '围绕收藏地点规划' : '已带入收藏地点' }}
              </div>
              <div class="context-list">
                <a-tag v-for="item in favoriteContext.favorites" :key="item.id">
                  {{ item.name }}
                </a-tag>
              </div>
            </div>
            <a-button size="small" @click="clearFavoriteContext">移除</a-button>
          </div>

          <div class="form-section">
            <div class="section-header">
              <EnvironmentOutlined />
              <span class="section-title">目的地与日期</span>
            </div>

            <a-row :gutter="[20, 16]">
              <a-col :xs="24" :lg="8">
                <a-form-item name="city" :rules="[{ required: true, message: '请输入目的地城市' }]">
                  <template #label>
                    <span class="form-label">目的地城市</span>
                  </template>
                  <a-input v-model:value="formData.city" placeholder="例如：北京" size="large" />
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="12" :lg="6">
                <a-form-item name="start_date" :rules="[{ required: true, message: '请选择开始日期' }]">
                  <template #label>
                    <span class="form-label">开始日期</span>
                  </template>
                  <a-date-picker v-model:value="formData.start_date" style="width: 100%" size="large" placeholder="选择日期" />
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="12" :lg="6">
                <a-form-item name="end_date" :rules="[{ required: true, message: '请选择结束日期' }]">
                  <template #label>
                    <span class="form-label">结束日期</span>
                  </template>
                  <a-date-picker v-model:value="formData.end_date" style="width: 100%" size="large" placeholder="选择日期" />
                </a-form-item>
              </a-col>
              <a-col :xs="24" :lg="4">
                <a-form-item>
                  <template #label>
                    <span class="form-label">旅行天数</span>
                  </template>
                  <div class="days-display-compact">
                    <span class="days-value">{{ formData.travel_days }}</span>
                    <span class="days-unit">天</span>
                  </div>
                </a-form-item>
              </a-col>
            </a-row>
          </div>

          <div class="form-section">
            <div class="section-header">
              <SettingOutlined />
              <span class="section-title">偏好设置</span>
            </div>

            <a-row :gutter="[20, 16]">
              <a-col :xs="24" :lg="12">
                <a-form-item name="transportation">
                  <template #label>
                    <span class="form-label">交通方式</span>
                  </template>
                  <a-select v-model:value="formData.transportation" size="large">
                    <a-select-option value="公共交通">公共交通</a-select-option>
                    <a-select-option value="自驾">自驾</a-select-option>
                    <a-select-option value="步行">步行</a-select-option>
                    <a-select-option value="混合">混合</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :xs="24" :lg="12">
                <a-form-item name="accommodation">
                  <template #label>
                    <span class="form-label">住宿偏好</span>
                  </template>
                  <a-select v-model:value="formData.accommodation" size="large">
                    <a-select-option value="经济型酒店">经济型酒店</a-select-option>
                    <a-select-option value="舒适型酒店">舒适型酒店</a-select-option>
                    <a-select-option value="豪华酒店">豪华酒店</a-select-option>
                    <a-select-option value="民宿">民宿</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :xs="24">
                <a-form-item name="preferences">
                  <template #label>
                    <span class="form-label">旅行偏好</span>
                  </template>
                  <div class="preference-editor">
                    <div class="preference-tags">
                      <a-checkable-tag
                        v-for="tag in availablePreferences"
                        :key="tag"
                        :checked="formData.preferences.includes(tag)"
                        @change="(checked: boolean) => togglePreference(tag, checked)"
                      >
                        {{ tag }}
                      </a-checkable-tag>
                    </div>

                    <div class="selected-tags">
                      <a-tag
                        v-for="tag in formData.preferences"
                        :key="tag"
                        closable
                        @close.prevent="removePreference(tag)"
                      >
                        {{ tag }}
                      </a-tag>
                      <span v-if="formData.preferences.length === 0" class="empty-tip">尚未选择偏好</span>
                    </div>

                    <a-input-search
                      v-model:value="customPreference"
                      placeholder="输入自定义偏好，例如：亲子、摄影、Citywalk"
                      enter-button="添加"
                      style="max-width: 520px"
                      @search="addCustomPreference"
                    />
                  </div>
                </a-form-item>
              </a-col>
            </a-row>
          </div>

          <div class="form-section">
            <div class="section-header">
              <MessageOutlined />
              <span class="section-title">额外要求</span>
            </div>

            <a-form-item name="free_text_input">
              <a-textarea
                v-model:value="formData.free_text_input"
                placeholder="例如：想去看升旗、需要无障碍设施、对海鲜过敏、希望安排轻松一点..."
                :rows="4"
                size="large"
              />
            </a-form-item>
          </div>

          <a-form-item>
            <a-button type="primary" html-type="submit" :loading="loading" size="large" block class="submit-button">
              <template v-if="!loading">
                <RocketOutlined />
                <span>开始规划我的旅行</span>
              </template>
              <template v-else>
                <span>正在生成中...</span>
              </template>
            </a-button>
          </a-form-item>

          <a-form-item v-if="loading">
            <div class="loading-container">
              <div class="loading-topline">
                <span>{{ loadingStatus }}</span>
                <strong>{{ loadingProgress }}%</strong>
              </div>
              <a-progress :percent="loadingProgress" status="active" :stroke-color="'#0f766e'" :stroke-width="8" />
              <div class="workflow-panel">
                <div
                  v-for="(step, index) in workflowSteps"
                  :key="step.key"
                  class="workflow-step"
                  :class="{ done: loadingProgress >= step.doneAt, active: index === activeWorkflowIndex && loadingProgress < 100 }"
                >
                  <div class="workflow-index">{{ index + 1 }}</div>
                  <div>
                    <div class="workflow-title">{{ step.title }}</div>
                    <div class="workflow-desc">{{ step.desc }}</div>
                  </div>
                </div>
              </div>
            </div>
          </a-form-item>
        </a-form>
      </a-card>

      <aside class="planner-aside">
        <a-card title="用户画像" :bordered="false">
          <div class="profile-stack">
            <div class="profile-row">
              <span>默认城市</span>
              <strong>{{ storedUser?.default_city || '未设置' }}</strong>
            </div>
            <div class="profile-row">
              <span>交通方式</span>
              <strong>{{ storedUser?.default_transportation || formData.transportation }}</strong>
            </div>
            <div class="profile-row">
              <span>住宿偏好</span>
              <strong>{{ storedUser?.default_accommodation || formData.accommodation }}</strong>
            </div>
            <div class="profile-tags">
              <a-tag v-for="tag in formData.preferences" :key="tag">{{ tag }}</a-tag>
              <span v-if="formData.preferences.length === 0" class="empty-tip">尚未选择偏好</span>
            </div>
          </div>
        </a-card>

        <a-card title="Agent 协作流程" :bordered="false">
          <div class="aside-workflow">
            <div v-for="(step, index) in workflowSteps" :key="step.key" class="aside-step">
              <span class="aside-index">{{ index + 1 }}</span>
              <div>
                <strong>{{ step.title }}</strong>
                <p>{{ step.desc }}</p>
              </div>
            </div>
          </div>
        </a-card>

        <a-card title="生成后会沉淀的数据" :bordered="false">
          <div class="data-list">
            <span>结构化行程</span>
            <span>预算明细</span>
            <span>天气信息</span>
            <span>地图坐标</span>
            <span>任务日志</span>
          </div>
        </a-card>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  EnvironmentOutlined,
  MessageOutlined,
  RocketOutlined,
  SettingOutlined
} from '@ant-design/icons-vue'
import { createTripPlanTask, fetchTrip, fetchTripPlanTask, getStoredUser } from '@/services/api'
import type { FavoritePlace, TripFormData } from '@/types'
import type { Dayjs } from 'dayjs'

const FAVORITE_PLANNING_KEY = 'tripPlanningFavorites'

type TripFormState = Omit<TripFormData, 'start_date' | 'end_date'> & {
  start_date: Dayjs | null
  end_date: Dayjs | null
}

type FavoritePlanningContext = {
  mode: 'selected' | 'focus'
  favorites: FavoritePlace[]
  created_at?: string
}

const router = useRouter()
const loading = ref(false)
const loadingProgress = ref(0)
const loadingStatus = ref('')
const customPreference = ref('')
const favoritePromptText = ref('')
const storedUser = getStoredUser()
const favoriteContext = reactive<FavoritePlanningContext>({
  mode: 'selected',
  favorites: []
})
const suggestedPreferences = [
  '历史文化',
  '自然风光',
  '美食',
  '购物',
  '艺术',
  '休闲',
  '亲子',
  '摄影',
  'Citywalk',
  '博物馆',
  '夜景',
  '小众路线',
  '无障碍',
  '慢节奏',
  '露营',
  '海滨',
  '咖啡馆',
  '演出',
  '温泉',
  '研学'
]
const workflowSteps = [
  { key: 'request', title: '需求解析', desc: '校验目的地、日期和旅行偏好', doneAt: 18 },
  { key: 'attractions', title: '景点搜索', desc: '调用高德 POI 检索候选景点', doneAt: 32 },
  { key: 'weather', title: '天气查询', desc: '获取目的地天气预报', doneAt: 44 },
  { key: 'hotels', title: '酒店查询', desc: '根据住宿偏好检索酒店', doneAt: 58 },
  { key: 'planning', title: '行程生成', desc: 'LLM 整合工具结果生成方案', doneAt: 78 },
  { key: 'validation', title: '结构校验', desc: 'Pydantic 校验并必要时修复 JSON', doneAt: 92 },
  { key: 'save', title: '数据保存', desc: '保存到用户行程库并返回结果', doneAt: 100 }
]

const activeWorkflowIndex = computed(() => {
  const index = workflowSteps.findIndex(step => loadingProgress.value < step.doneAt)
  return index === -1 ? workflowSteps.length - 1 : index
})

const formData = reactive<TripFormState>({
  city: storedUser?.default_city || '',
  start_date: null,
  end_date: null,
  travel_days: 1,
  transportation: storedUser?.default_transportation || '公共交通',
  accommodation: storedUser?.default_accommodation || '经济型酒店',
  preferences: storedUser?.default_preferences || [],
  free_text_input: ''
})

const availablePreferences = computed(() => {
  return Array.from(new Set([
    ...suggestedPreferences,
    ...(storedUser?.default_preferences || []),
    ...formData.preferences
  ]))
})

const addPreference = (tag: string) => {
  const value = tag.trim()
  if (!value) return
  if (formData.preferences.includes(value)) {
    message.info('这个偏好已经添加过了')
    return
  }
  formData.preferences.push(value)
}

const addCustomPreference = () => {
  addPreference(customPreference.value)
  customPreference.value = ''
}

const removePreference = (tag: string) => {
  formData.preferences = formData.preferences.filter(item => item !== tag)
}

const togglePreference = (tag: string, checked: boolean) => {
  if (checked) {
    addPreference(tag)
  } else {
    removePreference(tag)
  }
}

const compactPlace = (item: FavoritePlace) => {
  return [
    item.name,
    item.city ? `城市：${item.city}` : '',
    item.category ? `类型：${item.category}` : '',
    item.address ? `地址：${item.address}` : '',
    item.notes ? `备注：${item.notes}` : ''
  ].filter(Boolean).join('，')
}

const buildFavoritePrompt = (context: FavoritePlanningContext) => {
  const places = context.favorites
    .map((item, index) => `${index + 1}. ${compactPlace(item)}`)
    .join('\n')

  if (context.mode === 'focus' && context.favorites[0]) {
    return `请围绕用户收藏地点“${context.favorites[0].name}”规划本次行程，优先把它作为核心停留点，并结合附近景点、餐饮和路线效率安排。\n收藏地点：\n${places}`
  }

  return `请优先评估以下用户收藏地点是否适合加入本次行程；如果距离、时间或主题不匹配，可以不强行安排，并在建议中说明取舍。\n收藏地点：\n${places}`
}

const inferPreferenceFromFavorite = (item: FavoritePlace) => {
  const text = `${item.category} ${item.notes} ${item.name}`
  const mappings = [
    { keywords: ['餐饮', '餐厅', '美食', '小吃'], tag: '美食' },
    { keywords: ['酒店', '住宿', '宾馆'], tag: '住宿' },
    { keywords: ['学校', '科教', '博物馆', '展览', '文化'], tag: '研学' },
    { keywords: ['公园', '风景', '自然'], tag: '自然风光' },
    { keywords: ['商场', '购物', '商圈'], tag: '购物' }
  ]
  return mappings.find(mapping => mapping.keywords.some(keyword => text.includes(keyword)))?.tag
}

const applyFavoritePlanningContext = () => {
  const raw = sessionStorage.getItem(FAVORITE_PLANNING_KEY)
  if (!raw) return

  try {
    const context = JSON.parse(raw) as FavoritePlanningContext
    if (!Array.isArray(context.favorites) || context.favorites.length === 0) return

    favoriteContext.mode = context.mode === 'focus' ? 'focus' : 'selected'
    favoriteContext.favorites = context.favorites

    const firstCity = context.favorites.find(item => item.city)?.city
    if (firstCity) {
      formData.city = firstCity
    }

    context.favorites
      .map(inferPreferenceFromFavorite)
      .filter((tag): tag is string => Boolean(tag))
      .forEach(tag => {
        if (!formData.preferences.includes(tag)) {
          formData.preferences.push(tag)
        }
      })

    const prompt = buildFavoritePrompt(context)
    favoritePromptText.value = prompt
    if (!formData.free_text_input.includes(prompt)) {
      formData.free_text_input = formData.free_text_input
        ? `${formData.free_text_input.trim()}\n\n${prompt}`
        : prompt
    }

    sessionStorage.removeItem(FAVORITE_PLANNING_KEY)
  } catch (error) {
    console.error('读取收藏规划上下文失败:', error)
    sessionStorage.removeItem(FAVORITE_PLANNING_KEY)
  }
}

const clearFavoriteContext = () => {
  favoriteContext.favorites = []
  if (favoritePromptText.value) {
    formData.free_text_input = formData.free_text_input.replace(favoritePromptText.value, '').trim()
    favoritePromptText.value = ''
  }
  message.success('已移除本次收藏输入')
}

const resetLoading = () => {
  loading.value = false
  loadingProgress.value = 0
  loadingStatus.value = ''
}

// 监听日期变化,自动计算旅行天数
watch([() => formData.start_date, () => formData.end_date], ([start, end]) => {
  if (start && end) {
    const days = end.diff(start, 'day') + 1
    if (days > 0 && days <= 30) {
      formData.travel_days = days
    } else if (days > 30) {
      message.warning('旅行天数不能超过30天')
      formData.end_date = null
    } else {
      message.warning('结束日期不能早于开始日期')
      formData.end_date = null
    }
  }
})

const handleSubmit = async () => {
  if (!formData.start_date || !formData.end_date) {
    message.error('请选择日期')
    return
  }

  loading.value = true
  loadingProgress.value = 0
  loadingStatus.value = '正在初始化...'
  sessionStorage.removeItem('tripPlan')
  sessionStorage.removeItem('tripId')

  try {
    const requestData: TripFormData = {
      city: formData.city,
      start_date: formData.start_date.format('YYYY-MM-DD'),
      end_date: formData.end_date.format('YYYY-MM-DD'),
      travel_days: formData.travel_days,
      transportation: formData.transportation,
      accommodation: formData.accommodation,
      preferences: formData.preferences,
      free_text_input: formData.free_text_input
    }

    const task = await createTripPlanTask(requestData)
    loadingProgress.value = task.progress
    loadingStatus.value = task.stage

    // 后端生成可能持续数分钟；这里用任务 ID 轮询，避免前端请求长时间挂起。
    const pollTask = async () => {
      try {
        const latestTask = await fetchTripPlanTask(task.id)
        loadingProgress.value = latestTask.progress
        loadingStatus.value = latestTask.stage

        if (latestTask.status === 'succeeded' && latestTask.trip_id) {
          const detail = await fetchTrip(latestTask.trip_id)
          sessionStorage.setItem('tripPlan', JSON.stringify(detail.plan_data))
          sessionStorage.setItem('tripId', String(latestTask.trip_id))
          loadingProgress.value = 100
          loadingStatus.value = '行程生成完成'
          message.success('旅行计划生成成功!')
          setTimeout(() => {
            router.push({ path: '/result', query: { tripId: latestTask.trip_id } })
          }, 500)
          return
        }

        if (latestTask.status === 'failed') {
          throw new Error(latestTask.error_message || '生成旅行计划失败')
        }

        window.setTimeout(pollTask, 2500)
      } catch (error: any) {
        message.error(error.message || '生成旅行计划失败,请稍后重试')
        resetLoading()
      }
    }

    window.setTimeout(pollTask, 1000)
  } catch (error: any) {
    message.error(error.message || '生成旅行计划失败,请稍后重试')
    resetLoading()
  }
}

onMounted(applyFavoritePlanningContext)
</script>

<style scoped>
/* Compact day counter beside the date range. */
.days-display-compact {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  padding: 8px 16px;
  color: #ffffff;
}

.days-display-compact .days-value {
  font-size: 24px;
  font-weight: 700;
  margin-right: 4px;
}

.days-display-compact .days-unit {
  font-size: 14px;
}

.preference-editor {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preference-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preference-tags :deep(.ant-tag) {
  margin-inline-end: 0;
  padding: 6px 13px;
  border-radius: 4px;
  border-color: #d9e7e4;
}

.selected-tags {
  min-height: 40px;
  padding: 10px;
  border: 1px solid #e5eaf1;
  border-radius: 6px;
  background: #ffffff;
}

.selected-tags,
.profile-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.selected-tags :deep(.ant-tag) {
  margin-inline-end: 0;
  padding: 4px 10px;
  border-radius: 4px;
  background: #eef7f6;
  border-color: #cde7e3;
  color: #0f766e;
}

/* 提交按钮 */
.submit-button {
  height: 52px;
  font-size: 16px;
  font-weight: 650;
  border: none;
}

.submit-button:hover {
  box-shadow: 0 6px 16px rgba(15, 118, 110, 0.16);
}

.submit-button :deep(.anticon) {
  margin-right: 8px;
}

/* 加载容器 */
.loading-container {
  text-align: center;
  padding: 24px;
}

/* 动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.home-container {
  min-height: calc(100vh - 120px);
  background: #f6f8fb;
  padding: 0 0 40px;
  overflow: visible;
}

.page-header {
  text-align: left;
  margin-bottom: 24px;
  animation: fadeInDown 0.4s ease-out;
}

.page-title {
  font-size: 32px;
  font-weight: 780;
  color: #17202a;
  margin-bottom: 10px;
  text-shadow: none;
  letter-spacing: 0;
}

.page-subtitle {
  max-width: 760px;
  color: #667085;
  font-size: 15px;
  font-weight: 400;
}

.form-card {
  max-width: none;
  margin: 0;
  border-radius: 8px;
  border: 1px solid #e5eaf1;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.035);
  background: #ffffff !important;
  backdrop-filter: none;
}

.form-section {
  margin-bottom: 24px;
  padding: 22px;
}

.favorite-context-panel {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 20px;
  padding: 16px;
  border: 1px solid #cde7e3;
  border-radius: 8px;
  background: #f7fcfb;
}

.context-title {
  margin-bottom: 10px;
  color: #0f766e;
  font-weight: 750;
}

.context-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.planner-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 20px;
  align-items: start;
}

.planner-aside {
  display: grid;
  gap: 16px;
  position: sticky;
  top: 84px;
}

.form-section,
.loading-container {
  background: #f9fbfd;
  border: 1px solid #e5eaf1;
  border-radius: 8px;
}

.form-section:hover {
  transform: none;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
}

.section-header {
  border-bottom-color: #0f766e;
  gap: 10px;
  color: #0f766e;
}

.days-display-compact,
.submit-button {
  background: #0f766e;
  box-shadow: none;
  border-radius: 6px;
}

.loading-container {
  border-style: dashed;
  border-color: #0f766e;
}

.loading-topline {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
  color: #17202a;
  font-weight: 650;
}

.workflow-panel {
  margin-top: 22px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  text-align: left;
}

.workflow-step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  border: 1px solid #e5eaf1;
  border-radius: 6px;
  background: #ffffff;
  color: #667085;
}

.workflow-index {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  background: #edf2f7;
  color: #667085;
  font-weight: 700;
}

.workflow-title {
  color: #17202a;
  font-weight: 700;
}

.workflow-desc {
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.5;
}

.workflow-step.active {
  border-color: #0f766e;
  box-shadow: 0 6px 16px rgba(15, 118, 110, 0.12);
}

.workflow-step.active .workflow-index,
.workflow-step.done .workflow-index {
  background: #0f766e;
  color: #ffffff;
}

.workflow-step.done {
  background: #eef7f6;
  border-color: #cde7e3;
}

.profile-stack {
  display: grid;
  gap: 12px;
}

.profile-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e5eaf1;
}

.profile-row span,
.empty-tip {
  color: #667085;
}

.profile-row strong {
  color: #17202a;
}

.profile-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.aside-workflow {
  display: grid;
  gap: 12px;
}

.aside-step {
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 10px;
}

.aside-index {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 4px;
  background: #eef7f6;
  color: #0f766e;
  font-weight: 750;
}

.aside-step p {
  margin: 4px 0 0;
  color: #667085;
  font-size: 12px;
  line-height: 1.5;
}

.data-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.data-list span {
  padding: 7px 10px;
  border: 1px solid #e5eaf1;
  border-radius: 4px;
  background: #f9fbfd;
  color: #344054;
  font-size: 13px;
}

@media (max-width: 1100px) {
  .planner-layout {
    grid-template-columns: 1fr;
  }

  .planner-aside {
    position: static;
  }
}

/* Keep fixed-format controls compact and square. */
.days-display-compact,
.submit-button,
.loading-container,
.workflow-step {
  border-radius: 6px !important;
}

.form-card,
.form-section {
  border-radius: 8px !important;
}
</style>
