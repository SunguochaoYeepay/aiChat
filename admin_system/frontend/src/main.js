import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import axios from 'axios'

// 配置Vue Feature flag
window.__VUE_PROD_HYDRATION_MISMATCH_DETAILS__ = false;

// 配置axios
axios.defaults.withCredentials = true; // 允许跨域请求携带cookie
axios.defaults.baseURL = process.env.VUE_APP_API_URL || '/api';

// 添加请求拦截器，确保登录状态在请求之间保持
axios.interceptors.request.use(
  config => {
    // 可以在这里添加认证相关的请求头
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 添加响应拦截器，处理认证错误
axios.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    // 如果响应是401（未授权），清除用户状态并重定向到登录页面
    if (error.response && error.response.status === 401) {
      store.dispatch('logout');
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

const app = createApp(App)

app.use(store)
app.use(router)
app.use(Antd)
app.config.productionTip = false;

app.mount('#app') 