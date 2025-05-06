import axios from 'axios';

// API基础路径，移除/api前缀，因为axios.defaults.baseURL已经是'/api'
const API_URL = '/v1/dashboard/';

/**
 * 仪表盘API
 */
const dashboardApi = {
  /**
   * 获取仪表盘统计数据
   */
  getStatistics() {
    return axios.get(`${API_URL}statistics/`);
  }
};

export default dashboardApi; 