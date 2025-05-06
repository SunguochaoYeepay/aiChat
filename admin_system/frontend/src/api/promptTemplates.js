import axios from 'axios';

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true  // 包含 cookies
});

export default {
  /**
   * 获取所有提示词模板
   */
  getTemplates() {
    return apiClient.get('/templates/');
  },

  /**
   * 获取提示词模板分类
   */
  getTemplateCategories() {
    return apiClient.get('/templates/categories/');
  },

  /**
   * 获取单个提示词模板
   * @param {number} id - 模板ID
   */
  getTemplate(id) {
    return apiClient.get(`/templates/${id}/`);
  },

  /**
   * 创建提示词模板
   * @param {Object} template - 模板数据
   */
  createTemplate(template) {
    return apiClient.post('/templates/', template);
  },

  /**
   * 更新提示词模板
   * @param {number} id - 模板ID
   * @param {Object} template - 模板数据
   */
  updateTemplate(id, template) {
    return apiClient.put(`/templates/${id}/`, template);
  },

  /**
   * 删除提示词模板
   * @param {number} id - 模板ID
   */
  deleteTemplate(id) {
    return apiClient.delete(`/templates/${id}/`);
  },

  /**
   * 刷新提示词模板缓存
   */
  refreshCache() {
    return apiClient.post('/templates/refresh_cache/');
  },

  /**
   * 重置提示词模板为默认值
   */
  resetTemplates() {
    return apiClient.post('/templates/reset/');
  },

  /**
   * 批量更新提示词模板
   * @param {Object} templates - 模板数据，格式为 {category: {type: content}}
   */
  batchUpdateTemplates(templates) {
    return apiClient.post('/templates/batch_update/', templates);
  }
}; 