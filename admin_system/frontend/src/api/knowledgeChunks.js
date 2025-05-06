import axios from 'axios';

// API基础路径
const API_URL = '/api/v1/chunks/';

/**
 * 知识库分块API
 */
const knowledgeChunkApi = {
  /**
   * 获取所有知识库分块
   * @param {number} knowledgeBaseId 可选，按知识库过滤
   */
  getChunks(knowledgeBaseId = null) {
    let url = API_URL;
    if (knowledgeBaseId) {
      url += `?knowledge_base=${knowledgeBaseId}`;
    }
    return axios.get(url);
  },
  
  /**
   * 获取单个知识库分块
   * @param {number} id 分块ID
   */
  getChunk(id) {
    return axios.get(`${API_URL}${id}/`);
  },
  
  /**
   * 创建知识库分块
   * @param {object} chunkData 分块数据
   */
  createChunk(chunkData) {
    return axios.post(API_URL, chunkData);
  },
  
  /**
   * 更新知识库分块
   * @param {number} id 分块ID
   * @param {object} chunkData 分块数据
   */
  updateChunk(id, chunkData) {
    return axios.put(`${API_URL}${id}/`, chunkData);
  },
  
  /**
   * 删除知识库分块
   * @param {number} id 分块ID
   */
  deleteChunk(id) {
    return axios.delete(`${API_URL}${id}/`);
  },
  
  /**
   * 向量化知识库分块
   * @param {number} id 分块ID
   */
  vectorizeChunk(id) {
    return axios.post(`${API_URL}${id}/vectorize/`);
  }
};

export default knowledgeChunkApi; 