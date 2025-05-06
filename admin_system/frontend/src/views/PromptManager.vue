<template>
  <div class="prompt-manager">
    <div class="page-title">
      <h2>提示词模板管理</h2>
      <p class="sub-title">管理系统中使用的提示词模板</p>
      <div class="action-buttons">
        <a-button type="primary" @click="refreshData">刷新</a-button>
      </div>
    </div>

    <a-card>
      <a-tabs v-model:activeKey="activeTab">
        <a-tab-pane key="editor" tab="模板编辑器">
          <prompt-template-editor />
        </a-tab-pane>
        <a-tab-pane key="list" tab="模板列表">
          <a-table 
            :columns="columns" 
            :data-source="tableData" 
            :loading="loading"
            row-key="id"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'actions'">
                <a-space>
                  <a-button type="link" @click="editTemplate(record)">编辑</a-button>
                  <a-popconfirm
                    title="确定要删除此模板吗?"
                    @confirm="deleteTemplate(record.id)"
                    ok-text="确定"
                    cancel-text="取消"
                  >
                    <a-button type="link" danger>删除</a-button>
                  </a-popconfirm>
                </a-space>
              </template>
            </template>
          </a-table>
        </a-tab-pane>
        <a-tab-pane key="help" tab="帮助">
          <div class="help-content">
            <h2>提示词模板使用指南</h2>
            <p>提示词模板是定义 AI 模型行为的关键组件。通过调整提示词，可以控制 AI 的回复风格、格式和内容。</p>
            
            <h3>可用变量</h3>
            <p>在提示词模板中，您可以使用以下变量：</p>
            <ul>
              <li><strong>{query}</strong> - 用户的当前问题</li>
              <li><strong>{history}</strong> - 聊天历史记录</li>
              <li><strong>{content}</strong> - 知识库搜索结果</li>
              <li><strong>{topics}</strong> - 主题列表（用于主题匹配）</li>
            </ul>
            
            <h3>模板类别</h3>
            <p>系统提供以下几种模板类别：</p>
            <ul>
              <li><strong>chat</strong> - 用于常规聊天对话</li>
              <li><strong>search</strong> - 用于结合知识库搜索的回答</li>
              <li><strong>image_analysis</strong> - 用于图像分析场景</li>
              <li><strong>topic_matching</strong> - 用于主题匹配</li>
            </ul>
            
            <h3>最佳实践</h3>
            <p>1. 保持提示词清晰简洁</p>
            <p>2. 使用明确的指令和界限</p>
            <p>3. 定期检查和优化模板效果</p>
          </div>
        </a-tab-pane>
      </a-tabs>
    </a-card>

    <a-modal
      v-model:visible="editModalVisible"
      title="编辑提示词模板"
      @ok="saveEditedTemplate"
      width="700px"
    >
      <a-form layout="vertical">
        <a-form-item label="名称">
          <a-input v-model:value="editingTemplate.name" disabled />
        </a-form-item>
        <a-form-item label="描述">
          <a-input v-model:value="editingTemplate.description" />
        </a-form-item>
        <a-form-item label="内容">
          <a-textarea 
            v-model:value="editingTemplate.content" 
            :rows="12" 
            placeholder="请输入提示词模板内容..."
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import PromptTemplateEditor from '../components/PromptTemplateEditor.vue';
import promptTemplateApi from '../api/promptTemplates';

export default {
  name: 'PromptManager',
  components: {
    PromptTemplateEditor
  },
  
  setup() {
    const activeTab = ref('editor');
    const loading = ref(false);
    const tableData = ref([]);
    const editModalVisible = ref(false);
    const editingTemplate = reactive({
      id: null,
      name: '',
      description: '',
      content: ''
    });
    
    const columns = [
      {
        title: 'ID',
        dataIndex: 'id',
        key: 'id',
        width: 60
      },
      {
        title: '模板名称',
        dataIndex: 'name',
        key: 'name',
        sorter: (a, b) => a.name.localeCompare(b.name),
        width: 200
      },
      {
        title: '描述',
        dataIndex: 'description',
        key: 'description',
        width: 300
      },
      {
        title: '创建时间',
        dataIndex: 'created_at',
        key: 'created_at',
        width: 180
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
        width: 120
      }
    ];
    
    // 加载数据
    const loadData = async () => {
      loading.value = true;
      try {
        const response = await promptTemplateApi.getTemplates();
        tableData.value = response.data;
      } catch (error) {
        message.error('加载提示词模板失败: ' + error.message);
      } finally {
        loading.value = false;
      }
    };
    
    // 刷新数据
    const refreshData = () => {
      loadData();
    };
    
    // 编辑模板
    const editTemplate = (record) => {
      Object.assign(editingTemplate, record);
      editModalVisible.value = true;
    };
    
    // 保存编辑后的模板
    const saveEditedTemplate = async () => {
      try {
        await promptTemplateApi.updateTemplate(editingTemplate.id, {
          name: editingTemplate.name,
          description: editingTemplate.description,
          content: editingTemplate.content
        });
        message.success('模板更新成功');
        editModalVisible.value = false;
        loadData();
        await promptTemplateApi.refreshCache();
      } catch (error) {
        message.error('更新模板失败: ' + error.message);
      }
    };
    
    // 删除模板
    const deleteTemplate = async (id) => {
      try {
        await promptTemplateApi.deleteTemplate(id);
        message.success('模板删除成功');
        loadData();
        await promptTemplateApi.refreshCache();
      } catch (error) {
        message.error('删除模板失败: ' + error.message);
      }
    };
    
    onMounted(() => {
      loadData();
    });
    
    return {
      activeTab,
      loading,
      tableData,
      columns,
      editModalVisible,
      editingTemplate,
      refreshData,
      editTemplate,
      saveEditedTemplate,
      deleteTemplate
    };
  }
};
</script>

<style scoped>
.prompt-manager {
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

.help-content {
  padding: 16px;
  max-width: 800px;
  margin: 0 auto;
}

.help-content h2 {
  margin-bottom: 16px;
}

.help-content h3 {
  margin-top: 24px;
}
</style> 