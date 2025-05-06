<template>
  <div class="service-manager">
    <div class="page-title">
      <h2>服务管理</h2>
      <p class="sub-title">管理系统服务</p>
      <div class="action-buttons">
        <a-button type="primary" @click="refreshServices" style="margin-right: 8px">刷新</a-button>
        <a-button type="primary" @click="showAddModal">添加服务</a-button>
      </div>
    </div>

    <a-card>
      <a-table 
        :columns="columns" 
        :data-source="services" 
        :loading="loading"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 'running' ? 'green' : 'red'">
              {{ record.status_display }}
            </a-tag>
          </template>
          <template v-if="column.key === 'actions'">
            <a-space>
              <a-button 
                v-if="record.status !== 'running'" 
                type="primary" 
                size="small" 
                @click="startService(record)"
                :loading="actionLoading[record.id]"
              >
                启动
              </a-button>
              <a-button 
                v-else 
                danger 
                size="small" 
                @click="stopService(record)"
                :loading="actionLoading[record.id]"
              >
                停止
              </a-button>
              <a-button type="link" size="small" @click="editService(record)">编辑</a-button>
              <a-popconfirm
                title="确定要删除此服务吗?"
                @confirm="deleteService(record.id)"
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

    <!-- 添加/编辑服务模态框 -->
    <a-modal
      v-model:visible="modalVisible"
      :title="isEditing ? '编辑服务' : '添加服务'"
      @ok="saveService"
      :confirmLoading="submitLoading"
    >
      <a-form layout="vertical">
        <a-form-item label="服务名称">
          <a-input v-model:value="currentService.name" placeholder="输入服务名称" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="currentService.description" placeholder="输入服务描述" :rows="3" />
        </a-form-item>
        <a-form-item label="启动命令">
          <a-input v-model:value="currentService.command" placeholder="输入服务启动命令" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import { message } from 'ant-design-vue';
import serviceApi from '../api/services';

export default {
  name: 'ServiceManager',
  
  setup() {
    // 数据定义
    const services = ref([]);
    const loading = ref(false);
    const modalVisible = ref(false);
    const isEditing = ref(false);
    const submitLoading = ref(false);
    const actionLoading = reactive({});
    const currentService = reactive({
      id: null,
      name: '',
      description: '',
      command: '',
      status: 'stopped'
    });
    
    // 轮询定时器
    let statusTimer = null;
    
    // 表格列定义
    const columns = [
      {
        title: 'ID',
        dataIndex: 'id',
        key: 'id',
        width: 80
      },
      {
        title: '服务名称',
        dataIndex: 'name',
        key: 'name',
        width: 200
      },
      {
        title: '描述',
        dataIndex: 'description',
        key: 'description'
      },
      {
        title: '状态',
        dataIndex: 'status',
        key: 'status',
        width: 120
      },
      {
        title: '更新时间',
        dataIndex: 'updated_at',
        key: 'updated_at',
        width: 180
      },
      {
        title: '操作',
        key: 'actions',
        width: 200
      }
    ];
    
    // 加载服务列表
    const loadServices = async () => {
      loading.value = true;
      try {
        const response = await serviceApi.getServices();
        services.value = response.data;
      } catch (error) {
        message.error('加载服务列表失败: ' + error.message);
      } finally {
        loading.value = false;
      }
    };
    
    // 刷新服务
    const refreshServices = async () => {
      try {
        const response = await serviceApi.refreshServiceStatus();
        services.value = response.data;
        message.success('服务状态已刷新');
      } catch (error) {
        message.error('刷新服务状态失败: ' + error.message);
      }
    };
    
    // 定时刷新服务状态
    const startStatusPolling = () => {
      stopStatusPolling(); // 先停止之前的轮询
      statusTimer = setInterval(async () => {
        try {
          const response = await serviceApi.refreshServiceStatus();
          services.value = response.data;
        } catch (error) {
          console.error('刷新服务状态失败:', error);
        }
      }, 5000); // 每5秒刷新一次
    };
    
    const stopStatusPolling = () => {
      if (statusTimer) {
        clearInterval(statusTimer);
        statusTimer = null;
      }
    };
    
    // 启动服务
    const startService = async (service) => {
      actionLoading[service.id] = true;
      try {
        const response = await serviceApi.startService(service.id);
        message.success(response.data.message || '服务已启动');
        refreshServices();
      } catch (error) {
        message.error('启动服务失败: ' + (error.response?.data?.message || error.message));
      } finally {
        actionLoading[service.id] = false;
      }
    };
    
    // 停止服务
    const stopService = async (service) => {
      actionLoading[service.id] = true;
      try {
        const response = await serviceApi.stopService(service.id);
        message.success(response.data.message || '服务已停止');
        refreshServices();
      } catch (error) {
        message.error('停止服务失败: ' + (error.response?.data?.message || error.message));
      } finally {
        actionLoading[service.id] = false;
      }
    };
    
    // 显示添加模态框
    const showAddModal = () => {
      isEditing.value = false;
      Object.assign(currentService, {
        id: null,
        name: '',
        description: '',
        command: '',
        status: 'stopped'
      });
      modalVisible.value = true;
    };
    
    // 编辑服务
    const editService = (service) => {
      isEditing.value = true;
      Object.assign(currentService, service);
      modalVisible.value = true;
    };
    
    // 保存服务
    const saveService = async () => {
      if (!currentService.name || !currentService.command) {
        message.error('服务名称和启动命令不能为空');
        return;
      }
      
      submitLoading.value = true;
      try {
        if (isEditing.value) {
          await serviceApi.updateService(currentService.id, {
            name: currentService.name,
            description: currentService.description,
            command: currentService.command
          });
          message.success('服务更新成功');
        } else {
          await serviceApi.createService({
            name: currentService.name,
            description: currentService.description,
            command: currentService.command,
            status: 'stopped'
          });
          message.success('服务添加成功');
        }
        modalVisible.value = false;
        loadServices();
      } catch (error) {
        message.error((isEditing.value ? '更新' : '添加') + '服务失败: ' + error.message);
      } finally {
        submitLoading.value = false;
      }
    };
    
    // 删除服务
    const deleteService = async (id) => {
      try {
        await serviceApi.deleteService(id);
        message.success('服务删除成功');
        loadServices();
      } catch (error) {
        message.error('删除服务失败: ' + error.message);
      }
    };
    
    onMounted(() => {
      loadServices();
      startStatusPolling();
    });
    
    onUnmounted(() => {
      stopStatusPolling();
    });
    
    return {
      services,
      loading,
      columns,
      modalVisible,
      isEditing,
      currentService,
      submitLoading,
      actionLoading,
      refreshServices,
      startService,
      stopService,
      showAddModal,
      editService,
      saveService,
      deleteService
    };
  }
};
</script>

<style scoped>
.service-manager {
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
</style> 