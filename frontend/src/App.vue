<template>
  <div id="app">
    <navbar />
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <span class="brand-icon">✈</span>
          <span>机票预约平台</span>
        </div>
        <p class="footer-desc">安心出行 · 智慧预订 · 畅享旅程</p>
        <p class="footer-copy">© 2026 机票预约平台 · 软件系统分析与设计课程项目</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import Navbar from '@/components/Navbar.vue'
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-main {
  flex: 1;
}

.app-footer {
  background: #1a2b3c;
  color: rgba(255, 255, 255, 0.7);
  padding: 32px 20px;
  margin-top: auto;
}

.footer-inner {
  max-width: var(--max-width);
  margin: 0 auto;
  text-align: center;
}

.footer-brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
}

.brand-icon {
  font-size: 22px;
}

.footer-desc {
  font-size: 13px;
  margin: 0 0 12px;
  color: rgba(255, 255, 255, 0.5);
}

.footer-copy {
  font-size: 12px;
  margin: 0;
  color: rgba(255, 255, 255, 0.35);
}
</style>
