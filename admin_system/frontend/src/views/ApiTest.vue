<template>
  <div class="api-test">
    <a-page-header
      title="API 测试"
      sub-title="测试系统 API 接口"
    />
    
    <a-card class="api-test-content">
      <a-row :gutter="16">
        <a-col :span="8">
          <a-card title="API 接口列表" class="endpoint-list">
            <a-input-search
              v-model:value="searchKeyword"
              placeholder="搜索 API 接口"
              style="margin-bottom: 16px"
              @search="onSearch"
            />
            
            <a-list
              size="small"
              :loading="loading"
              :data-source="filteredEndpoints"
              :pagination="{ pageSize: 10 }"
            >
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-list-item-meta
                    :title="item.name"
                    :description="item.path"
                  >
                    <template #title>
                      <a @click="selectEndpoint(item)">{{ item.name }}</a>
                    </template>
                  </a-list-item-meta>
                  <template #actions>
                    <a-tag :color="item.method === 'GET' ? 'blue' : item.method === 'POST' ? 'green' : item.method === 'PUT' ? 'orange' : 'red'">
                      {{ item.method }}
                    </a-tag>
                  </template>
                </a-list-item>
              </template>
            </a-list>
          </a-card>
        </a-col>
        
        <a-col :span="16">
          <a-card v-if="currentEndpoint.id" :title="currentEndpoint.name" class="api-form">
            <p>{{ currentEndpoint.description }}</p>
            <a-divider />
            
            <a-form layout="vertical">
              <a-form-item label="请求路径">
                <a-input :value="currentEndpoint.path" disabled />
              </a-form-item>
              
              <a-form-item label="请求方法">
                <a-tag :color="currentEndpoint.method === 'GET' ? 'blue' : currentEndpoint.method === 'POST' ? 'green' : currentEndpoint.method === 'PUT' ? 'orange' : 'red'" style="font-size: 14px; padding: 4px 8px;">
                  {{ currentEndpoint.method }}
                </a-tag>
              </a-form-item>
              
              <a-form-item v-if="currentEndpoint.method !== 'GET'" label="请求体">
                <a-textarea
                  v-model:value="requestBody"
                  :rows="8"
                  placeholder="输入 JSON 格式的请求体"
                />
                <div style="margin-top: 8px">
                  <a-button @click="formatJson" size="small">格式化 JSON</a-button>
                  <a-button 
                    @click="clearRequestBody" 
                    size="small" 
                    style="margin-left: 8px"
                  >
                    清空
                  </a-button>
                </div>
              </a-form-item>
              
              <a-form-item v-if="currentEndpoint.method === 'GET'" label="查询参数">
                <a-row 
                  v-for="(param, index) in queryParams" 
                  :key="index" 
                  :gutter="8" 
                  style="margin-bottom: 8px"
                >
                  <a-col :span="8">
                    <a-input 
                      v-model:value="param.key" 
                      placeholder="参数名" 
                    />
                  </a-col>
                  <a-col :span="14">
                    <a-input 
                      v-model:value="param.value" 
                      placeholder="参数值" 
                    />
                  </a-col>
                  <a-col :span="2">
                    <a-button 
                      type="danger"
                      shape="circle"
                      @click="removeQueryParam(index)"
                    >
                      -
                    </a-button>
                  </a-col>
                </a-row>
                <a-button @click="addQueryParam" style="width: 100%">
                  添加参数
                </a-button>
              </a-form-item>
              
              <a-form-item label="API 密钥 (可选)">
                <a-select
                  v-model:value="selectedApiKey"
                  style="width: 100%"
                  placeholder="选择 API 密钥"
                  allow-clear
                >
                  <a-select-option v-for="key in apiKeys" :key="key.id" :value="key.key">
                    {{ key.name }}
                  </a-select-option>
                </a-select>
              </a-form-item>
              
              <a-form-item>
                <a-button 
                  type="primary" 
                  @click="sendRequest" 
                  :loading="sending"
                >
                  发送请求
                </a-button>
              </a-form-item>
            </a-form>
            
            <a-divider>响应</a-divider>
            
            <div v-if="response" class="response-container">
              <div class="response-header">
                <a-tag :color="getStatusColor(responseStatus)">
                  状态码: {{ responseStatus }}
                </a-tag>
                <span class="response-time">
                  响应时间: {{ responseTime }}ms
                </span>
              </div>
              
              <a-tabs v-model:activeKey="activeResponseTab">
                <a-tab-pane key="body" tab="响应体">
                  <pre class="response-body">{{ formattedResponse }}</pre>
                </a-tab-pane>
                <a-tab-pane key="headers" tab="响应头">
                  <a-table 
                    :columns="headerColumns" 
                    :data-source="responseHeaders" 
                    size="small" 
                    :pagination="false"
                  />
                </a-tab-pane>
              </a-tabs>
            </div>
            
            <div v-else-if="!sending" class="no-response">
              <p>发送请求后将在此处显示响应</p>
            </div>
          </a-card>
          
          <a-empty v-else description="请从左侧选择 API 接口" />
        </a-col>
      </a-row>
    </a-card>
  </div>
</template>

<script>
import { ref, reactive, computed, watch } from 'vue';
import { message } from 'ant-design-vue';

export default {
  name: 'ApiTest',
  
  setup() {
    // 数据
    const loading = ref(false);
    const sending = ref(false);
    const endpoints = ref([]);
    const searchKeyword = ref('');
    const activeResponseTab = ref('body');
    const selectedApiKey = ref('');
    const apiKeys = ref([]);
    const response = ref(null);
    const responseStatus = ref(0);
    const responseTime = ref(0);
    const responseHeaders = ref([]);
    const requestBody = ref('');
    const queryParams = ref([{ key: '', value: '' }]);
    
    const currentEndpoint = reactive({
      id: null,
      name: '',
      path: '',
      method: '',
      description: ''
    });
    
    const headerColumns = [
      {
        title: '名称',
        dataIndex: 'name',
        key: 'name'
      },
      {
        title: '值',
        dataIndex: 'value',
        key: 'value'
      }
    ];
    
    // 计算属性
    const filteredEndpoints = computed(() => {
      if (!searchKeyword.value) {
        return endpoints.value;
      }
      const keyword = searchKeyword.value.toLowerCase();
      return endpoints.value.filter(endpoint => 
        endpoint.name.toLowerCase().includes(keyword) || 
        endpoint.path.toLowerCase().includes(keyword)
      );
    });
    
    const formattedResponse = computed(() => {
      if (!response.value) return '';
      try {
        return JSON.stringify(response.value, null, 2);
      } catch (e) {
        return response.value;
      }
    });
    
    // 方法
    const loadEndpoints = async () => {
      loading.value = true;
      try {
        // 加载实际API接口列表
        const response = await fetch('/api/v1/endpoints');
        const data = await response.json();
        if (data.endpoints) {
          endpoints.value = data.endpoints;
        } else {
          // 如果API没有返回数据，使用示例数据
          initSampleData();
        }
      } catch (error) {
        console.error('加载 API 接口列表失败:', error);
        // 加载失败时使用示例数据
        initSampleData();
      } finally {
        loading.value = false;
      }
    };
    
    const loadApiKeys = async () => {
      try {
        // 加载实际API密钥
        const response = await fetch('/api/v1/api-keys');
        const data = await response.json();
        if (data.api_keys) {
          apiKeys.value = data.api_keys;
        } else {
          // 示例API密钥
          apiKeys.value = [
            { id: 1, name: '默认密钥', key: 'sk-demo-key-12345' },
            { id: 2, name: '测试密钥', key: 'sk-test-key-67890' }
          ];
        }
      } catch (error) {
        console.error('加载 API 密钥失败:', error);
        // 加载失败时使用示例数据
        apiKeys.value = [
          { id: 1, name: '默认密钥', key: 'sk-demo-key-12345' },
          { id: 2, name: '测试密钥', key: 'sk-test-key-67890' }
        ];
      }
    };
    
    const selectEndpoint = (endpoint) => {
      Object.assign(currentEndpoint, endpoint);
      
      // 重置请求和响应
      requestBody.value = '';
      queryParams.value = [{ key: '', value: '' }];
      response.value = null;
      responseStatus.value = 0;
      responseTime.value = 0;
      responseHeaders.value = [];
      
      // 如果有请求体模式，尝试格式化
      if (endpoint.request_schema) {
        try {
          requestBody.value = JSON.stringify(endpoint.request_schema, null, 2);
        } catch (e) {
          // 忽略错误
        }
      }
    };
    
    const onSearch = () => {
      // 不需要特别处理，filteredEndpoints 计算属性会自动更新
    };
    
    const formatJson = () => {
      if (!requestBody.value) return;
      
      try {
        const parsed = JSON.parse(requestBody.value);
        requestBody.value = JSON.stringify(parsed, null, 2);
      } catch (e) {
        message.error('JSON 格式错误: ' + e.message);
      }
    };
    
    const clearRequestBody = () => {
      requestBody.value = '';
    };
    
    const addQueryParam = () => {
      queryParams.value.push({ key: '', value: '' });
    };
    
    const removeQueryParam = (index) => {
      queryParams.value.splice(index, 1);
      if (queryParams.value.length === 0) {
        addQueryParam();
      }
    };
    
    const getStatusColor = (status) => {
      if (status >= 200 && status < 300) return 'green';
      if (status >= 300 && status < 400) return 'blue';
      if (status >= 400 && status < 500) return 'orange';
      if (status >= 500) return 'red';
      return 'default';
    };
    
    const buildQueryString = () => {
      const validParams = queryParams.value.filter(param => param.key && param.value);
      if (validParams.length === 0) return '';
      
      const params = new URLSearchParams();
      validParams.forEach(param => {
        params.append(param.key, param.value);
      });
      
      return `?${params.toString()}`;
    };
    
    const sendRequest = async () => {
      if (!currentEndpoint.id) {
        message.warning('请先选择一个 API 接口');
        return;
      }
      
      sending.value = true;
      const startTime = Date.now();
      
      try {
        // 构建请求 URL
        let url = currentEndpoint.path;
        if (currentEndpoint.method === 'GET') {
          url += buildQueryString();
        }
        
        // 构建请求头
        const headers = {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        };
        
        if (selectedApiKey.value) {
          headers['X-API-Key'] = selectedApiKey.value;
        }
        
        // 发送请求
        const fetchOptions = {
          method: currentEndpoint.method,
          headers: headers
        };
        
        if (currentEndpoint.method !== 'GET' && requestBody.value) {
          try {
            fetchOptions.body = JSON.stringify(JSON.parse(requestBody.value));
          } catch (e) {
            message.warning('请求体不是有效的 JSON 格式，将按原样发送');
            fetchOptions.body = requestBody.value;
          }
        }
        
        const result = await fetch(url, fetchOptions);
        
        // 处理响应
        responseStatus.value = result.status;
        responseTime.value = Date.now() - startTime;
        
        // 处理响应头
        const headers_arr = [];
        result.headers.forEach((value, name) => {
          headers_arr.push({ name, value });
        });
        responseHeaders.value = headers_arr;
        
        // 处理响应体
        const contentType = result.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
          response.value = await result.json();
        } else if (contentType.includes('text/')) {
          response.value = await result.text();
        } else {
          response.value = `[二进制数据 - ${contentType}]`;
        }
        
        message.success(`请求成功，状态码: ${result.status}`);
      } catch (error) {
        message.error('发送请求失败: ' + error.message);
        responseStatus.value = 0;
        responseTime.value = Date.now() - startTime;
        responseHeaders.value = [];
        response.value = { error: error.message };
      } finally {
        sending.value = false;
      }
    };
    
    // 初始化示例数据
    const initSampleData = () => {
      endpoints.value = [
        {
          id: 1,
          name: '获取聊天完成',
          path: '/api/v1/chat/completions',
          method: 'POST',
          description: '发送消息到模型并获取回复',
          request_schema: {
            messages: [
              { role: "system", content: "你是一个有用的AI助手。" },
              { role: "user", content: "你好，请介绍一下自己。" }
            ],
            stream: false,
            template_type: "general"
          }
        },
        {
          id: 2,
          name: '分析图像',
          path: '/api/v1/analyze-image',
          method: 'POST',
          description: '分析图像并获取描述',
          request_schema: {
            image_url: "https://example.com/image.jpg",
            prompt: "描述这张图片"
          }
        },
        {
          id: 3,
          name: '知识库搜索',
          path: '/api/v1/knowledge/search',
          method: 'POST',
          description: '在知识库中搜索相关内容',
          request_schema: {
            query: "如何使用知识库搜索功能?",
            kb_ids: [1, 2],
            limit: 5
          }
        },
        {
          id: 4,
          name: '获取提示词模板',
          path: '/api/v1/templates/',
          method: 'GET',
          description: '获取所有提示词模板'
        },
        {
          id: 5,
          name: '获取知识库列表',
          path: '/api/v1/knowledge/',
          method: 'GET',
          description: '获取所有知识库'
        }
      ];
    };
    
    // 生命周期钩子
    const initData = () => {
      loadEndpoints();
      loadApiKeys();
    };
    
    // 调用初始化
    initData();
    
    return {
      loading,
      sending,
      endpoints,
      searchKeyword,
      currentEndpoint,
      apiKeys,
      selectedApiKey,
      requestBody,
      queryParams,
      response,
      responseStatus,
      responseTime,
      responseHeaders,
      headerColumns,
      activeResponseTab,
      filteredEndpoints,
      formattedResponse,
      selectEndpoint,
      onSearch,
      formatJson,
      clearRequestBody,
      addQueryParam,
      removeQueryParam,
      getStatusColor,
      sendRequest
    };
  }
};
</script>

<style scoped>
.api-test {
  padding: 24px;
}

.api-test-content {
  margin-top: 24px;
}

.endpoint-list {
  height: 100%;
}

.api-form {
  min-height: 600px;
}

.response-container {
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 16px;
  background: #fafafa;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.response-time {
  color: #999;
  font-size: 14px;
}

.response-body {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  overflow: auto;
  max-height: 400px;
  font-family: 'Courier New', Courier, monospace;
  white-space: pre-wrap;
}

.no-response {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  background: #fafafa;
  border-radius: 4px;
}
</style> 