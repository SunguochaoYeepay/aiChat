import { createStore } from 'vuex'
import promptTemplateApi from '../api/promptTemplates'
import knowledgeBaseApi from '../api/knowledgeBase'
import authApi from '../api/auth'

export default createStore({
  state: {
    user: null,
    isAuthenticated: false,
    promptTemplates: [],
    promptCategories: [],
    knowledgeBases: []
  },
  
  getters: {
    getUser: state => state.user,
    isAuthenticated: state => state.isAuthenticated,
    getPromptTemplates: state => state.promptTemplates,
    getPromptCategories: state => state.promptCategories,
    getKnowledgeBases: state => state.knowledgeBases
  },
  
  mutations: {
    SET_USER(state, user) {
      state.user = user;
      state.isAuthenticated = !!user;
    },
    SET_PROMPT_TEMPLATES(state, templates) {
      state.promptTemplates = templates;
    },
    SET_PROMPT_CATEGORIES(state, categories) {
      state.promptCategories = categories;
    },
    SET_KNOWLEDGE_BASES(state, knowledgeBases) {
      state.knowledgeBases = knowledgeBases;
    }
  },
  
  actions: {
    // 登录
    async login({ commit }, credentials) {
      try {
        const response = await authApi.login(credentials.username, credentials.password);
        const user = response.data.user;
        commit('SET_USER', user);
        localStorage.setItem('user', JSON.stringify(user));
        return user;
      } catch (error) {
        console.error('登录失败:', error);
        throw error;
      }
    },
    
    // 登出
    async logout({ commit }) {
      try {
        await authApi.logout();
        commit('SET_USER', null);
        localStorage.removeItem('user');
      } catch (error) {
        console.error('登出失败:', error);
        // 即使API调用失败，也清除本地用户状态
        commit('SET_USER', null);
        localStorage.removeItem('user');
        throw error;
      }
    },
    
    // 初始化用户状态
    async initAuth({ commit, dispatch }) {
      // 首先从本地存储恢复用户状态
      const user = localStorage.getItem('user');
      if (user) {
        commit('SET_USER', JSON.parse(user));
        
        // 然后尝试验证当前用户状态是否有效
        try {
          const response = await authApi.getCurrentUser();
          commit('SET_USER', response.data.user);
          localStorage.setItem('user', JSON.stringify(response.data.user));
        } catch (error) {
          // 如果验证失败，清除用户状态
          console.error('验证用户状态失败:', error);
          if (error.response && error.response.status === 401) {
            dispatch('logout');
          }
        }
      }
    },
    
    // 获取所有提示词模板
    async fetchPromptTemplates({ commit }) {
      try {
        const response = await promptTemplateApi.getTemplates();
        commit('SET_PROMPT_TEMPLATES', response.data);
        return response.data;
      } catch (error) {
        console.error('获取提示词模板失败:', error);
        throw error;
      }
    },
    
    // 获取提示词模板分类
    async fetchPromptCategories({ commit }) {
      try {
        const response = await promptTemplateApi.getTemplateCategories();
        commit('SET_PROMPT_CATEGORIES', response.data);
        return response.data;
      } catch (error) {
        console.error('获取提示词模板分类失败:', error);
        throw error;
      }
    },
    
    // 获取所有知识库
    async fetchKnowledgeBases({ commit }) {
      try {
        const response = await knowledgeBaseApi.getKnowledgeBases();
        commit('SET_KNOWLEDGE_BASES', response.data);
        return response.data;
      } catch (error) {
        console.error('获取知识库列表失败:', error);
        throw error;
      }
    },
    
    // 删除知识库
    async deleteKnowledgeBase({ dispatch }, id) {
      try {
        await knowledgeBaseApi.deleteKnowledgeBase(id);
        // 重新加载知识库列表
        dispatch('fetchKnowledgeBases');
        return { status: 'success', message: '知识库删除成功' };
      } catch (error) {
        console.error('删除知识库失败:', error);
        throw error;
      }
    }
  },
  
  modules: {
    // 可以在这里添加模块
  }
}) 