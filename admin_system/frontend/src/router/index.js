import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import PromptManager from '../views/PromptManager.vue'
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/prompts',
    name: 'PromptManager',
    component: PromptManager,
    meta: { requiresAuth: true }
  },
  {
    path: '/knowledge',
    name: 'KnowledgeBase',
    // 使用懒加载
    component: () => import('../views/KnowledgeBase.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/api',
    name: 'ApiTest',
    // 使用懒加载
    component: () => import('../views/ApiTest.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/services',
    name: 'ServiceManager',
    // 使用懒加载
    component: () => import('../views/ServiceManager.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/models',
    name: 'ModelConfigManager',
    // 使用懒加载
    component: () => import('../views/ModelConfigManager.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'UserManager',
    // 使用懒加载
    component: () => import('../views/UserManager.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/api-keys',
    name: 'ApiKeyManager',
    // 使用懒加载
    component: () => import('../views/ApiKeyManager.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 路由守卫，用于验证用户是否已登录
router.beforeEach((to, from, next) => {
  // 初始化用户认证状态
  store.dispatch('initAuth');
  
  // 检查路由是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin);
  const isAuthenticated = store.getters.isAuthenticated;
  const user = store.getters.getUser;
  
  // 如果需要管理员权限，检查用户是否为管理员
  if (requiresAdmin && (!user || !user.is_staff)) {
    next({ name: 'Dashboard' });
  }
  // 如果需要登录但未登录，则重定向到登录页面
  else if (requiresAuth && !isAuthenticated) {
    next({ name: 'Login' });
  } 
  // 如果已登录但访问登录页面，则重定向到首页
  else if (to.name === 'Login' && isAuthenticated) {
    next({ name: 'Dashboard' });
  }
  // 其他情况正常通过
  else {
    next();
  }
});

export default router 