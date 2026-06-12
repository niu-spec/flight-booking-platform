<template>
  <div class="page-container assistant-page">
    <h1 class="page-title">出行助手</h1>
    <p class="page-subtitle">大模型智能客服 + 个性化出行准备清单</p>

    <div class="assistant-layout">
      <div class="page-card chat-panel">
        <div class="chat-header">
          <h3>🤖 智能客服「小飞」</h3>
          <el-tag :type="modeTag.type" size="small" effect="dark">{{ modeTag.text }}</el-tag>
        </div>
        <p v-if="chatMode === 'rule'" class="mode-hint">
          未配置大模型 API Key，当前为规则引擎模式。
          在 backend/.env 中设置 LLM_API_KEY 即可启用真实大模型。
        </p>
        <div class="chat-messages" ref="chatBox">
          <div v-for="(msg, i) in messages" :key="i" class="chat-msg" :class="msg.role">
            <div class="bubble">
              <span v-if="msg.role === 'bot' && msg.mode === 'llm'" class="ai-badge">AI</span>
              {{ msg.text }}
            </div>
          </div>
          <div v-if="chatting" class="chat-msg bot">
            <div class="bubble typing">正在思考...</div>
          </div>
        </div>
        <div class="chat-input">
          <el-input
            v-model="input"
            placeholder="问我任何机票预订问题，支持多轮对话"
            :disabled="chatting"
            @keyup.enter="sendMessage"
          />
          <el-button type="primary" @click="sendMessage" :loading="chatting" :disabled="!input.trim()">
            发送
          </el-button>
        </div>
        <div class="quick-questions">
          <button
            v-for="q in quickQs"
            :key="q"
            type="button"
            class="quick-btn"
            :disabled="chatting"
            @click="askQuick(q)"
          >{{ q }}</button>
        </div>
      </div>

      <div class="page-card checklist-panel">
        <h3>📋 出行准备清单</h3>
        <div v-if="!checklists.length" class="empty-hint">
          出票后将自动生成清单
          <el-button text type="primary" @click="$router.push('/itineraries')">查看行程</el-button>
        </div>
        <div v-for="cl in checklists" :key="cl.id" class="checklist-block">
          <div class="cl-header">
            <span>{{ cl.route }} · {{ cl.flight_no }}</span>
            <span class="cl-progress">{{ doneCount(cl) }}/{{ cl.items.length }}</span>
          </div>
          <label v-for="item in cl.items" :key="item.id" class="cl-item">
            <input type="checkbox" v-model="item.done" @change="saveChecklist(cl)" />
            <span :class="{ done: item.done }">{{ item.text }}</span>
            <el-tag size="small" type="info">{{ item.category }}</el-tag>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { innovationApi } from '@/api/innovation'

const messages = ref([
  {
    role: 'bot',
    text: '您好！我是智能客服「小飞」，由大模型驱动，可以解答退票、改签、优惠券、积分、选座等问题。有什么可以帮您？',
    mode: 'llm'
  }
])
const input = ref('')
const chatting = ref(false)
const chatMode = ref('llm')
const checklists = ref([])
const chatBox = ref(null)

const quickQs = ['如何退票？', '积分怎么用？', '如何选座？', '降价提醒怎么用？', '银卡会员有什么权益？']

const modeTag = computed(() => {
  if (chatMode.value === 'llm') {
    return { type: 'success', text: '大模型在线' }
  }
  return { type: 'info', text: '规则引擎' }
})

const doneCount = (cl) => cl.items.filter(i => i.done).length

const scrollBottom = async () => {
  await nextTick()
  if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
}

const buildHistory = () => {
  return messages.value
    .filter(m => m.role === 'user' || m.role === 'bot')
    .slice(-10)
    .map(m => ({
      role: m.role === 'bot' ? 'assistant' : 'user',
      content: m.text
    }))
}

const sendMessage = async () => {
  const text = input.value.trim()
  if (!text || chatting.value) return
  messages.value.push({ role: 'user', text })
  input.value = ''
  chatting.value = true
  await scrollBottom()
  try {
    const history = buildHistory().slice(0, -1)
    const res = await innovationApi.chat(text, history)
    chatMode.value = res.mode || 'rule'
    messages.value.push({ role: 'bot', text: res.reply, mode: res.mode })
  } finally {
    chatting.value = false
    scrollBottom()
  }
}

const askQuick = (q) => {
  input.value = q
  sendMessage()
}

const fetchChecklists = async () => {
  try {
    const res = await innovationApi.getChecklists()
    checklists.value = res.results || res
  } catch {
    checklists.value = []
  }
}

const saveChecklist = async (cl) => {
  await innovationApi.updateChecklist(cl.itinerary, cl.items)
}

onMounted(fetchChecklists)
</script>

<style scoped>
.assistant-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.chat-header h3 { margin: 0; font-size: 16px; }
.mode-hint {
  font-size: 12px;
  color: var(--warning);
  background: #fff8e6;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 12px;
}
.chat-messages {
  height: 360px;
  overflow-y: auto;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 12px;
}
.chat-msg { margin-bottom: 12px; display: flex; }
.chat-msg.user { justify-content: flex-end; }
.chat-msg.bot { justify-content: flex-start; }
.bubble {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  position: relative;
}
.chat-msg.user .bubble { background: var(--primary); color: #fff; border-bottom-right-radius: 4px; }
.chat-msg.bot .bubble { background: #fff; border: 1px solid var(--border); border-bottom-left-radius: 4px; }
.bubble.typing { color: var(--text-muted); font-style: italic; }
.ai-badge {
  display: inline-block;
  background: linear-gradient(135deg, #7b61ff, #0086f6);
  color: #fff;
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 4px;
  margin-right: 6px;
  vertical-align: middle;
}
.chat-input { display: flex; gap: 8px; }
.quick-questions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.quick-btn {
  border: 1px solid var(--primary-light);
  background: var(--primary-light);
  color: var(--primary);
  padding: 4px 12px;
  border-radius: 14px;
  font-size: 12px;
  cursor: pointer;
}
.quick-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.checklist-panel h3 { margin: 0 0 16px; font-size: 16px; }
.checklist-block { margin-bottom: 20px; }
.cl-header {
  display: flex;
  justify-content: space-between;
  font-weight: 600;
  margin-bottom: 10px;
  font-size: 14px;
}
.cl-progress { color: var(--primary); font-size: 13px; }
.cl-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px dashed var(--border);
  font-size: 14px;
  cursor: pointer;
}
.cl-item span.done { text-decoration: line-through; color: var(--text-muted); }
.empty-hint { text-align: center; color: var(--text-muted); padding: 40px 0; font-size: 14px; }
@media (max-width: 900px) { .assistant-layout { grid-template-columns: 1fr; } }
</style>
