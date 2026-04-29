<template>
  <div class="forbidden-page">
    <div class="content-panel forbidden-card">
      <div class="page-kicker">403</div>
      <h1 class="page-title-modern">无权限访问</h1>
      <p class="page-description">当前账号不是管理员，无法进入系统管理后台。</p>
      <a-space style="margin-top: 22px">
        <RouterLink to="/dashboard">
          <a-button type="primary">返回工作台</a-button>
        </RouterLink>
        <RouterLink to="/login">
          <a-button>切换账号</a-button>
        </RouterLink>
      </a-space>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.forbidden-page {
  min-height: calc(100vh - 160px);
  display: grid;
  place-items: center;
}

.forbidden-card {
  width: min(520px, 100%);
}
</style>
