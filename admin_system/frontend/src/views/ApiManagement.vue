<template>
  <div class="api-management">
    <a-page-header
      title="API 管理"
      sub-title="管理与测试系统 API 接口"
    />
    
    <a-card class="api-management-content">
      <a-tabs v-model:activeKey="activeTab">
        <a-tab-pane key="list" tab="API 列表">
          <!-- API列表部分 -->
          <div class="api-list-container">
            <div class="api-list-header">
              <a-button type="primary" @click="showCreateModal">
                添加API接口
              </a-button>
              <a-input-search
                v-model:value="searchKeyword"
                placeholder="搜索 API 接口"
                style="width: 250px; margin-left: 16px;"
                @search="onSearch"
              />
            </div>
            
            <a-table
              :dataSource="filteredEndpoints"
              :columns="columns"
              :loading="loading"
              rowKey="id"
              :pagination="{ pageSize: 10 }"
            >
              <!-- 方法列 -->
              <template #bodyCell="{ column, record }">
                <template v-if="column.dataIndex === 'method'">
                  <a-tag :color="getMethodColor(record.method)">
                    {{ record.method }}
                  </a-tag>
                </template>
                
                <!-- 状态列 -->
                <template v-if="column.dataIndex === 'status'">
                  <a-tag :color="getStatusColor(record.status)">
                    {{ getStatusText(record.status) }}
                  </a-tag>
                </template>
                
                <!-- 权限列 -->
                <template v-if="column.dataIndex === 'permission'">
                  <a-tag :color="getPermissionColor(record.permission)">
                    {{ getPermissionText(record.permission) }}
                  </a-tag>
                </template>
                
                <!-- 操作列 -->
                <template v-if="column.dataIndex === 'action'">
                  <a-space>
                    <a @click="showTestModal(record)">测试</a>
                    <a-divider type="vertical" />
                    <a @click="showEditModal(record)">编辑</a>
                    <a-divider type="vertical" />
                    <a-popconfirm
                      title="确定要删除这个API接口吗?"
                      ok-text="确定"
                      cancel-text="取消"
                      @confirm="deleteEndpoint(record.id)"
                    >
                      <a class="danger-link">删除</a>
                    </a-popconfirm>
                  </a-space>
                </template>
              </template>
            </a-table>
          </div>
        </a-tab-pane>
        
        <a-tab-pane key="test" tab="API 测试">
          <!-- 引入现有的API测试组件 -->
          <ApiTest />
        </a-tab-pane>
      </a-tabs>
    </a-card>
    
    <!-- API编辑模态框 -->
    <a-modal
      v-model:visible="editModalVisible"
      :title="isEdit ? '编辑 API 接口' : '添加 API 接口'"
      width="700px"
      @ok="handleSaveEndpoint"
      @cancel="closeEditModal"
      :okButtonProps="{ loading: saving }"
    >
      <a-form 
        :model="endpointForm" 
        :label-col="{ span: 4 }"
        :wrapper-col="{ span: 20 }"
      >
        <a-form-item label="接口名称" required>
          <a-input v-model:value="endpointForm.name" placeholder="请输入接口名称" />
        </a-form-item>
        
        <a-form-item label="接口路径" required>
          <a-input v-model:value="endpointForm.path" placeholder="请输入接口路径，例如 /api/v1/example" />
        </a-form-item>
        
        <a-form-item label="请求方法" required>
          <a-select v-model:value="endpointForm.method">
            <a-select-option value="GET">GET</a-select-option>
            <a-select-option value="POST">POST</a-select-option>
            <a-select-option value="PUT">PUT</a-select-option>
            <a-select-option value="DELETE">DELETE</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item label="接口状态">
          <a-select v-model:value="endpointForm.status">
            <a-select-option value="active">活跃</a-select-option>
            <a-select-option value="deprecated">已弃用</a-select-option>
            <a-select-option value="maintenance">维护中</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item label="权限要求">
          <a-select v-model:value="endpointForm.permission">
            <a-select-option value="public">公开</a-select-option>
            <a-select-option value="authenticated">需要认证</a-select-option>
            <a-select-option value="admin">仅管理员</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item label="接口描述">
          <a-textarea v-model:value="endpointForm.description" :rows="3" placeholder="请输入接口描述" />
        </a-form-item>
        
        <a-form-item label="请求参数">
          <a-textarea v-model:value="endpointForm.requestSchemaStr" :rows="5" placeholder="请输入JSON格式的请求参数配置" />
          <small>输入JSON格式，例如 {"param1": "string", "param2": "number"}</small>
        </a-form-item>
        
        <a-form-item label="响应格式">
          <a-textarea v-model:value="endpointForm.responseSchemaStr" :rows="5" placeholder="请输入JSON格式的响应参数配置" />
          <small>输入JSON格式，例如 {"code": 200, "data": {"field1": "value"}}</small>
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- API测试模态框 -->
    <a-modal
      v-model:visible="testModalVisible"
      title="测试 API 接口"
      width="800px"
      footer={null}
      @cancel="closeTestModal"
    >
      <div v-if="currentEndpoint.id" class="api-test-modal">
        <div class="api-test-header">
          <a-tag :color="getMethodColor(currentEndpoint.method)" style="margin-right: 8px;">
            {{ currentEndpoint.method }}
          </a-tag>
          <span class="api-path">{{ currentEndpoint.path }}</span>
        </div>
        
        <p class="api-description">{{ currentEndpoint.description }}</p>
        
        <a-divider />
        
        <!-- 参数输入区 -->
        <div class="test-params-area">
          <a-form-item v-if="currentEndpoint.method !== 'GET'" label="请求体">
            <a-textarea
              v-model:value="testRequestBody"
              :rows="8"
              placeholder="输入 JSON 格式的请求体"
            />
            <div style="margin-top: 8px">
              <a-button @click="formatTestJson" size="small">格式化 JSON</a-button>
              <a-button 
                @click="useRequestSchema" 
                size="small" 
                style="margin-left: 8px"
              >
                使用示例
              </a-button>
            </div>
          </a-form-item>
          
          <a-form-item v-if="currentEndpoint.method === 'GET'" label="查询参数">
            <a-row 
              v-for="(param, index) in testQueryParams" 
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
                  @click="removeTestQueryParam(index)"
                >
                  -
                </a-button>
              </a-col>
            </a-row>
            <a-button @click="addTestQueryParam" style="width: 100%">
              添加参数
            </a-button>
          </a-form-item>
          
          <a-form-item label="API 密钥 (可选)">
            <a-select
              v-model:value="testApiKey"
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
              @click="executeTest" 
              :loading="testing"
            >
              发送请求
            </a-button>
          </a-form-item>
        </div>
        
        <a-divider>响应</a-divider>
        
        <!-- 响应区域 -->
        <div v-if="testResponse" class="test-response-container">
          <div class="test-response-header">
            <a-tag :color="getResponseStatusColor(testResponseStatus)">
              状态码: {{ testResponseStatus }}
            </a-tag>
            <span class="test-response-time">
              响应时间: {{ testResponseTime }}ms
            </span>
          </div>
          
          <a-tabs v-model:activeKey="activeResponseTab">
            <a-tab-pane key="body" tab="响应体">
              <pre class="test-response-body">{{ formattedTestResponse }}</pre>
            </a-tab-pane>
            <a-tab-pane key="headers" tab="响应头">
              <a-table 
                :columns="headerColumns" 
                :dataSource="testResponseHeaders" 
                size="small" 
                :pagination="false"
              />
            </a-tab-pane>
          </a-tabs>
        </div>
        
        <div v-else-if="!testing" class="no-response">
          <p>发送请求后将在此处显示响应</p>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import ApiTest from './ApiTest.vue';
import { 
  getApiEndpoints, 
  getApiEndpointById, 
  createApiEndpoint, 
  updateApiEndpoint, 
  deleteApiEndpoint,
  testApiEndpoint
} from '../api/apiManagement';
import { getApiKeys } from '../api/apiKeys';

export default {
  name: 'ApiManagement',
  
  components: {
    ApiTest
  },
  
  setup() {
    // 标签页状态
    const activeTab = ref('list');
    
    // 列表状态
    const loading = ref(false);
    const endpoints = ref([]);
    const searchKeyword = ref('');
    
    // 编辑模态框状态
    const editModalVisible = ref(false);
    const isEdit = ref(false);
    const saving = ref(false);
    const endpointForm = reactive({
      id: '',
      name: '',
      path: '',
      method: 'GET',
      description: '',
      status: 'active',
      permission: 'authenticated',
      requestSchemaStr: '{}',
      responseSchemaStr: '{}'
    });
    
    // 测试模态框状态
    const testModalVisible = ref(false);
    const currentEndpoint = reactive({});
    const testApiKey = ref('');
    const apiKeys = ref([]);
    const testRequestBody = ref('');
    const testQueryParams = ref([{ key: '', value: '' }]);
    const testing = ref(false);
    const testResponse = ref(null);
    const testResponseStatus = ref(0);
    const testResponseTime = ref(0);
    const testResponseHeaders = ref([]);
    const activeResponseTab = ref('body');
    
    // 表格列定义
    const columns = [
      {
        title: '接口名称',
        dataIndex: 'name',
        key: 'name',
      },
      {
        title: '接口路径',
        dataIndex: 'path',
        key: 'path',
      },
      {
        title: '请求方法',
        dataIndex: 'method',
        key: 'method',
        width: 100,
      },
      {
        title: '状态',
        dataIndex: 'status',
        key: 'status',
        width: 100,
      },
      {
        title: '权限',
        dataIndex: 'permission',
        key: 'permission',
        width: 120,
      },
      {
        title: '操作',
        dataIndex: 'action',
        key: 'action',
        width: 150,
      }
    ];
    
    // 响应头表格列定义
    const headerColumns = [
      {
        title: '名称',
        dataIndex: 'name',
        key: 'name',
      },
      {
        title: '值',
        dataIndex: 'value',
        key: 'value',
      }
    ];
    
    // 计算属性 - 过滤后的API端点列表
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
    
    // 计算属性 - 格式化的测试响应
    const formattedTestResponse = computed(() => {
      if (!testResponse.value) return '';
      
      try {
        return JSON.stringify(testResponse.value, null, 2);
      } catch (e) {
        return testResponse.value;
      }
    });
    
    // 方法 - 获取方法颜色
    const getMethodColor = (method) => {
      switch (method) {
        case 'GET': return 'blue';
        case 'POST': return 'green';
        case 'PUT': return 'orange';
        case 'DELETE': return 'red';
        default: return 'default';
      }
    };
    
    // 方法 - 获取状态颜色和文本
    const getStatusColor = (status) => {
      switch (status) {
        case 'active': return 'green';
        case 'deprecated': return 'red';
        case 'maintenance': return 'orange';
        default: return 'default';
      }
    };
    
    const getStatusText = (status) => {
      switch (status) {
        case 'active': return '活跃';
        case 'deprecated': return '已弃用';
        case 'maintenance': return '维护中';
        default: return status;
      }
    };
    
    // 方法 - 获取权限颜色和文本
    const getPermissionColor = (permission) => {
      switch (permission) {
        case 'public': return 'green';
        case 'authenticated': return 'blue';
        case 'admin': return 'purple';
        default: return 'default';
      }
    };
    
    const getPermissionText = (permission) => {
      switch (permission) {
        case 'public': return '公开';
        case 'authenticated': return '需要认证';
        case 'admin': return '仅管理员';
        default: return permission;
      }
    };
    
    // 方法 - 加载API端点列表
    const loadEndpoints = async () => {
      loading.value = true;
      try {
        const result = await getApiEndpoints();
        endpoints.value = result;
      } catch (error) {
        message.error('加载API列表失败');
      } finally {
        loading.value = false;
      }
    };
    
    // 方法 - 加载API密钥列表
    const loadApiKeys = async () => {
      try {
        const result = await getApiKeys();
        apiKeys.value = result;
      } catch (error) {
        message.error('加载API密钥失败');
      }
    };
    
    // 方法 - 搜索
    const onSearch = () => {
      // 已经使用计算属性实现，无需额外处理
    };
    
    // 方法 - 重置端点表单
    const resetEndpointForm = () => {
      endpointForm.id = '';
      endpointForm.name = '';
      endpointForm.path = '';
      endpointForm.method = 'GET';
      endpointForm.description = '';
      endpointForm.status = 'active';
      endpointForm.permission = 'authenticated';
      endpointForm.requestSchemaStr = '{}';
      endpointForm.responseSchemaStr = '{}';
    };
    
    // 方法 - 显示创建模态框
    const showCreateModal = () => {
      resetEndpointForm();
      isEdit.value = false;
      editModalVisible.value = true;
    };
    
    // 方法 - 显示编辑模态框
    const showEditModal = async (endpoint) => {
      try {
        const detailedEndpoint = await getApiEndpointById(endpoint.id);
        
        endpointForm.id = detailedEndpoint.id;
        endpointForm.name = detailedEndpoint.name;
        endpointForm.path = detailedEndpoint.path;
        endpointForm.method = detailedEndpoint.method;
        endpointForm.description = detailedEndpoint.description || '';
        endpointForm.status = detailedEndpoint.status;
        endpointForm.permission = detailedEndpoint.permission;
        
        // 格式化JSON Schema（如果存在）
        if (detailedEndpoint.request_schema) {
          endpointForm.requestSchemaStr = JSON.stringify(detailedEndpoint.request_schema, null, 2);
        } else {
          endpointForm.requestSchemaStr = '{}';
        }
        
        if (detailedEndpoint.response_schema) {
          endpointForm.responseSchemaStr = JSON.stringify(detailedEndpoint.response_schema, null, 2);
        } else {
          endpointForm.responseSchemaStr = '{}';
        }
        
        isEdit.value = true;
        editModalVisible.value = true;
      } catch (error) {
        message.error('获取API详情失败');
      }
    };
    
    // 方法 - 保存端点
    const saveEndpoint = async () => {
      // 检查必填字段
      if (!endpointForm.name || !endpointForm.path) {
        message.error('请填写必填项');
        return;
      }
      
      saving.value = true;
      
      try {
        // 处理JSON Schema
        let requestSchema = {};
        let responseSchema = {};
        
        try {
          if (endpointForm.requestSchemaStr && endpointForm.requestSchemaStr !== '{}') {
            requestSchema = JSON.parse(endpointForm.requestSchemaStr);
          }
          
          if (endpointForm.responseSchemaStr && endpointForm.responseSchemaStr !== '{}') {
            responseSchema = JSON.parse(endpointForm.responseSchemaStr);
          }
        } catch (e) {
          message.error('JSON Schema格式错误');
          saving.value = false;
          return;
        }
        
        // 构建保存数据
        const saveData = {
          name: endpointForm.name,
          path: endpointForm.path,
          method: endpointForm.method,
          description: endpointForm.description,
          status: endpointForm.status,
          permission: endpointForm.permission,
          request_schema: requestSchema,
          response_schema: responseSchema
        };
        
        if (isEdit.value) {
          // 更新
          await updateApiEndpoint(endpointForm.id, saveData);
          message.success('API接口更新成功');
        } else {
          // 创建
          await createApiEndpoint(saveData);
          message.success('API接口创建成功');
        }
        
        // 刷新列表并关闭对话框
        editModalVisible.value = false;
        loadEndpoints();
      } catch (error) {
        if (error.response && error.response.data) {
          message.error(error.response.data.message || '操作失败');
        } else {
          message.error('操作失败');
        }
      } finally {
        saving.value = false;
      }
    };
    
    // 方法 - 删除端点
    const deleteEndpoint = async (endpoint) => {
      try {
        await deleteApiEndpoint(endpoint.id);
        message.success('API接口删除成功');
        loadEndpoints();
      } catch (error) {
        message.error('API接口删除失败');
      }
    };
    
    // 方法 - 显示测试模态框
    const showTestModal = (endpoint) => {
      Object.assign(currentEndpoint, endpoint);
      testApiKey.value = ''; // 重置API密钥
      testRequestBody.value = '{}'; // 重置请求体
      testQueryParams.value = [{ key: '', value: '' }]; // 重置查询参数
      testResponse.value = null; // 重置响应
      testResponseStatus.value = 0;
      testResponseTime.value = 0;
      testResponseHeaders.value = [];
      activeResponseTab.value = 'body';
      testModalVisible.value = true;
    };
    
    // 方法 - 添加测试查询参数
    const addTestQueryParam = () => {
      testQueryParams.value.push({ key: '', value: '' });
    };
    
    // 方法 - 移除测试查询参数
    const removeTestQueryParam = (index) => {
      if (testQueryParams.value.length > 1) {
        testQueryParams.value.splice(index, 1);
      }
    };
    
    // 方法 - 执行测试
    const executeTest = async () => {
      if (!currentEndpoint.id) {
        message.error('未选择API接口');
        return;
      }
      
      testing.value = true;
      
      try {
        // 处理查询参数
        const validQueryParams = testQueryParams.value.filter(param => param.key);
        
        // 处理请求体
        let parsedRequestBody = {};
        try {
          if (testRequestBody.value && testRequestBody.value !== '{}') {
            parsedRequestBody = JSON.parse(testRequestBody.value);
          }
        } catch (e) {
          message.error('请求体JSON格式错误');
          testing.value = false;
          return;
        }
        
        // 构建测试请求数据
        const requestData = {
          endpoint_id: currentEndpoint.id,
          api_key: testApiKey.value,
          body: parsedRequestBody
        };
        
        if (validQueryParams.length > 0) {
          requestData.query_params = {};
          validQueryParams.forEach(param => {
            requestData.query_params[param.key] = param.value;
          });
        }
        
        // 发送测试请求
        const response = await testApiEndpoint(requestData);
        
        // 处理响应
        testResponse.value = response.response_data;
        testResponseStatus.value = response.status_code;
        testResponseTime.value = response.response_time;
        
        // 处理响应头
        testResponseHeaders.value = [];
        if (response.headers) {
          Object.keys(response.headers).forEach(key => {
            testResponseHeaders.value.push({
              name: key,
              value: response.headers[key]
            });
          });
        }
      } catch (error) {
        if (error.response && error.response.data) {
          message.error(error.response.data.message || '测试失败');
        } else {
          message.error('测试失败');
        }
      } finally {
        testing.value = false;
      }
    };
    
    // 方法 - 获取响应状态颜色
    const getResponseStatusColor = (status) => {
      if (status >= 200 && status < 300) return 'green';
      if (status >= 300 && status < 400) return 'blue';
      if (status >= 400 && status < 500) return 'orange';
      if (status >= 500) return 'red';
      return 'default';
    };
    
    // 方法 - 关闭编辑模态框
    const closeEditModal = () => {
      editModalVisible.value = false;
      resetEndpointForm();
    };
    
    // 方法 - 关闭测试模态框
    const closeTestModal = () => {
      testModalVisible.value = false;
    };
    
    // 方法 - 格式化测试JSON
    const formatTestJson = () => {
      try {
        const parsed = JSON.parse(testRequestBody.value);
        testRequestBody.value = JSON.stringify(parsed, null, 2);
      } catch (e) {
        message.error('JSON格式无效');
      }
    };
    
    // 方法 - 使用请求Schema示例
    const useRequestSchema = () => {
      try {
        testRequestBody.value = JSON.stringify(currentEndpoint.request_schema || {}, null, 2);
      } catch (e) {
        testRequestBody.value = '{}';
      }
    };
    
    // 初始化
    onMounted(() => {
      loadEndpoints();
      loadApiKeys();
    });
    
    return {
      // 状态
      activeTab,
      loading,
      endpoints,
      searchKeyword,
      editModalVisible,
      isEdit,
      saving,
      endpointForm,
      testModalVisible,
      currentEndpoint,
      testApiKey,
      apiKeys,
      testRequestBody,
      testQueryParams,
      testing,
      testResponse,
      testResponseStatus,
      testResponseTime,
      testResponseHeaders,
      activeResponseTab,
      
      // 计算属性
      filteredEndpoints,
      formattedTestResponse,
      
      // 常量
      columns,
      headerColumns,
      
      // 方法
      getMethodColor,
      getStatusColor,
      getStatusText,
      getPermissionColor,
      getPermissionText,
      onSearch,
      showCreateModal,
      showEditModal,
      closeEditModal,
      saveEndpoint,
      deleteEndpoint,
      showTestModal,
      addTestQueryParam,
      removeTestQueryParam,
      executeTest,
      getResponseStatusColor,
      formatTestJson,
      useRequestSchema
    };
  }
};
</script>

<style scoped>
.api-management {
  padding: 0 16px;
}

.api-management-content {
  margin-top: 16px;
}

.api-list-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.danger-link {
  color: #ff4d4f;
}

.danger-link:hover {
  color: #ff7875;
}

.api-test-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.api-path {
  font-family: monospace;
  font-size: 16px;
}

.api-description {
  color: #666;
  margin-top: 8px;
}

.test-response-body {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  max-height: 300px;
  overflow: auto;
  font-family: monospace;
}

.test-response-header {
  margin-bottom: 16px;
}

.test-response-time {
  margin-left: 12px;
  color: #666;
}

.no-response {
  text-align: center;
  color: #999;
  padding: 40px 0;
  background-color: #f5f5f5;
  border-radius: 4px;
}
</style> 