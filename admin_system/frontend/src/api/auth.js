import axios from 'axios';

// 用户登录
export const login = (username, password) => {
  console.log('Login request:', { username, password });
  console.log('Request URL:', axios.defaults.baseURL + '/auth/login/');
  return axios.post(`/auth/login/`, { username, password })
    .then(response => {
      console.log('Login response:', response.data);
      return response;
    })
    .catch(error => {
      console.error('Login error details:', error.response ? error.response.data : error.message);
      throw error;
    });
};

// 用户登出
export const logout = () => {
  return axios.post(`/auth/logout/`);
};

// 获取当前用户信息
export const getCurrentUser = () => {
  return axios.get(`/auth/user/`);
};

// 获取用户列表
export const getUserList = () => {
  return axios.get(`/auth/users/`);
};

// 创建用户
export const createUser = (userData) => {
  return axios.post(`/auth/users/create/`, userData);
};

// 更新用户
export const updateUser = (userId, userData) => {
  return axios.put(`/auth/users/${userId}/update/`, userData);
};

// 删除用户
export const deleteUser = (userId) => {
  return axios.delete(`/auth/users/${userId}/delete/`);
};

export default {
  login,
  logout,
  getCurrentUser,
  getUserList,
  createUser,
  updateUser,
  deleteUser
}; 