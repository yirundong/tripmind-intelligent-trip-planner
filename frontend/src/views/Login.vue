<template>
  <div class="auth-layout">
    <section class="auth-panel">
      <div class="auth-card">
        <RouterLink class="brand" to="/login">
          <span class="brand-mark">T</span>
          <span>TripMind</span>
        </RouterLink>
        <h1 class="auth-title">欢迎回来</h1>
        <p class="auth-subtitle">普通用户进入旅行规划工作台，管理员登录后可进入系统管理后台。</p>

        <div class="role-hint">
          <div>
            <strong>普通用户</strong>
            <span>规划行程、管理收藏、编辑历史方案</span>
          </div>
          <div>
            <strong>管理员</strong>
            <span>查看用户、任务日志和系统运行统计</span>
          </div>
        </div>

        <a-form layout="vertical" :model="form" @finish="submit">
          <a-form-item label="邮箱或用户名" name="identity" :rules="[{ required: true, message: '请输入邮箱或用户名' }]">
            <a-input v-model:value="form.identity" size="large" placeholder="you@example.com" />
          </a-form-item>
          <a-form-item label="密码" name="password" :rules="[{ required: true, message: '请输入密码' }]">
            <a-input-password v-model:value="form.password" size="large" placeholder="至少6位" />
          </a-form-item>
          <a-button type="primary" html-type="submit" size="large" block :loading="loading">登录</a-button>
        </a-form>

        <p class="auth-footer">
          还没有账号？
          <RouterLink to="/register">立即注册</RouterLink>
        </p>
      </div>
    </section>

    <section class="auth-visual">
      <div class="visual-card">
        <div class="visual-title">把旅行规划变成可管理的个人资产</div>
        <p class="page-description">每一次生成都会沉淀为可编辑、可复制、可追踪的行程记录。</p>
        <div class="visual-grid">
          <div class="visual-tile">行程持久保存</div>
          <div class="visual-tile">地点收藏夹</div>
          <div class="visual-tile">预算和天气汇总</div>
          <div class="visual-tile">AI二次修改入口</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { message } from 'ant-design-vue'
import { loginUser } from '@/services/api'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const form = reactive({
  identity: '',
  password: ''
})

const submit = async () => {
  loading.value = true
  try {
    await loginUser(form)
    message.success('登录成功')
    router.push((route.query.redirect as string) || '/dashboard')
  } catch (error: any) {
    message.error(error.response?.data?.detail || error.message || '登录失败')
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

.role-hint {
  display: grid;
  gap: 10px;
  margin-bottom: 22px;
}

.role-hint > div {
  padding: 12px;
  border: 1px solid #e5eaf1;
  border-left: 3px solid #0f766e;
  border-radius: 6px;
  background: #f9fbfd;
}

.role-hint strong,
.role-hint span {
  display: block;
}

.role-hint span {
  margin-top: 4px;
  color: #667085;
  font-size: 13px;
}
</style>
