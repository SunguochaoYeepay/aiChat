<template>
  <div class="login-container">
    <a-card title="系统登录" class="login-card">
      <a-form
        :model="loginForm"
        @finish="handleSubmit"
        layout="vertical"
      >
        <a-form-item
          label="用户名"
          name="username"
          :rules="[{ required: true, message: '请输入用户名' }]"
        >
          <a-input 
            v-model:value="loginForm.username" 
            placeholder="请输入用户名"
            size="large"
          />
        </a-form-item>

        <a-form-item
          label="密码"
          name="password"
          :rules="[{ required: true, message: '请输入密码' }]"
        >
          <a-input-password 
            v-model:value="loginForm.password" 
            placeholder="请输入密码"
            size="large"
          />
        </a-form-item>

        <a-form-item>
          <a-button 
            type="primary" 
            html-type="submit" 
            size="large" 
            block
            :loading="loading"
          >
            登录
          </a-button>
        </a-form-item>
      </a-form>

      <a-alert v-if="error" type="error" :message="error" show-icon />
    </a-card>
  </div>
</template>

<script>
import { defineComponent, reactive, ref } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'LoginView',
  
  setup() {
    const store = useStore();
    const router = useRouter();
    const loading = ref(false);
    const error = ref('');
    
    const loginForm = reactive({
      username: '',
      password: ''
    });
    
    const handleSubmit = async (values) => {
      loading.value = true;
      error.value = '';
      
      try {
        await store.dispatch('login', {
          username: values.username,
          password: values.password
        });
        
        // 登录成功后重定向到首页
        router.push('/');
      } catch (err) {
        if (err.response && err.response.data) {
          error.value = err.response.data.error || '登录失败';
        } else {
          error.value = '登录失败，请检查网络连接';
        }
      } finally {
        loading.value = false;
      }
    };
    
    return {
      loginForm,
      loading,
      error,
      handleSubmit
    };
  }
});
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style> 