import axios from 'axios';

// 获取API密钥列表
export const getApiKeys = () => {
  return axios.get(`/v1/api-keys`);
};

// 创建API密钥
export const createApiKey = (apiKeyData) => {
  return axios.post(`/v1/api-keys/create`, apiKeyData);
};

// 更新API密钥
export const updateApiKey = (keyId, apiKeyData) => {
  return axios.put(`/v1/api-keys/${keyId}/update`, apiKeyData);
};

// 删除API密钥
export const deleteApiKey = (keyId) => {
  return axios.delete(`/v1/api-keys/${keyId}/delete`);
};

export default {
  getApiKeys,
  createApiKey,
  updateApiKey,
  deleteApiKey
}; 