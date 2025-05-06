import axios from 'axios';

// API基础路径
const API_URL = '/api/v1/services/';

/**
 * 服务管理API
 */
const serviceApi = {
  /**
   * 获取所有服务
   */
  getServices() {
    return axios.get(API_URL);
  },
  
  /**
   * 获取单个服务
   * @param {number} id 服务ID
   */
  getService(id) {
    return axios.get(`${API_URL}${id}/`);
  },
  
  /**
   * 创建服务
   * @param {object} serviceData 服务数据
   */
  createService(serviceData) {
    return axios.post(API_URL, serviceData);
  },
  
  /**
   * 更新服务
   * @param {number} id 服务ID
   * @param {object} serviceData 服务数据
   */
  updateService(id, serviceData) {
    return axios.put(`${API_URL}${id}/`, serviceData);
  },
  
  /**
   * 删除服务
   * @param {number} id 服务ID
   */
  deleteService(id) {
    return axios.delete(`${API_URL}${id}/`);
  },
  
  /**
   * 启动服务
   * @param {number} id 服务ID
   */
  startService(id) {
    return axios.post(`${API_URL}${id}/start/`);
  },
  
  /**
   * 停止服务
   * @param {number} id 服务ID
   */
  stopService(id) {
    return axios.post(`${API_URL}${id}/stop/`);
  },
  
  /**
   * 刷新所有服务状态
   */
  refreshServiceStatus() {
    return axios.get(`${API_URL}refresh_status/`);
  }
};

export default serviceApi; 