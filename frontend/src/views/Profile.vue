<template>
  <div>
    <div class="page-toolbar">
      <div>
        <div class="page-kicker">PROFILE</div>
        <h1 class="page-title-modern">个人中心</h1>
        <p class="page-description">维护默认城市、交通、住宿和偏好，让后续规划更快开始。</p>
      </div>
    </div>

    <a-spin :spinning="loading">
      <div class="content-panel profile-panel">
        <a-form layout="vertical" :model="form">
          <a-row :gutter="18">
            <a-col :span="12">
              <a-form-item label="用户名"><a-input v-model:value="form.username" /></a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="邮箱"><a-input v-model:value="form.email" disabled /></a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="18">
            <a-col :span="8">
              <a-form-item label="默认城市"><a-input v-model:value="form.default_city" placeholder="例如 上海" /></a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="默认交通">
                <a-select v-model:value="form.default_transportation">
                  <a-select-option value="公共交通">公共交通</a-select-option>
                  <a-select-option value="自驾">自驾</a-select-option>
                  <a-select-option value="步行">步行</a-select-option>
                  <a-select-option value="混合">混合</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="默认住宿">
                <a-select v-model:value="form.default_accommodation">
                  <a-select-option value="经济型酒店">经济型酒店</a-select-option>
                  <a-select-option value="舒适型酒店">舒适型酒店</a-select-option>
                  <a-select-option value="豪华酒店">豪华酒店</a-select-option>
                  <a-select-option value="民宿">民宿</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>
          <a-form-item label="默认偏好">
            <div class="preference-editor">
              <div class="preset-tags">
                <a-checkable-tag
                  v-for="tag in suggestedPreferences"
                  :key="tag"
                  :checked="form.default_preferences.includes(tag)"
                  @change="(checked: boolean) => togglePreference(tag, checked)"
                >
                  {{ tag }}
                </a-checkable-tag>
              </div>

              <div class="selected-tags">
                <a-tag
                  v-for="tag in form.default_preferences"
                  :key="tag"
                  closable
                  @close.prevent="removePreference(tag)"
                >
                  {{ tag }}
                </a-tag>
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
          <a-button type="primary" :loading="saving" @click="save">保存资料</a-button>
        </a-form>
      </div>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { fetchMe, updateMe } from '@/services/api'

const loading = ref(false)
const saving = ref(false)
const customPreference = ref('')
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
  '慢节奏'
]
const form = reactive({
  id: 0,
  email: '',
  username: '',
  avatar_url: '',
  default_city: '',
  default_transportation: '公共交通',
  default_accommodation: '经济型酒店',
  default_preferences: [] as string[],
  is_admin: false
})

const addPreference = (tag: string) => {
  const value = tag.trim()
  if (!value) return
  if (form.default_preferences.includes(value)) {
    message.info('这个偏好已经添加过了')
    return
  }
  form.default_preferences.push(value)
}

const addCustomPreference = () => {
  addPreference(customPreference.value)
  customPreference.value = ''
}

const removePreference = (tag: string) => {
  form.default_preferences = form.default_preferences.filter(item => item !== tag)
}

const togglePreference = (tag: string, checked: boolean) => {
  if (checked) {
    addPreference(tag)
  } else {
    removePreference(tag)
  }
}

const load = async () => {
  loading.value = true
  try {
    Object.assign(form, await fetchMe())
  } finally {
    loading.value = false
  }
}

const save = async () => {
  saving.value = true
  try {
    Object.assign(form, await updateMe(form))
    message.success('资料已更新')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.profile-panel {
  max-width: 980px;
}

.preference-editor {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.preset-tags,
.selected-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preset-tags :deep(.ant-tag) {
  margin-inline-end: 0;
  padding: 5px 12px;
  border-radius: 4px;
  border-color: #d9e7e4;
}

.selected-tags {
  min-height: 34px;
  padding: 12px;
  border: 1px solid #e5eaf1;
  border-radius: 6px;
  background: #f9fbfd;
}

.selected-tags :deep(.ant-tag) {
  margin-inline-end: 0;
  padding: 4px 10px;
  border-radius: 4px;
  background: #eef7f6;
  border-color: #cde7e3;
  color: #0f766e;
}
</style>
