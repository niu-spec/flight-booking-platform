<template>
  <div class="page-container">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <h1 class="page-title" style="margin:0">消息中心</h1>
      <el-button @click="handleReadAll">全部已读</el-button>
    </div>
    <div v-loading="loading">
      <div v-for="msg in messages" :key="msg.id" class="msg-card page-card" :class="{ unread: !msg.is_read }">
        <div class="msg-header">
          <el-tag size="small">{{ typeMap[msg.notification_type] || '系统' }}</el-tag>
          <span class="msg-time">{{ formatDateTime(msg.created_at) }}</span>
        </div>
        <h3>{{ msg.title }}</h3>
        <p>{{ msg.content }}</p>
        <el-button v-if="!msg.is_read" size="small" text type="primary" @click="handleRead(msg)">标为已读</el-button>
      </div>
      <div v-if="!loading && !messages.length" class="empty-state page-card">暂无消息</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { notificationApi } from '@/api/notification'
import { formatDateTime } from '@/utils/travel'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const messages = ref([])
const typeMap = { order: '订单', payment: '支付', flight: '航班', refund: '退款', system: '系统' }

const fetchList = async () => {
  loading.value = true
  try {
    const res = await notificationApi.getList()
    messages.value = res.results || res
  } finally {
    loading.value = false
  }
}

const handleRead = async (msg) => {
  await notificationApi.read(msg.id)
  msg.is_read = true
}

const handleReadAll = async () => {
  await notificationApi.readAll()
  ElMessage.success('全部已读')
  fetchList()
}

onMounted(fetchList)
</script>

<style scoped>
.msg-card { margin-bottom: 12px; }
.msg-card.unread { border-left: 4px solid var(--primary); }
.msg-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.msg-time { font-size: 12px; color: var(--text-muted); }
.msg-card h3 { margin: 0 0 8px; font-size: 16px; }
.msg-card p { margin: 0; color: var(--text-secondary); font-size: 14px; }
</style>
