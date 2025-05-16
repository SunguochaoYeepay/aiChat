<template>
  <a-layout class="main-layout" v-if="isAuthenticated">
    <a-layout-sider
      v-model:collapsed="collapsed"
      :trigger="null"
      collapsible
      class="main-sider"
    >
      <div class="logo">
        <h2 v-if="!collapsed">设计助手系统</h2>
        <h2 v-else>系统</h2>
      </div>
      
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
      >
        <a-menu-item key="dashboard">
          <template #icon><dashboard-outlined /></template>
          <router-link to="/">控制台</router-link>
        </a-menu-item>
        
        <a-sub-menu key="content-management">
          <template #icon><file-text-outlined /></template>
          <template #title>内容管理</template>
          
          <a-menu-item key="prompts">
            <template #icon><message-outlined /></template>
            <router-link to="/prompts">提示词模板</router-link>
          </a-menu-item>
          
          <a-menu-item key="knowledge">
            <template #icon><database-outlined /></template>
            <router-link to="/knowledge">知识库管理</router-link>
          </a-menu-item>
        </a-sub-menu>
        
        <a-sub-menu key="system-management">
          <template #icon><setting-outlined /></template>
          <template #title>系统管理</template>
          
          <a-menu-item key="services">
            <template #icon><api-outlined /></template>
            <router-link to="/services">服务管理</router-link>
          </a-menu-item>
          
          <a-menu-item key="models">
            <template #icon><experiment-outlined /></template>
            <router-link to="/models">模型配置</router-link>
          </a-menu-item>
          
          <a-menu-item key="users" v-if="isAdmin">
            <template #icon><user-outlined /></template>
            <router-link to="/users">用户管理</router-link>
          </a-menu-item>
          
          <a-menu-item key="api-keys" v-if="isAdmin">
            <template #icon><key-outlined /></template>
            <router-link to="/api-keys">API密钥</router-link>
          </a-menu-item>
        </a-sub-menu>
        
        <a-sub-menu key="api-management-menu">
          <template #icon><code-outlined /></template>
          <template #title>API 管理</template>
          
          <a-menu-item key="api-test">
            <template #icon><experiment-outlined /></template>
            <router-link to="/api">API测试</router-link>
          </a-menu-item>
          
          <a-menu-item key="api-management" v-if="isAdmin">
            <template #icon><api-outlined /></template>
            <router-link to="/api-management">API接口管理</router-link>
          </a-menu-item>
        </a-sub-menu>
      </a-menu>
    </a-layout-sider>
    
    <a-layout>
      <a-layout-header class="main-header">
        <menu-unfold-outlined
          v-if="collapsed"
          class="trigger"
          @click="() => (collapsed = !collapsed)"
        />
        <menu-fold-outlined
          v-else
          class="trigger"
          @click="() => (collapsed = !collapsed)"
        />
        
        <div class="header-right">
          <a-dropdown>
            <a class="user-dropdown" @click.prevent>
              <a-avatar><template #icon><user-outlined /></template></a-avatar>
              <span class="username">{{ username }}</span>
              <down-outlined />
            </a>
            <template #overlay>
              <a-menu>
                <a-menu-item key="user-info">
                  <user-outlined />
                  个人信息
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item key="logout" @click="handleLogout">
                  <logout-outlined />
                  退出登录
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>
      
      <a-layout-content class="main-content">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
  
  <div v-else>
    <router-view />
  </div>
</template>

<script>
import { defineComponent, ref, computed, watch } from 'vue';
import { useStore } from 'vuex';
import { useRoute, useRouter } from 'vue-router';
import {
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  DashboardOutlined,
  FileTextOutlined,
  MessageOutlined,
  DatabaseOutlined,
  SettingOutlined,
  ApiOutlined,
  ExperimentOutlined,
  UserOutlined,
  KeyOutlined,
  CodeOutlined,
  DownOutlined,
  LogoutOutlined
} from '@ant-design/icons-vue';

export default defineComponent({
  name: 'App',
  components: {
    MenuUnfoldOutlined,
    MenuFoldOutlined,
    DashboardOutlined,
    FileTextOutlined,
    MessageOutlined,
    DatabaseOutlined,
    SettingOutlined,
    ApiOutlined,
    ExperimentOutlined,
    UserOutlined,
    KeyOutlined,
    CodeOutlined,
    DownOutlined,
    LogoutOutlined
  },
  setup() {
    const store = useStore();
    const route = useRoute();
    const router = useRouter();
    
    // 侧边栏折叠状态
    const collapsed = ref(false);
    
    // 菜单选中的key
    const selectedKeys = ref(['dashboard']);
    
    // 根据路由更新选中的菜单项
    const updateSelectedMenu = () => {
      const path = route.path;
      if (path === '/') {
        selectedKeys.value = ['dashboard'];
      } else if (path === '/prompts') {
        selectedKeys.value = ['prompts'];
      } else if (path === '/knowledge') {
        selectedKeys.value = ['knowledge'];
      } else if (path === '/services') {
        selectedKeys.value = ['services'];
      } else if (path === '/models') {
        selectedKeys.value = ['models'];
      } else if (path === '/users') {
        selectedKeys.value = ['users'];
      } else if (path === '/api-keys') {
        selectedKeys.value = ['api-keys'];
      } else if (path === '/api') {
        selectedKeys.value = ['api-test'];
      } else if (path === '/api-management') {
        selectedKeys.value = ['api-management'];
      }
    };
    
    // 监听路由变化，更新菜单选中状态
    watch(() => route.path, updateSelectedMenu, { immediate: true });
    
    // 计算属性：是否已登录
    const isAuthenticated = computed(() => store.getters.isAuthenticated);
    
    // 计算属性：是否为管理员
    const isAdmin = computed(() => {
      const user = store.getters.getUser;
      return user && user.is_staff;
    });
    
    // 计算属性：当前用户名
    const username = computed(() => {
      const user = store.getters.getUser;
      return user ? user.username : '';
    });
    
    // 处理退出登录
    const handleLogout = async () => {
      try {
        await store.dispatch('logout');
        router.push('/login');
      } catch (error) {
        console.error('退出登录失败:', error);
      }
    };
    
    return {
      collapsed,
      selectedKeys,
      isAuthenticated,
      isAdmin,
      username,
      handleLogout,
    };
  }
});
</script>

<style>
.main-layout {
  min-height: 100vh;
}

.main-sider {
  overflow: auto;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
}

.logo {
  height: 64px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
}

.main-header {
  background: #fff;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  position: sticky;
  top: 0;
  z-index: 1;
}

.trigger {
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s;
}

.trigger:hover {
  color: #1890ff;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: rgba(0, 0, 0, 0.65);
}

.username {
  margin-right: 4px;
}

.main-content {
  margin-left: 200px;
  overflow: initial;
  transition: margin-left 0.2s;
}

.collapsed .main-content {
  margin-left: 80px;
}
</style> 