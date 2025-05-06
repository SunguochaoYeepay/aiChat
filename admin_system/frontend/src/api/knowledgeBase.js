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
   * 获取所有知识库
   */
  getKnowledgeBases() {
    return apiClient.get('/knowledge/');
  },

  /**
   * 获取单个知识库
   * @param {number} id - 知识库ID
   */
  getKnowledgeBase(id) {
    return apiClient.get(`/knowledge/${id}/`);
  },

  /**
   * 创建知识库
   * @param {Object} knowledgeBase - 知识库数据
   */
  createKnowledgeBase(knowledgeBase) {
    return apiClient.post('/knowledge/', knowledgeBase);
  },

  /**
   * 更新知识库
   * @param {number} id - 知识库ID
   * @param {Object} knowledgeBase - 知识库数据
   */
  updateKnowledgeBase(id, knowledgeBase) {
    return apiClient.put(`/knowledge/${id}/`, knowledgeBase);
  },

  /**
   * 删除知识库
   * @param {number} id - 知识库ID
   */
  deleteKnowledgeBase(id) {
    return apiClient.delete(`/knowledge/${id}/`);
  },

  /**
   * 从目录导入知识库
   * @param {string} directory - 目录路径
   */
  importFromDirectory(directory) {
    return apiClient.post('/knowledge/import_directory/', { directory });
  },

  /**
   * 上传知识库文件
   * @param {File} file - 文件对象
   */
  uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiClient.post('/knowledge/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },

  /**
   * 向量化知识库
   * @param {number} id - 知识库ID
   */
  indexKnowledgeBase(id) {
    return apiClient.post(`/knowledge/${id}/index/`);
  }
}; 