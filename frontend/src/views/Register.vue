<template>
  <div class="auth-layout">
    <section class="auth-panel">
      <div class="auth-card">
        <RouterLink class="brand" to="/login">
          <span class="brand-mark">T</span>
          <span>TripMind</span>
        </RouterLink>
        <h1 class="auth-title">创建账号</h1>
        <p class="auth-subtitle">保存偏好、复用行程、收藏地点，让每一次规划都有迹可循。</p>

        <a-form layout="vertical" :model="form" @finish="submit">
          <a-form-item label="用户名" name="username" :rules="[{ required: true, message: '请输入用户名' }]">
            <a-input v-model:value="form.username" size="large" placeholder="例如：Ariza" />
          </a-form-item>
          <a-form-item label="邮箱" name="email" :rules="[{ required: true, message: '请输入邮箱' }]">
            <a-input v-model:value="form.email" size="large" placeholder="you@example.com" />
          </a-form-item>
          <a-form-item label="密码" name="password" :rules="[{ required: true, min: 6, message: '密码至少6位' }]">
            <a-input-password v-model:value="form.password" size="large" placeholder="至少6位" />
          </a-form-item>
          <a-button type="primary" html-type="submit" size="large" block :loading="loading">注册并进入系统</a-button>
        </a-form>

        <p class="auth-footer">
          已经有账号？
          <RouterLink to="/login">去登录</RouterLink>
        </p>
      </div>
    </section>

    <section class="auth-visual">
      <div class="visual-card">
        <div class="visual-title">从一次生成升级为长期旅行知识库</div>
        <p class="page-description">保存偏好、复用行程、收藏地点，让 AI 规划越来越懂你。</p>
        <div class="visual-grid">
          <div class="visual-tile">默认偏好</div>
          <div class="visual-tile">历史行程</div>
          <div class="visual-tile">目的地探索</div>
          <div class="visual-tile">导出分享</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { registerUser } from '@/services/api'

const router = useRouter()
const loading = ref(false)
const form = reactive({
  username: '',
  email: '',
  password: ''
})

const submit = async () => {
  loading.value = true
  try {
    await registerUser(form)
    message.success('注册成功')
    router.push('/dashboard')
  } catch (error: any) {
    message.error(error.response?.data?.detail || error.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-footer {
  margin-top: 18px;
  color: #667085;
}
</style>
