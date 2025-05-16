import axios from 'axios';

// API端点基础URL
const apiBaseUrl = process.env.VUE_APP_API_URL || '';

/**
 * 获取所有API密钥列表
 */
export const getApiKeys = async () => {
  try {
    // 使用正确的API路径，基础URL中已包含'/api'
    const fullUrl = `${apiBaseUrl}/v1/api-keys`;
    console.log(`正在请求API密钥列表: ${fullUrl}`);
    const response = await axios.get(fullUrl);
    if (response.data && response.data.api_keys) {
      return response.data.api_keys;
    }
    return [];
  } catch (error) {
    console.error('获取API密钥列表失败:', error);
    if (error.response) {
      console.error('响应状态:', error.response.status);
      console.error('响应数据:', error.response.data);
    }
    throw error;
  }
};

// 创建API密钥
export const createApiKey = async (apiKeyData) => {
  try {
    const fullUrl = `${apiBaseUrl}/v1/api-keys/create`;
    console.log(`正在创建API密钥: ${fullUrl}`);
    return await axios.post(fullUrl, apiKeyData);
  } catch (error) {
    console.error('创建API密钥失败:', error);
    throw error;
  }
};

// 更新API密钥
export const updateApiKey = async (keyId, apiKeyData) => {
  try {
    const fullUrl = `${apiBaseUrl}/v1/api-keys/${keyId}/update`;
    console.log(`正在更新API密钥: ${fullUrl}`);
    return await axios.put(fullUrl, apiKeyData);
  } catch (error) {
    console.error(`更新API密钥失败 (ID: ${keyId}):`, error);
    throw error;
  }
};

// 删除API密钥
export const deleteApiKey = async (keyId) => {
  try {
    const fullUrl = `${apiBaseUrl}/v1/api-keys/${keyId}/delete`;
    console.log(`正在删除API密钥: ${fullUrl}`);
    return await axios.delete(fullUrl);
  } catch (error) {
    console.error(`删除API密钥失败 (ID: ${keyId}):`, error);
    throw error;
  }
};

const apiKeysApi = {
  getApiKeys,
  createApiKey,
  updateApiKey,
  deleteApiKey
};

export default apiKeysApi; 