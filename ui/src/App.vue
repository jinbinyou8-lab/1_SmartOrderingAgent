<template>
  <div id="app">
    <el-container class="main-container">
      <el-header class="header">
        <div class="header-content">
          <img src="https://element-plus.org/images/element-plus-logo.svg" alt="logo" class="logo" style="width: 30px; margin-right: 10px; display: none;">
          <h1>🍽️ 智能点餐助手</h1>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <el-row :gutter="20">
          <!-- 左侧：智能对话区域 -->
          <el-col :span="10">
            <el-card class="chat-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>💬 智能对话</span>
                  <el-tag size="small" type="success">在线</el-tag>
                </div>
              </template>
              
              <!-- 聊天历史记录 -->
              <div class="chat-history" ref="chatHistoryRef">
                <div v-if="chatMessages.length === 0" class="welcome-message">
                  <p>👋 您好！我是您的智能点餐助手。</p>
                  <p>您可以问我：</p>
                  <div class="suggestion-chips">
                    <el-tag class="chip" @click="quickAsk('你们几点营业？')">你们几点营业？</el-tag>
                    <el-tag class="chip" @click="quickAsk('推荐几个不辣的菜')">推荐不辣的菜</el-tag>
                    <el-tag class="chip" @click="quickAsk('能送到清华大学吗？')">能送到清华大学吗？</el-tag>
                  </div>
                </div>
                
                <div v-for="(msg, index) in chatMessages" :key="index" class="message-wrapper" :class="msg.role">
                  <div class="avatar">
                    {{ msg.role === 'user' ? '👤' : '🤖' }}
                  </div>
                  <div class="message-bubble">
                    <div v-if="msg.role === 'assistant'" v-html="formatMessage(msg.content)" class="markdown-content"></div>
                    <div v-else>{{ msg.content }}</div>
                  </div>
                </div>
                
                <div v-if="chatLoading" class="message-wrapper assistant">
                  <div class="avatar">🤖</div>
                  <div class="message-bubble loading-bubble">
                    <div class="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 输入区域 -->
              <div v-if="faqSuggestionsVisible" class="faq-suggestions">
                <div class="faq-suggestions-title">您可能想问：</div>
                <div class="faq-suggestions-list">
                  <el-button
                    v-for="item in faqSuggestions"
                    :key="item.id"
                    type="primary"
                    plain
                    size="small"
                    class="faq-suggestion-btn"
                    @click="selectFaqSuggestion(item)"
                  >
                    {{ item.question }}
                  </el-button>
                </div>
              </div>

              <div class="chat-input-wrapper">
                <el-input
                  v-model="chatQuery"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入您的需求..."
                  class="chat-input"
                  @keyup.enter.native.prevent="sendChatQuery"
                  resize="none"
                />
                <el-button
                  type="primary"
                  @click="sendChatQuery"
                  :loading="chatLoading"
                  class="send-btn"
                  circle
                >
                  <template #icon>
                    <span>➤</span>
                  </template>
                </el-button>
              </div>
            </el-card>
          </el-col>
          
          <!-- 右侧：功能区域 -->
          <el-col :span="14">

            <!-- 预订信息 -->
            <el-card class="reservation-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>📅 预订信息</span>
                  <el-button type="text" @click="loadReservations" :loading="reservationLoading">刷新</el-button>
                </div>
              </template>
              <div class="reservation-body">
                <div v-if="reservationLoading" class="reservation-loading">
                  <el-skeleton :rows="3" animated />
                </div>
                <div v-else-if="reservations.length > 0" class="reservation-list">
                  <div v-for="item in reservations" :key="item.id" class="reservation-item">
                    <div class="reservation-title">
                      <span>预订 #{{ item.id }}</span>
                      <span class="reservation-time">{{ item.arrival_time }}</span>
                    </div>
                    <div class="reservation-meta">
                      <span>👥 {{ item.num_people }} 人</span>
                      <span>🧒 {{ item.num_children }} 儿童</span>
                      <span v-if="item.seat_preference">🪑 {{ item.seat_preference }}</span>
                      <span v-if="item.main_dish_preference">🍲 {{ item.main_dish_preference }}</span>
                    </div>
                    <div v-if="item.other_comments" class="reservation-comments">
                      {{ item.other_comments }}
                    </div>
                  </div>
                </div>
                <el-empty v-else description="暂无预订信息" image-size="60"></el-empty>
              </div>
            </el-card>


            
            <!-- 菜品列表 -->
            <el-card class="menu-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>📋 菜单列表</span>
                  <el-tag size="small" effect="plain">数量: {{ menuItems.length }}</el-tag>
                  <el-button type="text" @click="loadMenuItems" :loading="menuLoading">刷新</el-button>
                </div>
              </template>
              
              <div class="menu-container">
                 <el-alert
                   v-if="menuError"
                   :title="menuError"
                   type="error"
                   :closable="true"
                   show-icon
                   effect="dark"
                   style="margin-bottom: 12px;"
                 />
                 <div v-if="menuLoading" class="loading-state">
                    <el-skeleton :rows="5" animated />
                 </div>
                 
                 <div v-else-if="menuItems.length > 0" class="menu-grid">
                    <div
                      v-for="item in menuItems"
                      :key="item.id"
                      class="menu-item-card"
                      :class="{
                        highlighted: highlightedItems.includes(getItemIdStr(item)),
                        flashing: flashingItems.includes(getItemIdStr(item))
                      }"
                    >
                      <div class="item-badge" v-if="highlightedItems.includes(getItemIdStr(item))">推荐</div>
                      <div class="item-header">
                        <div class="item-name">{{ item.dish_name }}</div>
                        <div class="item-price">{{ item.formatted_price }}</div>
                      </div>
                      <div class="item-tags">
                         <el-tag size="small" effect="plain">{{ item.category }}</el-tag>
                         <el-tag size="small" :type="getSpiceType(item.spice_level)" effect="light">{{ item.spice_text }}</el-tag>
                         <el-tag v-if="item.is_vegetarian" size="small" type="success" effect="light">素食</el-tag>
                      </div>
                      <div class="item-desc" :title="item.description">{{ item.description }}</div>
                    </div>
                 </div>
                 <el-empty v-else description="暂无菜品" />
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>


  </div>
</template>

<script>
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import { chatAPI, deliveryAPI, menuAPI, faqAPI, reservationAPI } from './api/index.js'
import { ElMessage } from 'element-plus'

export default {
  name: 'App',
  setup() {
    // 聊天相关
    const chatQuery = ref('')
    const chatMessages = ref([])
    const chatLoading = ref(false)
    const chatHistoryRef = ref(null)
    const faqSuggestions = ref([])
    const faqSuggestLoading = ref(false)
    let faqSuggestTimer = null

    // 配送相关
    const deliveryAddress = ref('')
    const travelMode = ref("2")
    const deliveryResponse = ref(null)
    const deliveryLoading = ref(false)

    // 菜单相关
    const menuItems = ref([])
    const menuLoading = ref(false)
    const menuError = ref('')
    const highlightedItems = ref([])
    const flashingItems = ref([])
    let autoHighlightTimer = null
    let lastHighlightKey = ''

    // 购物车相关
    const cartItems = ref([])
    const showOrderDialog = ref(false)

    // 预订信息
    const reservations = ref([])
    const reservationLoading = ref(false)

    const cartTotal = computed(() => {
      return cartItems.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
    })

    const cartCount = computed(() => {
      return cartItems.value.reduce((sum, item) => sum + item.quantity, 0)
    })

    const addToCart = (item, quantity = 1) => {
      // 使用 loose equality (==) 来兼容 string/number 类型的 ID
      const existing = cartItems.value.find(i => i.id == item.id)
      if (existing) {
        existing.quantity += quantity
      } else {
        cartItems.value.push({ ...item, quantity })
      }
      ElMessage.success(`已将 ${item.dish_name} 加入购物车`)
    }

    const addToCartById = (id, quantity = 1) => {
      const item = menuItems.value.find(i => i.id == id)
      if (item) {
        addToCart(item, quantity)
      } else {
        console.warn('Item not found for cart:', id)
      }
    }

    const updateQuantity = (item, delta) => {
      const newQty = item.quantity + delta
      if (newQty <= 0) {
        // 同样使用 loose equality (==)
        cartItems.value = cartItems.value.filter(i => i.id != item.id)
      } else {
        item.quantity = newQty
      }
    }

    const placeOrder = () => {
      if (cartItems.value.length === 0) return
      showOrderDialog.value = true
    }

    const confirmOrder = () => {
      cartItems.value = []
      showOrderDialog.value = false
      ElMessage.success('下单成功！厨房正在准备您的美食')
    }

    // 滚动到底部
    const scrollToBottom = async () => {
      await nextTick()
      if (chatHistoryRef.value) {
        chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
      }
    }

    // 格式化消息
    const formatMessage = (content) => {
      if (!content) return ''
      return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br/>')
    }

    // 快速提问
    const quickAsk = (text) => {
      chatQuery.value = text
      sendChatQuery()
    }

    const fetchFaqSuggestions = async (query) => {
      const q = (query || '').trim()
      if (!q) {
        faqSuggestions.value = []
        return
      }
      faqSuggestLoading.value = true
      try {
        const res = await faqAPI.suggest(q, 6)
        const items = Array.isArray(res?.suggestions) ? res.suggestions : []
        faqSuggestions.value = items
      } catch (e) {
        faqSuggestions.value = []
      } finally {
        faqSuggestLoading.value = false
      }
    }

    const selectFaqSuggestion = async (item) => {
      if (!item?.question || !item?.answer) return
      if (chatLoading.value) return
      const question = item.question
      const answer = item.answer
      chatMessages.value.push({ role: 'user', content: question })
      chatMessages.value.push({ role: 'assistant', content: answer })
      chatQuery.value = ''
      faqSuggestions.value = []
      scrollToBottom()
    }

    // 发送消息
    const sendChatQuery = async () => {
      if (!chatQuery.value.trim() || chatLoading.value) return
      
      const query = chatQuery.value
      faqSuggestions.value = []
      chatMessages.value.push({ role: 'user', content: query })
      chatQuery.value = ''
      chatLoading.value = true
      scrollToBottom()

      let hasCreatedMessage = false

      await chatAPI.sendStreamMessage(
        query,
        (data) => {
          if (data?.type === 'recommendation' || data?.menu_ids) {
            highlightRecommendedItems(data.menu_ids)
          }

          if (data?.type === 'action' && data?.action === 'add_to_cart') {
            const items = Array.isArray(data.items) ? data.items : []
            if (items.length > 0) {
              for (const item of items) {
                if (item?.id != null) {
                  addToCartById(item.id, item.quantity || 1)
                }
              }
            } else if (data?.data?.menu_id != null) {
              addToCartById(data.data.menu_id, data.data.quantity || 1)
            }
          }

          const token =
            data?.type === 'token'
              ? (typeof data?.content === 'string'
                  ? data.content
                  : typeof data?.data === 'string'
                    ? data.data
                    : '')
              : ''
          const err = data?.type === 'error' ? data?.error : data?.error

          if (token) {
            if (!hasCreatedMessage) {
              chatLoading.value = false
              chatMessages.value.push({ role: 'assistant', content: '' })
              hasCreatedMessage = true
            }
            const currentMsg = chatMessages.value[chatMessages.value.length - 1]
            currentMsg.content += token
            scheduleAutoHighlightFromText(currentMsg.content)
            scrollToBottom()
          }

          if (err) {
            if (!hasCreatedMessage) {
              chatLoading.value = false
              chatMessages.value.push({ role: 'assistant', content: '' })
              hasCreatedMessage = true
            }
            const currentMsg = chatMessages.value[chatMessages.value.length - 1]
            currentMsg.content += `\n[错误: ${err}]`
          }
        },
        (error) => {
          console.error('Chat error:', error)
          chatLoading.value = false
          
          if (!hasCreatedMessage) {
            chatMessages.value.push({ role: 'assistant', content: '' })
            hasCreatedMessage = true
          }
          const currentMsg = chatMessages.value[chatMessages.value.length - 1]
          currentMsg.content += '\n[网络错误，请检查连接]'
        },
        () => {
          chatLoading.value = false
          scrollToBottom()
        }
      )
    }

    // 配送查询
    const checkDelivery = async () => {
      if (!deliveryAddress.value.trim()) return
      deliveryLoading.value = true
      try {
        const response = await deliveryAPI.checkRange(deliveryAddress.value, travelMode.value)
        deliveryResponse.value = response
      } catch (e) {
        // 错误处理
      } finally {
        deliveryLoading.value = false
      }
    }

    // 加载菜单
    const getMenuItemsFromResponse = (response) => {
      if (!response) return []
      if (Array.isArray(response)) return response
      if (Array.isArray(response.menu_items)) return response.menu_items
      if (Array.isArray(response.menuItems)) return response.menuItems
      const data = response.data
      if (Array.isArray(data)) return data
      if (Array.isArray(data?.menu_items)) return data.menu_items
      if (Array.isArray(data?.menuItems)) return data.menuItems
      if (Array.isArray(data?.items)) return data.items
      return []
    }

    const loadMenuItems = async () => {
      menuLoading.value = true
      menuError.value = ''
      try {
        const response = await menuAPI.getMenuList()
        const items = getMenuItemsFromResponse(response)
        menuItems.value = items
        if (!items.length && response?.message) {
          ElMessage.warning(response.message)
        }
      } catch (e) {
        menuItems.value = []
        menuError.value = e?.message || '菜品获取失败'
        ElMessage.error(menuError.value)
      } finally {
        menuLoading.value = false
      }
    }

    const loadReservations = async () => {
      reservationLoading.value = true
      try {
        const res = await reservationAPI.list(10)
        reservations.value = Array.isArray(res?.reservations) ? res.reservations : []
      } catch (e) {
        reservations.value = []
        ElMessage.error(e?.message || '预订信息获取失败')
      } finally {
        reservationLoading.value = false
      }
    }

    // 高亮推荐
    const highlightRecommendedItems = (ids) => {
      if (!ids) return
      const normalized = (Array.isArray(ids) ? ids : [])
        .map(id => (id == null ? '' : String(id)))
        .filter(Boolean)
      const unique = Array.from(new Set(normalized)).sort()
      const key = unique.join(',')
      if (!key || key === lastHighlightKey) return
      lastHighlightKey = key
      highlightedItems.value = unique
      flashingItems.value = unique
      window.setTimeout(() => {
        flashingItems.value = []
      }, 900)
      // 滚动到菜单区域
      // 这里如果需要可以做自动滚动，但现在布局是左右分栏，可能不需要强制滚动
    }

    const extractMenuIdsFromText = (text) => {
      if (!text) return []
      const ids = []
      for (const item of menuItems.value) {
        if (!item?.dish_name || item?.id == null) continue
        if (text.includes(item.dish_name)) ids.push(String(item.id))
      }
      return ids
    }

    const getItemIdStr = (item) => {
      if (!item || item.id == null) return ''
      return String(item.id)
    }

    const scheduleAutoHighlightFromText = (text) => {
      if (autoHighlightTimer) window.clearTimeout(autoHighlightTimer)
      autoHighlightTimer = window.setTimeout(() => {
        const ids = extractMenuIdsFromText(text)
        if (ids.length) highlightRecommendedItems(ids)
      }, 240)
    }

    const getSpiceType = (level) => {
      return ['', 'success', 'warning', 'danger'][level] || ''
    }

    const cleanupBrowserCaches = async () => {
      try {
        if ('serviceWorker' in navigator) {
          const regs = await navigator.serviceWorker.getRegistrations()
          for (const reg of regs) {
            try {
              await reg.unregister()
            } catch (e) {
              // ignore
            }
          }
        }
        if ('caches' in window) {
          const keys = await window.caches.keys()
          for (const k of keys) {
            try {
              await window.caches.delete(k)
            } catch (e) {
              // ignore
            }
          }
        }
      } catch (e) {
        // ignore
      }
    }

    onMounted(() => {
      cleanupBrowserCaches()
      loadMenuItems()
      loadReservations()
    })

    watch(
      chatQuery,
      (val) => {
        if (faqSuggestTimer) window.clearTimeout(faqSuggestTimer)
        const q = (val || '').trim()
        if (!q || q.length < 2 || chatLoading.value) {
          faqSuggestions.value = []
          return
        }
        faqSuggestTimer = window.setTimeout(() => {
          fetchFaqSuggestions(q)
        }, 220)
      },
      { flush: 'post' }
    )

    return {
      chatQuery,
      chatMessages,
      chatLoading,
      chatHistoryRef,
      sendChatQuery,
      quickAsk,
      formatMessage,
      faqSuggestions,
      faqSuggestLoading,
      selectFaqSuggestion,
      faqSuggestionsVisible: computed(() => !faqSuggestLoading.value && faqSuggestions.value.length > 0),
      
      deliveryAddress,
      travelMode,
      deliveryResponse,
      deliveryLoading,
      checkDelivery,
      
      menuItems,
      menuLoading,
      menuError,
      highlightedItems,
      flashingItems,
      loadMenuItems,
      getSpiceType,
      getItemIdStr,

      cartItems,
      cartTotal,
      cartCount,
      addToCart,
      updateQuantity,
      placeOrder,
      showOrderDialog,
      confirmOrder,

      reservations,
      reservationLoading,
      loadReservations
    }
  }
}
</script>

<style>
/* 全局重置 */
body {
  margin: 0;
  background-color: #f0f2f5;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 头部 */
.header {
  background: white;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  z-index: 10;
}

.header h1 {
  font-size: 20px;
  margin: 0;
  color: #303133;
}

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 20px;
  overflow: hidden;
}

.el-row, .el-col {
  height: 100%;
}

/* 卡片通用 */
.el-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: none;
  border-radius: 12px;
}

.el-card__body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

/* 聊天卡片 */
.chat-card .el-card__body {
  padding: 0;
  background-color: #f7f7f7;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.welcome-message {
  text-align: center;
  color: #909399;
  margin-top: 40px;
}

.suggestion-chips {
  margin-top: 15px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

.chip {
  cursor: pointer;
  transition: all 0.2s;
}

.chip:hover {
  transform: translateY(-2px);
}

.message-wrapper {
  display: flex;
  gap: 10px;
  max-width: 85%;
}

.message-wrapper.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  font-size: 20px;
  flex-shrink: 0;
}

.message-bubble {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  line-height: 1.5;
  font-size: 14px;
  color: #303133;
}

.message-wrapper.user .message-bubble {
  background: #409EFF;
  color: white;
  border-bottom-right-radius: 2px;
}

.message-wrapper.assistant .message-bubble {
  border-top-left-radius: 2px;
}

.chat-input-wrapper {
  padding: 15px;
  background: white;
  display: flex;
  gap: 10px;
  align-items: flex-end;
  border-top: 1px solid #eee;
}

.faq-suggestions {
  background: white;
  border-top: 1px solid #eee;
  padding: 10px 15px;
}

.faq-suggestions-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.faq-suggestions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.faq-suggestion-btn {
  border-radius: 999px;
}

.typing-indicator span {
  display: inline-block;
  width: 6px;
  height: 6px;
  background-color: #909399;
  border-radius: 50%;
  margin: 0 2px;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 功能区布局 */
.reservation-card {
  height: auto;
  margin-bottom: 20px;
}

.reservation-card .el-card__body {
  padding: 20px;
}

.reservation-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.reservation-item {
  border: 1px solid #ebeef5;
  border-radius: 10px;
  padding: 12px;
  background: #fff;
}

.reservation-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  margin-bottom: 8px;
}

.reservation-time {
  font-weight: 400;
  font-size: 12px;
  color: #909399;
}

.reservation-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 13px;
  color: #606266;
}

.reservation-comments {
  margin-top: 8px;
  font-size: 13px;
  color: #303133;
  background: #f7f7f7;
  border-radius: 8px;
  padding: 8px 10px;
}


.menu-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.menu-container {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.menu-item-card {
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.menu-item-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.menu-item-card.highlighted {
  border-color: #F56C6C;
  background-color: #fef0f0;
}

.menu-item-card.flashing {
  animation: flashPulse 0.9s ease-in-out 1;
}

@keyframes flashPulse {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 rgba(245, 108, 108, 0);
  }
  35% {
    transform: scale(1.02);
    box-shadow: 0 0 0 8px rgba(245, 108, 108, 0.18);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 rgba(245, 108, 108, 0);
  }
}

.item-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: #F56C6C;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-bottom-left-radius: 8px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-weight: 600;
}

.item-price {
  color: #F56C6C;
}

.item-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}

.item-desc {
  font-size: 12px;
  color: #909399;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.mode-select {
  display: flex;
  justify-content: flex-end;
}



/* 菜单项加购按钮 */
.item-action-btn {
  position: absolute;
  bottom: 10px;
  right: 10px;
}


</style> 
