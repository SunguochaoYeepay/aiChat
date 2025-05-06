<template>
  <div class="api-key-manager-container">
    <a-card title="API密钥管理" :bordered="false">
      <template #extra>
        <a-button type="primary" @click="showCreateModal">
          <template #icon><plus-outlined /></template>
          创建API密钥
        </a-button>
      </template>

      <a-table
        :columns="columns"
        :data-source="apiKeys"
        :loading="loading"
        :pagination="{ pageSize: 10 }"
        rowKey="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'is_active'">
            <a-tag :color="record.is_active ? 'green' : 'red'">
              {{ record.is_active ? '激活' : '禁用' }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'action'">
            <a-space>
              <a-button type="link" @click="copyApiKey(record)">复制</a-button>
              <a-button type="link" @click="showEditModal(record)">编辑</a-button>
              <a-popconfirm
                title="确定要删除这个API密钥吗？"
                ok-text="确定"
                cancel-text="取消"
                @confirm="deleteApiKey(record)"
              >
                <a-button type="link" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>

      <!-- 创建API密钥弹窗 -->
      <a-modal
        v-model:visible="createModalVisible"
        title="创建API密钥"
        @ok="handleCreateApiKey"
        :confirmLoading="modalLoading"
      >
        <a-form
          :model="apiKeyForm"
          :rules="rules"
          ref="createFormRef"
          layout="vertical"
        >
          <a-form-item label="名称" name="name">
            <a-input v-model:value="apiKeyForm.name" placeholder="请输入API密钥名称" />
          </a-form-item>
          <a-form-item label="描述" name="description">
            <a-textarea v-model:value="apiKeyForm.description" placeholder="请输入描述" rows="4" />
          </a-form-item>
          <a-form-item label="过期时间" name="expires_at">
            <a-date-picker
              v-model:value="apiKeyForm.expires_at"
              show-time
              format="YYYY-MM-DD HH:mm:ss"
              placeholder="选择过期时间（可选）"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="允许的IP地址" name="allowed_ips">
            <a-textarea 
              v-model:value="apiKeyForm.allowed_ips" 
              placeholder="请输入允许的IP地址，多个IP用逗号分隔（可选）" 
              rows="2"
            />
          </a-form-item>
          <a-form-item label="速率限制（每分钟请求数）" name="rate_limit_override">
            <a-input-number 
              v-model:value="apiKeyForm.rate_limit_override" 
              placeholder="留空表示使用接口默认限制"
              style="width: 100%"
            />
          </a-form-item>
        </a-form>
      </a-modal>

      <!-- 编辑API密钥弹窗 -->
      <a-modal
        v-model:visible="editModalVisible"
        title="编辑API密钥"
        @ok="handleUpdateApiKey"
        :confirmLoading="modalLoading"
      >
        <a-form
          :model="apiKeyForm"
          :rules="rules"
          ref="editFormRef"
          layout="vertical"
        >
          <a-form-item label="名称" name="name">
            <a-input v-model:value="apiKeyForm.name" placeholder="请输入API密钥名称" />
          </a-form-item>
          <a-form-item label="描述" name="description">
            <a-textarea v-model:value="apiKeyForm.description" placeholder="请输入描述" rows="4" />
          </a-form-item>
          <a-form-item label="过期时间" name="expires_at">
            <a-date-picker
              v-model:value="apiKeyForm.expires_at"
              show-time
              format="YYYY-MM-DD HH:mm:ss"
              placeholder="选择过期时间（可选）"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="允许的IP地址" name="allowed_ips">
            <a-textarea 
              v-model:value="apiKeyForm.allowed_ips" 
              placeholder="请输入允许的IP地址，多个IP用逗号分隔（可选）" 
              rows="2"
            />
          </a-form-item>
          <a-form-item label="速率限制（每分钟请求数）" name="rate_limit_override">
            <a-input-number 
              v-model:value="apiKeyForm.rate_limit_override" 
              placeholder="留空表示使用接口默认限制"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item name="is_active">
            <a-checkbox v-model:checked="apiKeyForm.is_active">激活</a-checkbox>
          </a-form-item>
        </a-form>
      </a-modal>

      <!-- 显示新创建的API密钥弹窗 -->
      <a-modal
        v-model:visible="keyDisplayModalVisible"
        title="API密钥创建成功"
        :closable="false"
        :maskClosable="false"
        :footer="null"
      >
        <div class="key-display">
          <p class="warning-text">⚠️ 请记下您的API密钥，此密钥只会显示一次！</p>
          <a-input-password
            v-model:value="newApiKey"
            readonly
            :addonAfter="copyAddon"
          />
          <div class="key-actions">
            <a-button type="primary" @click="handleApiKeyCopied">
              我已复制密钥
            </a-button>
          </div>
        </div>
      </a-modal>
    </a-card>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, onMounted, h } from 'vue';
import { message } from 'ant-design-vue';
import { PlusOutlined, CopyOutlined } from '@ant-design/icons-vue';
import { getApiKeys, createApiKey, updateApiKey, deleteApiKey } from '../api/apiKeys';

export default defineComponent({
  name: 'ApiKeyManager',
  components: {
    PlusOutlined,
    CopyOutlined
  },
  setup() {
    const apiKeys = ref([]);
    const loading = ref(false);
    const createModalVisible = ref(false);
    const editModalVisible = ref(false);
    const keyDisplayModalVisible = ref(false);
    const modalLoading = ref(false);
    const currentApiKeyId = ref(null);
    const newApiKey = ref('');
    const createFormRef = ref(null);
    const editFormRef = ref(null);
    
    const columns = [
      { title: 'ID', dataIndex: 'id', key: 'id' },
      { title: '名称', dataIndex: 'name', key: 'name' },
      { title: 'API密钥', dataIndex: 'key', key: 'key' },
      { title: '状态', dataIndex: 'is_active', key: 'is_active' },
      { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
      { title: '调用次数', dataIndex: 'call_count', key: 'call_count' },
      { title: '操作', dataIndex: 'action', key: 'action' }
    ];
    
    const apiKeyForm = reactive({
      name: '',
      description: '',
      expires_at: null,
      allowed_ips: '',
      rate_limit_override: null,
      is_active: true
    });
    
    const rules = {
      name: [{ required: true, message: '请输入API密钥名称', trigger: 'blur' }]
    };
    
    const copyAddon = h(CopyOutlined, {
      onClick: () => {
        navigator.clipboard.writeText(newApiKey.value)
          .then(() => message.success('API密钥已复制到剪贴板'))
          .catch(() => message.error('复制失败，请手动复制'));
      }
    });
    
    // 获取API密钥列表
    const fetchApiKeys = async () => {
      loading.value = true;
      try {
        const response = await getApiKeys();
        apiKeys.value = response.data.api_keys;
      } catch (error) {
        console.error('获取API密钥列表失败:', error);
        message.error('获取API密钥列表失败');
      } finally {
        loading.value = false;
      }
    };
    
    // 显示创建API密钥弹窗
    const showCreateModal = () => {
      resetApiKeyForm();
      createModalVisible.value = true;
    };
    
    // 显示编辑API密钥弹窗
    const showEditModal = (apiKey) => {
      resetApiKeyForm();
      currentApiKeyId.value = apiKey.id;
      
      apiKeyForm.name = apiKey.name;
      apiKeyForm.description = apiKey.description || '';
      apiKeyForm.expires_at = apiKey.expires_at ? new Date(apiKey.expires_at) : null;
      apiKeyForm.allowed_ips = apiKey.allowed_ips || '';
      apiKeyForm.rate_limit_override = apiKey.rate_limit_override;
      apiKeyForm.is_active = apiKey.is_active;
      
      editModalVisible.value = true;
    };
    
    // 重置表单
    const resetApiKeyForm = () => {
      apiKeyForm.name = '';
      apiKeyForm.description = '';
      apiKeyForm.expires_at = null;
      apiKeyForm.allowed_ips = '';
      apiKeyForm.rate_limit_override = null;
      apiKeyForm.is_active = true;
      currentApiKeyId.value = null;
    };
    
    // 创建API密钥
    const handleCreateApiKey = async () => {
      try {
        await createFormRef.value.validate();
        modalLoading.value = true;
        
        const formData = {
          name: apiKeyForm.name,
          description: apiKeyForm.description,
          is_active: apiKeyForm.is_active
        };
        
        if (apiKeyForm.expires_at) {
          formData.expires_at = apiKeyForm.expires_at.toISOString();
        }
        
        if (apiKeyForm.allowed_ips) {
          formData.allowed_ips = apiKeyForm.allowed_ips;
        }
        
        if (apiKeyForm.rate_limit_override) {
          formData.rate_limit_override = apiKeyForm.rate_limit_override;
        }
        
        const response = await createApiKey(formData);
        
        // 显示新创建的API密钥
        newApiKey.value = response.data.api_key;
        createModalVisible.value = false;
        keyDisplayModalVisible.value = true;
        
      } catch (error) {
        if (error.response && error.response.data) {
          message.error(error.response.data.error || '创建API密钥失败');
        } else if (error.message) {
          // 表单验证错误
          console.error('表单验证失败', error);
        } else {
          message.error('创建API密钥失败');
        }
      } finally {
        modalLoading.value = false;
      }
    };
    
    // 更新API密钥
    const handleUpdateApiKey = async () => {
      try {
        await editFormRef.value.validate();
        modalLoading.value = true;
        
        const formData = {
          name: apiKeyForm.name,
          description: apiKeyForm.description,
          is_active: apiKeyForm.is_active
        };
        
        if (apiKeyForm.expires_at) {
          formData.expires_at = apiKeyForm.expires_at.toISOString();
        }
        
        if (apiKeyForm.allowed_ips) {
          formData.allowed_ips = apiKeyForm.allowed_ips;
        }
        
        if (apiKeyForm.rate_limit_override) {
          formData.rate_limit_override = apiKeyForm.rate_limit_override;
        }
        
        await updateApiKey(currentApiKeyId.value, formData);
        
        message.success('更新API密钥成功');
        editModalVisible.value = false;
        fetchApiKeys(); // 刷新API密钥列表
      } catch (error) {
        if (error.response && error.response.data) {
          message.error(error.response.data.error || '更新API密钥失败');
        } else if (error.message) {
          // 表单验证错误
          console.error('表单验证失败', error);
        } else {
          message.error('更新API密钥失败');
        }
      } finally {
        modalLoading.value = false;
      }
    };
    
    // 删除API密钥
    const deleteApiKey = async (apiKey) => {
      loading.value = true;
      try {
        await deleteApiKey(apiKey.id);
        message.success(`API密钥 ${apiKey.name} 已删除`);
        fetchApiKeys(); // 刷新API密钥列表
      } catch (error) {
        if (error.response && error.response.data) {
          message.error(error.response.data.error || '删除API密钥失败');
        } else {
          message.error('删除API密钥失败');
        }
      } finally {
        loading.value = false;
      }
    };
    
    // 复制API密钥
    const copyApiKey = (apiKey) => {
      // 通常API密钥是敏感信息，这里仅复制显示的部分密钥
      navigator.clipboard.writeText(apiKey.key)
        .then(() => message.success('API密钥已复制到剪贴板'))
        .catch(() => message.error('复制失败，请手动复制'));
    };
    
    // 处理API密钥复制完成
    const handleApiKeyCopied = () => {
      keyDisplayModalVisible.value = false;
      fetchApiKeys(); // 刷新API密钥列表
      message.success('API密钥创建成功');
    };
    
    onMounted(() => {
      fetchApiKeys();
    });
    
    return {
      apiKeys,
      loading,
      columns,
      apiKeyForm,
      rules,
      createModalVisible,
      editModalVisible,
      keyDisplayModalVisible,
      modalLoading,
      newApiKey,
      copyAddon,
      createFormRef,
      editFormRef,
      showCreateModal,
      showEditModal,
      handleCreateApiKey,
      handleUpdateApiKey,
      deleteApiKey,
      copyApiKey,
      handleApiKeyCopied
    };
  }
});
</script>

<style scoped>
.api-key-manager-container {
  padding: 24px;
}

.key-display {
  text-align: center;
}

.warning-text {
  color: #ff4d4f;
  font-weight: bold;
  margin-bottom: 16px;
}

.key-actions {
  margin-top: 24px;
}
</style> 