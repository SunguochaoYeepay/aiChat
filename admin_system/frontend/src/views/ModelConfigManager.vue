<template>
  <div class="model-config-manager">
    <div class="page-title">
      <h2>模型配置管理</h2>
      <p class="sub-title">管理AI模型配置</p>
      <div class="action-buttons">
        <a-button type="primary" @click="loadConfigs" style="margin-right: 8px">刷新</a-button>
        <a-button type="primary" @click="showAddModal">添加配置</a-button>
      </div>
    </div>

    <a-card>
      <a-table 
        :columns="columns" 
        :data-source="configs" 
        :loading="loading"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'is_active'">
            <a-tag :color="record.is_active ? 'green' : 'default'">
              {{ record.is_active ? '已激活' : '未激活' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'device'">
            {{ record.device_display }}
          </template>
          <template v-if="column.key === 'precision'">
            {{ record.precision_display }}
          </template>
          <template v-if="column.key === 'actions'">
            <a-space>
              <a-button 
                v-if="!record.is_active" 
                type="primary" 
                size="small" 
                @click="activateConfig(record)"
                :loading="actionLoading[record.id]"
              >
                激活
              </a-button>
              <a-button 
                v-if="record.is_active" 
                type="primary" 
                size="small" 
                @click="reloadModel(record)"
                :loading="actionLoading[record.id]"
              >
                重载模型
              </a-button>
              <a-button type="link" size="small" @click="editConfig(record)">编辑</a-button>
              <a-popconfirm
                v-if="!record.is_active"
                title="确定要删除此配置吗?"
                @confirm="deleteConfig(record.id)"
                ok-text="确定"
                cancel-text="取消"
              >
                <a-button type="link" danger size="small">删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 添加/编辑配置模态框 -->
    <a-modal
      v-model:visible="modalVisible"
      :title="isEditing ? '编辑模型配置' : '添加模型配置'"
      @ok="saveConfig"
      :confirmLoading="submitLoading"
      width="700px"
    >
      <a-form layout="vertical">
        <a-form-item label="模型名称">
          <a-input v-model:value="currentConfig.name" placeholder="输入模型配置名称" />
        </a-form-item>
        <a-form-item label="模型路径">
          <a-input v-model:value="currentConfig.model_path" placeholder="输入模型文件/目录路径" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="currentConfig.description" placeholder="输入模型配置描述" :rows="2" />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="运行设备">
              <a-select v-model:value="currentConfig.device">
                <a-select-option value="cuda">GPU (CUDA)</a-select-option>
                <a-select-option value="cpu">CPU</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="批处理大小">
              <a-input-number v-model:value="currentConfig.batch_size" :min="1" :max="16" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="精度">
              <a-select v-model:value="currentConfig.precision">
                <a-select-option value="float16">半精度 (float16)</a-select-option>
                <a-select-option value="float32">全精度 (float32)</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="激活状态">
          <a-switch v-model:checked="currentConfig.is_active" />
          <span class="form-help-text">如果激活，该配置将被用于模型加载</span>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import modelConfigApi from '../api/modelConfigs';

export default {
  name: 'ModelConfigManager',
  
  setup() {
    // 数据定义
    const configs = ref([]);
    const loading = ref(false);
    const modalVisible = ref(false);
    const isEditing = ref(false);
    const submitLoading = ref(false);
    const actionLoading = reactive({});
    const currentConfig = reactive({
      id: null,
      name: '',
      model_path: '',
      device: 'cuda',
      is_active: false,
      batch_size: 1,
      precision: 'float16',
      description: ''
    });
    
    // 表格列定义
    const columns = [
      {
        title: 'ID',
        dataIndex: 'id',
        key: 'id',
        width: 70
      },
      {
        title: '名称',
        dataIndex: 'name',
        key: 'name',
        width: 150
      },
      {
        title: '模型路径',
        dataIndex: 'model_path',
        key: 'model_path',
        width: 250,
        ellipsis: true
      },
      {
        title: '设备',
        dataIndex: 'device',
        key: 'device',
        width: 100
      },
      {
        title: '批处理大小',
        dataIndex: 'batch_size',
        key: 'batch_size',
        width: 100
      },
      {
        title: '精度',
        dataIndex: 'precision',
        key: 'precision',
        width: 120
      },
      {
        title: '状态',
        dataIndex: 'is_active',
        key: 'is_active',
        width: 100
      },
      {
        title: '操作',
        key: 'actions',
        width: 220
      }
    ];
    
    // 加载模型配置列表
    const loadConfigs = async () => {
      loading.value = true;
      try {
        const response = await modelConfigApi.getModelConfigs();
        configs.value = response.data;
      } catch (error) {
        message.error('加载模型配置失败: ' + error.message);
      } finally {
        loading.value = false;
      }
    };
    
    // 显示添加模态框
    const showAddModal = () => {
      isEditing.value = false;
      Object.assign(currentConfig, {
        id: null,
        name: '',
        model_path: '',
        device: 'cuda',
        is_active: false,
        batch_size: 1,
        precision: 'float16',
        description: ''
      });
      modalVisible.value = true;
    };
    
    // 编辑配置
    const editConfig = (config) => {
      isEditing.value = true;
      Object.assign(currentConfig, config);
      modalVisible.value = true;
    };
    
    // 保存配置
    const saveConfig = async () => {
      if (!currentConfig.name || !currentConfig.model_path) {
        message.error('模型名称和路径不能为空');
        return;
      }
      
      submitLoading.value = true;
      try {
        if (isEditing.value) {
          await modelConfigApi.updateModelConfig(currentConfig.id, {
            name: currentConfig.name,
            model_path: currentConfig.model_path,
            device: currentConfig.device,
            is_active: currentConfig.is_active,
            batch_size: currentConfig.batch_size,
            precision: currentConfig.precision,
            description: currentConfig.description
          });
          message.success('模型配置更新成功');
        } else {
          await modelConfigApi.createModelConfig({
            name: currentConfig.name,
            model_path: currentConfig.model_path,
            device: currentConfig.device,
            is_active: currentConfig.is_active,
            batch_size: currentConfig.batch_size,
            precision: currentConfig.precision,
            description: currentConfig.description
          });
          message.success('模型配置添加成功');
        }
        modalVisible.value = false;
        loadConfigs();
      } catch (error) {
        message.error((isEditing.value ? '更新' : '添加') + '模型配置失败: ' + error.message);
      } finally {
        submitLoading.value = false;
      }
    };
    
    // 激活配置
    const activateConfig = async (config) => {
      actionLoading[config.id] = true;
      try {
        const response = await modelConfigApi.activateModelConfig(config.id);
        message.success(response.data.message || '模型配置已激活');
        loadConfigs();
      } catch (error) {
        message.error('激活模型配置失败: ' + (error.response?.data?.message || error.message));
      } finally {
        actionLoading[config.id] = false;
      }
    };
    
    // 重新加载模型
    const reloadModel = async (config) => {
      actionLoading[config.id] = true;
      try {
        const response = await modelConfigApi.reloadModel(config.id);
        message.success(response.data.message || '模型已重新加载');
      } catch (error) {
        message.error('重载模型失败: ' + (error.response?.data?.message || error.message));
      } finally {
        actionLoading[config.id] = false;
      }
    };
    
    // 删除配置
    const deleteConfig = async (id) => {
      try {
        await modelConfigApi.deleteModelConfig(id);
        message.success('模型配置删除成功');
        loadConfigs();
      } catch (error) {
        message.error('删除模型配置失败: ' + error.message);
      }
    };
    
    onMounted(() => {
      loadConfigs();
    });
    
    return {
      configs,
      loading,
      columns,
      modalVisible,
      isEditing,
      currentConfig,
      submitLoading,
      actionLoading,
      loadConfigs,
      showAddModal,
      editConfig,
      saveConfig,
      activateConfig,
      reloadModel,
      deleteConfig
    };
  }
};
</script>

<style scoped>
.model-config-manager {
  width: 100%;
}

.page-title {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.page-title h2 {
  margin-bottom: 8px;
}

.sub-title {
  color: rgba(0, 0, 0, 0.45);
  font-size: 14px;
}

.action-buttons {
  margin-top: 16px;
}

.ant-card {
  margin-bottom: 16px;
}

.form-help-text {
  margin-left: 10px;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}
</style> 