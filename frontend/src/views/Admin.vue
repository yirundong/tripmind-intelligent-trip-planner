<template>
  <div>
    <div class="page-toolbar">
      <div>
        <div class="page-kicker">ADMIN</div>
        <h1 class="page-title-modern">系统管理后台</h1>
        <p class="page-description">查看系统用户、行程、收藏和异步任务运行情况。</p>
      </div>
      <a-space>
        <a-select v-model:value="taskStatus" allow-clear placeholder="任务状态" style="width: 150px" @change="loadTasks">
          <a-select-option value="queued">排队中</a-select-option>
          <a-select-option value="running">运行中</a-select-option>
          <a-select-option value="succeeded">成功</a-select-option>
          <a-select-option value="failed">失败</a-select-option>
        </a-select>
        <a-button @click="loadAll" :loading="loading">刷新</a-button>
      </a-space>
    </div>

    <a-spin :spinning="loading">
      <div class="metric-grid admin-metrics">
        <div class="metric-card">
          <div class="metric-label">用户数</div>
          <div class="metric-value">{{ stats?.user_count || 0 }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">行程数</div>
          <div class="metric-value">{{ stats?.trip_count || 0 }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">收藏数</div>
          <div class="metric-value">{{ stats?.favorite_count || 0 }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">任务总数</div>
          <div class="metric-value">{{ stats?.task_count || 0 }}</div>
        </div>
      </div>

      <div class="metric-grid admin-task-metrics">
        <div class="metric-card soft">
          <div class="metric-label">成功任务</div>
          <div class="metric-value">{{ stats?.succeeded_task_count || 0 }}</div>
        </div>
        <div class="metric-card soft">
          <div class="metric-label">运行/排队</div>
          <div class="metric-value">{{ stats?.running_task_count || 0 }}</div>
        </div>
        <div class="metric-card soft danger">
          <div class="metric-label">失败任务</div>
          <div class="metric-value">{{ stats?.failed_task_count || 0 }}</div>
        </div>
        <div class="metric-card soft">
          <div class="metric-label">任务成功率</div>
          <div class="metric-value">{{ stats?.success_rate || 0 }}%</div>
        </div>
        <div class="metric-card soft">
          <div class="metric-label">平均进度</div>
          <div class="metric-value">{{ stats?.avg_task_progress || 0 }}%</div>
        </div>
        <div class="metric-card soft">
          <div class="metric-label">近7天任务</div>
          <div class="metric-value">{{ stats?.recent_7d_task_count || 0 }}</div>
        </div>
      </div>

      <section class="content-panel city-panel" style="margin-bottom: 18px">
        <h2 class="section-title-modern">热门目的地</h2>
        <div v-if="stats?.popular_cities?.length" class="city-list">
          <div v-for="item in stats.popular_cities" :key="item.city" class="city-item">
            <span>{{ item.city }}</span>
            <a-progress :percent="cityPercent(item.count)" size="small" :show-info="false" />
            <strong>{{ item.count }}</strong>
          </div>
        </div>
        <a-empty v-else description="暂无城市数据" />
      </section>

      <section class="content-panel" style="margin-bottom: 18px">
        <h2 class="section-title-modern">任务日志</h2>
        <a-table :data-source="tasks" :columns="taskColumns" row-key="id" :pagination="{ pageSize: 8 }">
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'status'">
              <a-tag :color="statusColor(record.status)">{{ statusText(record.status) }}</a-tag>
            </template>
            <template v-else-if="column.key === 'progress'">
              <a-progress :percent="record.progress" size="small" />
            </template>
            <template v-else-if="column.key === 'error_message'">
              <span class="error-text">{{ record.error_message || '-' }}</span>
            </template>
          </template>
        </a-table>
      </section>

      <section class="content-panel">
        <h2 class="section-title-modern">用户列表</h2>
        <a-table :data-source="users" :columns="userColumns" row-key="id" :pagination="{ pageSize: 8 }">
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'role'">
              <a-tag :color="record.is_admin ? 'green' : 'blue'">{{ record.is_admin ? '管理员' : '用户' }}</a-tag>
            </template>
            <template v-else-if="column.key === 'active'">
              <a-tag :color="record.is_active ? 'green' : 'red'">{{ record.is_active ? '启用' : '停用' }}</a-tag>
            </template>
          </template>
        </a-table>
      </section>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { message } from 'ant-design-vue'
import { fetchAdminStats, fetchAdminTasks, fetchAdminUsers } from '@/services/api'
import type { AdminStats, AdminTaskSummary, AdminUserSummary } from '@/types'

const loading = ref(false)
const taskStatus = ref<string | undefined>()
const stats = ref<AdminStats | null>(null)
const tasks = ref<AdminTaskSummary[]>([])
const users = ref<AdminUserSummary[]>([])

const taskColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
  { title: '用户', dataIndex: 'username', key: 'username' },
  { title: '城市', dataIndex: 'city', key: 'city' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '进度', dataIndex: 'progress', key: 'progress', width: 160 },
  { title: '阶段', dataIndex: 'stage', key: 'stage' },
  { title: '错误', dataIndex: 'error_message', key: 'error_message' },
  { title: '更新时间', dataIndex: 'updated_at', key: 'updated_at' }
]

const userColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '邮箱', dataIndex: 'email', key: 'email' },
  { title: '角色', key: 'role' },
  { title: '状态', key: 'active' },
  { title: '行程数', dataIndex: 'trip_count', key: 'trip_count' },
  { title: '注册时间', dataIndex: 'created_at', key: 'created_at' }
]

const statusText = (status: string) => {
  const map: Record<string, string> = {
    queued: '排队中',
    running: '运行中',
    succeeded: '成功',
    failed: '失败'
  }
  return map[status] || status
}

const statusColor = (status: string) => {
  const map: Record<string, string> = {
    queued: 'default',
    running: 'processing',
    succeeded: 'success',
    failed: 'error'
  }
  return map[status] || 'default'
}

const loadStats = async () => {
  stats.value = await fetchAdminStats()
}

const loadTasks = async () => {
  tasks.value = await fetchAdminTasks({ status: taskStatus.value, limit: 100 })
}

const loadUsers = async () => {
  users.value = await fetchAdminUsers({ limit: 100 })
}

const cityPercent = (count: number) => {
  const max = Math.max(...(stats.value?.popular_cities.map(item => item.count) || [1]))
  return Math.round((count / max) * 100)
}

const loadAll = async () => {
  loading.value = true
  try {
    await Promise.all([loadStats(), loadTasks(), loadUsers()])
  } catch (error: any) {
    message.error(error.response?.data?.detail || '管理员数据加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)
</script>

<style scoped>
.admin-metrics {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.admin-task-metrics {
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.metric-card.soft {
  background: #f9fbfd;
}

.metric-card.danger .metric-value {
  color: #dc2626;
}

.error-text {
  color: #dc2626;
  max-width: 240px;
  display: inline-block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.city-panel {
  padding-bottom: 10px;
}

.city-list {
  display: grid;
  gap: 12px;
}

.city-item {
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr) 40px;
  gap: 14px;
  align-items: center;
}

.city-item span {
  color: #17202a;
  font-weight: 650;
}

.city-item strong {
  text-align: right;
  color: #0f766e;
}

@media (max-width: 980px) {
  .admin-metrics,
  .admin-task-metrics {
    grid-template-columns: 1fr;
  }
}
</style>
