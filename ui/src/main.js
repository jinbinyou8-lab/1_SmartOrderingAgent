import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import { ElMessage } from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'

const app = createApp(App)

// 注册Element Plus
app.use(ElementPlus)

app.config.errorHandler = (err) => {
  try {
    console.error(err)
    ElMessage.error(err?.message || '页面运行出错')
  } catch (e) {
    // ignore
  }
}

app.mount('#app') 
