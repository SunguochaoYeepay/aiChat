import axios from 'axios';

// API基础路径
const API_URL = '/api/v1/models/';

/**
 * 模型配置API
 */
const modelConfigApi = {
  /**
   * 获取所有模型配置
   */
  getModelConfigs() {
    return axios.get(API_URL);
  },
  
  /**
   * 获取单个模型配置
   * @param {number} id 模型配置ID
   */
  getModelConfig(id) {
    return axios.get(`${API_URL}${id}/`);
  },
  
  /**
   * 创建模型配置
   * @param {object} configData 模型配置数据
   */
  createModelConfig(configData) {
    return axios.post(API_URL, configData);
  },
  
  /**
   * 更新模型配置
   * @param {number} id 模型配置ID
   * @param {object} configData 模型配置数据
   */
  updateModelConfig(id, configData) {
    return axios.put(`${API_URL}${id}/`, configData);
  },
  
  /**
   * 删除模型配置
   * @param {number} id 模型配置ID
   */
  deleteModelConfig(id) {
    return axios.delete(`${API_URL}${id}/`);
  },
  
  /**
   * 激活模型配置
   * @param {number} id 模型配置ID
   */
  activateModelConfig(id) {
    return axios.post(`${API_URL}${id}/activate/`);
  },
  
  /**
   * 重新加载模型
   * @param {number} id 模型配置ID
   */
  reloadModel(id) {
    return axios.post(`${API_URL}${id}/reload_model/`);
  }
};

export default modelConfigApi; 