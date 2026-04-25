import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import { i18n } from './i18n'
import '@fontsource-variable/inter/index.css'
import '@fontsource/noto-sans-tc/300.css'
import '@fontsource/noto-sans-tc/400.css'
import '@fontsource/noto-sans-tc/500.css'
import '@fontsource/noto-sans-tc/700.css'
import './style.css'
import 'vue-sonner/style.css'
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.use(i18n)
app.use(router)
app.mount('#app')
document.body.classList.add('app-loaded')
setTimeout(() => {
  const loader = document.getElementById('loading-screen')
  if (loader) loader.remove()
}, 300)
