import axios from 'axios';

// 配置axios默认设置
axios.defaults.withCredentials = true;  // 确保跨域请求时携带凭证（Cookie）

// API端点基础URL，确保使用正确的域名和端口
const apiBaseUrl = process.env.VUE_APP_API_URL || '';

// 端点路径，现在baseUrl中已包含/api前缀
const endpointsPath = '/v1/endpoints';

/**
 * 获取所有API端点列表
 */
export const getApiEndpoints = async () => {
  try {
    const fullUrl = `${apiBaseUrl}${endpointsPath}`;
    console.log(`正在请求API端点列表: ${fullUrl}`);
    
    const response = await axios.get(fullUrl);
    console.log('API端点列表响应数据:', response.data);
    
    // 处理API响应数据，确保返回endpoints数组
    if (response.data && response.data.endpoints) {
      return response.data.endpoints;
    } else {
      console.error('API响应格式不正确:', response.data);
      return [];
    }
  } catch (error) {
    // 更详细的错误信息
    console.error('获取API端点列表失败:', error);
    console.error('错误详情:', error.message);
    if (error.response) {
      console.error('响应状态:', error.response.status);
      console.error('响应数据:', error.response.data);
    }
    throw error;
  }
};

/**
 * 获取单个API端点详情
 * @param {number} id API端点ID
 */
export const getApiEndpointById = async (id) => {
  try {
    const response = await axios.get(`${apiBaseUrl}/endpoint/${id}/`);
    return response.data;
  } catch (error) {
    console.error(`获取API端点详情失败 (ID: ${id}):`, error);
    throw error;
  }
};

/**
 * 创建新的API端点
 * @param {Object} endpoint API端点数据
 */
export const createApiEndpoint = async (endpoint) => {
  try {
    const response = await axios.post(`${apiBaseUrl}/v1/endpoints/create`, endpoint);
    return response.data;
  } catch (error) {
    console.error('创建API端点失败:', error);
    throw error;
  }
};

/**
 * 更新API端点
 * @param {number} id API端点ID
 * @param {Object} endpoint API端点数据
 */
export const updateApiEndpoint = async (id, endpoint) => {
  try {
    const response = await axios.put(`${apiBaseUrl}/v1/endpoints/${id}/update`, endpoint);
    return response.data;
  } catch (error) {
    console.error(`更新API端点失败 (ID: ${id}):`, error);
    throw error;
  }
};

/**
 * 删除API端点
 * @param {number} id API端点ID
 */
export const deleteApiEndpoint = async (id) => {
  try {
    const response = await axios.delete(`${apiBaseUrl}/v1/endpoints/${id}/delete`);
    return response.data;
  } catch (error) {
    console.error(`删除API端点失败 (ID: ${id}):`, error);
    throw error;
  }
};

/**
 * 测试API端点
 * @param {Object} testData 测试数据
 */
export const testApiEndpoint = async (testData) => {
  try {
    // 修复：将body字段转换为request_body字符串
    if (testData.body) {
      testData.request_body = JSON.stringify(testData.body);
      delete testData.body;
    }
    
    const response = await axios.post(`${apiBaseUrl}/test/execute/`, testData);
    return response.data;
  } catch (error) {
    console.error('测试API端点失败:', error);
    throw error;
  }
}; 