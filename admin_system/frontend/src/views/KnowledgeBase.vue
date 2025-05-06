<template>
  <div class="knowledge-base">
    <div class="page-title">
      <h2>知识库管理</h2>
      <p class="sub-title">管理系统的知识库文档和分块</p>
      <div class="action-buttons">
        <a-button type="primary" @click="importKnowledge" style="margin-right: 8px">导入知识</a-button>
        <a-button type="default" @click="refreshKnowledgeBases">刷新</a-button>
      </div>
    </div>

    <a-card>
      <a-tabs v-model:activeKey="activeTab">
        <a-tab-pane key="knowledge" tab="知识库管理">
          <a-table
            :columns="columns"
            :data-source="knowledgeList"
            :loading="loading"
            row-key="id"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'actions'">
                <a-space>
                  <a-button type="link" @click="viewContent(record)">查看内容</a-button>
                  <a-button type="link" @click="viewChunks(record)">查看分块</a-button>
                  <a-button type="link" @click="indexKnowledge(record.id)" :disabled="record.is_indexed">
                    {{ record.is_indexed ? '已向量化' : '向量化' }}
                  </a-button>
                  <a-popconfirm
                    title="确定要删除此知识库?"
                    @confirm="deleteKnowledge(record.id)"
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
        <a-tab-pane key="chunks" tab="分块管理">
          <div style="margin-bottom: 16px">
            <a-select
              v-model:value="selectedKnowledgeBase"
              placeholder="选择知识库"
              style="width: 300px; margin-right: 16px"
              @change="loadChunks"
            >
              <a-select-option v-for="kb in knowledgeList" :key="kb.id" :value="kb.id">
                {{ kb.name }}
              </a-select-option>
            </a-select>
            <a-button type="primary" @click="loadChunks" :disabled="!selectedKnowledgeBase">加载分块</a-button>
          </div>
          
          <a-table
            :columns="chunkColumns"
            :data-source="chunksList"
            :loading="chunksLoading"
            row-key="id"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'content'">
                <div style="max-height: 100px; overflow: auto;">
                  {{ record.content }}
                </div>
              </template>
              <template v-if="column.key === 'is_indexed'">
                <a-tag :color="record.is_indexed ? 'green' : 'red'">
                  {{ record.is_indexed ? '已向量化' : '未向量化' }}
                </a-tag>
              </template>
              <template v-if="column.key === 'actions'">
                <a-space>
                  <a-button type="link" @click="editChunk(record)">编辑</a-button>
                  <a-button 
                    type="link" 
                    @click="vectorizeChunk(record.id)" 
                    :disabled="record.is_indexed"
                  >
                    向量化
                  </a-button>
                  <a-popconfirm
                    title="确定要删除此分块?"
                    @confirm="deleteChunk(record.id)"
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
      </a-tabs>
    </a-card>

    <!-- 知识库内容预览模态框 -->
    <a-modal
      v-model:visible="contentModalVisible"
      :title="currentKnowledge.name"
      width="800px"
      :footer="null"
    >
      <div class="knowledge-content-preview">
        <pre>{{ currentKnowledge.content }}</pre>
      </div>
    </a-modal>

    <!-- 知识库分块模态框 -->
    <a-modal
      v-model:visible="chunksModalVisible"
      :title="`${currentKnowledge.name} - 分块管理`"
      width="900px"
      :footer="null"
    >
      <a-spin :spinning="chunksLoading">
        <a-table 
          :columns="chunkColumns" 
          :data-source="knowledgeChunks" 
          :pagination="{ pageSize: 5 }"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'content'">
              <div style="max-height: 100px; overflow: auto;">
                {{ record.content }}
              </div>
            </template>
            <template v-if="column.key === 'is_indexed'">
              <a-tag :color="record.is_indexed ? 'green' : 'red'">
                {{ record.is_indexed ? '已向量化' : '未向量化' }}
              </a-tag>
            </template>
            <template v-if="column.key === 'actions'">
              <a-space>
                <a-button type="link" size="small" @click="editChunk(record)">编辑</a-button>
                <a-button 
                  type="link" 
                  size="small" 
                  @click="vectorizeChunk(record.id)" 
                  :disabled="record.is_indexed"
                >
                  向量化
                </a-button>
                <a-popconfirm
                  title="确定要删除此分块?"
                  @confirm="deleteChunk(record.id)"
                  ok-text="确定"
                  cancel-text="取消"
                >
                  <a-button type="link" danger size="small">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-spin>
    </a-modal>

    <!-- 导入知识模态框 -->
    <a-modal
      v-model:visible="importModalVisible"
      title="导入知识库"
      @ok="submitImport"
      :confirmLoading="importLoading"
    >
      <a-form layout="vertical">
        <a-form-item label="从文件导入">
          <a-upload-dragger
            name="file"
            :multiple="false"
            :before-upload="beforeUpload"
            :custom-request="customUploadRequest"
          >
            <p class="ant-upload-drag-icon">
              <a-icon type="inbox" />
            </p>
            <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p class="ant-upload-hint">支持上传 Markdown 文件</p>
          </a-upload-dragger>
        </a-form-item>
        
        <a-divider>或者</a-divider>
        
        <a-form-item label="从目录导入">
          <a-input 
            v-model:value="importDirectory" 
            placeholder="请输入知识库文件所在目录的绝对路径" 
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 编辑分块模态框 -->
    <a-modal
      v-model:visible="editChunkModalVisible"
      title="编辑知识库分块"
      @ok="saveChunk"
      :confirmLoading="saveChunkLoading"
      width="800px"
    >
      <a-form layout="vertical">
        <a-form-item label="所属知识库" v-if="editingChunk.knowledge_base">
          <a-input v-model:value="editingChunk.knowledge_base_name" disabled />
        </a-form-item>
        <a-form-item label="分块内容">
          <a-textarea 
            v-model:value="editingChunk.content" 
            :rows="10" 
            placeholder="请输入分块内容..." 
          />
        </a-form-item>
        <a-form-item label="元数据">
          <a-input 
            v-model:value="editingChunk.metadata_str" 
            placeholder="元数据 (JSON 格式)" 
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import knowledgeBaseApi from '../api/knowledgeBase';
import knowledgeChunkApi from '../api/knowledgeChunks';

export default {
  name: 'KnowledgeBase',
  
  setup() {
    const loading = ref(false);
    const chunksLoading = ref(false);
    const knowledgeList = ref([]);
    const chunksList = ref([]);
    const knowledgeChunks = ref([]);
    const contentModalVisible = ref(false);
    const chunksModalVisible = ref(false);
    const importModalVisible = ref(false);
    const editChunkModalVisible = ref(false);
    const importLoading = ref(false);
    const saveChunkLoading = ref(false);
    const importDirectory = ref('');
    const activeTab = ref('knowledge');
    const selectedKnowledgeBase = ref(null);
    
    const currentKnowledge = reactive({
      id: null,
      name: '',
      content: ''
    });
    
    const editingChunk = reactive({
      id: null,
      knowledge_base: null,
      knowledge_base_name: '',
      content: '',
      is_indexed: false,
      metadata: {},
      metadata_str: '{}'
    });
    
    const columns = [
      {
        title: 'ID',
        dataIndex: 'id',
        key: 'id',
        width: 80
      },
      {
        title: '知识库名称',
        dataIndex: 'name',
        key: 'name',
        width: 200
      },
      {
        title: '描述',
        dataIndex: 'description',
        key: 'description',
        width: 300
      },
      {
        title: '文件路径',
        dataIndex: 'file_path',
        key: 'file_path',
        width: 300
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
        width: 280
      }
    ];
    
    const chunkColumns = [
      {
        title: 'ID',
        dataIndex: 'id',
        key: 'id',
        width: 60
      },
      {
        title: '内容',
        dataIndex: 'content',
        key: 'content',
        ellipsis: true
      },
      {
        title: '向量化状态',
        dataIndex: 'is_indexed',
        key: 'is_indexed',
        width: 100
      },
      {
        title: '创建时间',
        dataIndex: 'created_at',
        key: 'created_at',
        width: 180
      },
      {
        title: '操作',
        key: 'actions',
        width: 200
      }
    ];
    
    // 加载知识库列表
    const loadKnowledgeList = async () => {
      loading.value = true;
      try {
        const response = await knowledgeBaseApi.getKnowledgeBases();
        knowledgeList.value = response.data || [];
      } catch (error) {
        message.error('加载知识库列表失败: ' + error.message);
      } finally {
        loading.value = false;
      }
    };
    
    // 刷新知识库列表
    const refreshKnowledgeBases = () => {
      loadKnowledgeList();
    };
    
    // 查看知识库内容
    const viewContent = async (record) => {
      try {
        const response = await knowledgeBaseApi.getKnowledgeBase(record.id);
        const data = response.data;
        
        currentKnowledge.id = data.id;
        currentKnowledge.name = data.name;
        currentKnowledge.content = data.content;
        
        contentModalVisible.value = true;
      } catch (error) {
        message.error('获取知识库内容失败: ' + error.message);
      }
    };
    
    // 查看知识库分块
    const viewChunks = async (record) => {
      currentKnowledge.id = record.id;
      currentKnowledge.name = record.name;
      chunksModalVisible.value = true;
      await loadKnowledgeChunks(record.id);
    };
    
    // 加载知识库分块
    const loadKnowledgeChunks = async (knowledgeBaseId) => {
      chunksLoading.value = true;
      try {
        const response = await knowledgeChunkApi.getChunks(knowledgeBaseId);
        knowledgeChunks.value = response.data || [];
      } catch (error) {
        message.error('加载知识库分块失败: ' + error.message);
      } finally {
        chunksLoading.value = false;
      }
    };
    
    // 加载分块列表（用于分块管理标签页）
    const loadChunks = async () => {
      if (!selectedKnowledgeBase.value) {
        chunksList.value = [];
        return;
      }
      
      chunksLoading.value = true;
      try {
        const response = await knowledgeChunkApi.getChunks(selectedKnowledgeBase.value);
        chunksList.value = response.data || [];
      } catch (error) {
        message.error('加载分块失败: ' + error.message);
      } finally {
        chunksLoading.value = false;
      }
    };
    
    // 向量化知识库
    const indexKnowledge = async (id) => {
      try {
        const response = await knowledgeBaseApi.indexKnowledgeBase(id);
        if (response.data.status === 'success') {
          message.success(response.data.message || '知识库向量化成功');
          loadKnowledgeList();
        } else {
          message.error(response.data.message || '知识库向量化失败');
        }
      } catch (error) {
        message.error('向量化知识库失败: ' + error.message);
      }
    };
    
    // 删除知识库
    const deleteKnowledge = async (id) => {
      try {
        await knowledgeBaseApi.deleteKnowledgeBase(id);
        message.success('知识库删除成功');
        loadKnowledgeList();
      } catch (error) {
        message.error('删除知识库失败: ' + error.message);
      }
    };
    
    // 编辑分块
    const editChunk = (chunk) => {
      editingChunk.id = chunk.id;
      editingChunk.knowledge_base = chunk.knowledge_base;
      
      // 查找知识库名称
      const kb = knowledgeList.value.find(k => k.id === chunk.knowledge_base);
      editingChunk.knowledge_base_name = kb ? kb.name : `知识库 #${chunk.knowledge_base}`;
      
      editingChunk.content = chunk.content;
      editingChunk.is_indexed = chunk.is_indexed;
      editingChunk.metadata = chunk.metadata || {};
      editingChunk.metadata_str = JSON.stringify(chunk.metadata || {}, null, 2);
      
      editChunkModalVisible.value = true;
    };
    
    // 保存分块
    const saveChunk = async () => {
      saveChunkLoading.value = true;
      try {
        // 尝试解析元数据
        let metadata = {};
        try {
          metadata = JSON.parse(editingChunk.metadata_str);
        } catch (e) {
          message.error('元数据必须是有效的 JSON 格式');
          saveChunkLoading.value = false;
          return;
        }
        
        await knowledgeChunkApi.updateChunk(editingChunk.id, {
          knowledge_base: editingChunk.knowledge_base,
          content: editingChunk.content,
          metadata: metadata
        });
        
        message.success('分块更新成功');
        editChunkModalVisible.value = false;
        
        // 刷新分块列表
        if (chunksModalVisible.value) {
          await loadKnowledgeChunks(currentKnowledge.id);
        }
        if (activeTab.value === 'chunks') {
          await loadChunks();
        }
      } catch (error) {
        message.error('更新分块失败: ' + error.message);
      } finally {
        saveChunkLoading.value = false;
      }
    };
    
    // 向量化分块
    const vectorizeChunk = async (id) => {
      try {
        const response = await knowledgeChunkApi.vectorizeChunk(id);
        if (response.data.status === 'success') {
          message.success(response.data.message || '分块向量化成功');
          
          // 刷新分块列表
          if (chunksModalVisible.value) {
            await loadKnowledgeChunks(currentKnowledge.id);
          }
          if (activeTab.value === 'chunks') {
            await loadChunks();
          }
        } else {
          message.error(response.data.message || '分块向量化失败');
        }
      } catch (error) {
        message.error('向量化分块失败: ' + error.message);
      }
    };
    
    // 删除分块
    const deleteChunk = async (id) => {
      try {
        await knowledgeChunkApi.deleteChunk(id);
        message.success('分块删除成功');
        
        // 刷新分块列表
        if (chunksModalVisible.value) {
          await loadKnowledgeChunks(currentKnowledge.id);
        }
        if (activeTab.value === 'chunks') {
          await loadChunks();
        }
      } catch (error) {
        message.error('删除分块失败: ' + error.message);
      }
    };
    
    // 打开导入模态框
    const importKnowledge = () => {
      importModalVisible.value = true;
    };
    
    // 上传前验证
    const beforeUpload = (file) => {
      const isMarkdown = file.type === 'text/markdown' || file.name.endsWith('.md');
      if (!isMarkdown) {
        message.error('只能上传 Markdown 文件!');
      }
      return isMarkdown;
    };
    
    // 自定义上传
    const customUploadRequest = async ({ file, onSuccess, onError }) => {
      try {
        const response = await knowledgeBaseApi.uploadFile(file);
        if (response.data.status === 'success') {
          message.success(response.data.message || '文件上传成功');
          onSuccess();
          loadKnowledgeList();
        } else {
          message.error(response.data.message || '文件上传失败');
          onError();
        }
      } catch (error) {
        message.error('上传失败: ' + error.message);
        onError();
      }
    };
    
    // 提交导入
    const submitImport = async () => {
      if (!importDirectory.value) {
        message.warning('请输入导入目录');
        return;
      }
      
      importLoading.value = true;
      try {
        const response = await knowledgeBaseApi.importFromDirectory(importDirectory.value);
        if (response.data.status === 'success') {
          message.success(response.data.message || '导入成功');
          importModalVisible.value = false;
          loadKnowledgeList();
        } else {
          message.error(response.data.message || '导入失败');
        }
      } catch (error) {
        message.error('导入知识库失败: ' + error.message);
      } finally {
        importLoading.value = false;
      }
    };
    
    onMounted(() => {
      loadKnowledgeList();
    });
    
    return {
      loading,
      chunksLoading,
      knowledgeList,
      chunksList,
      knowledgeChunks,
      columns,
      chunkColumns,
      contentModalVisible,
      chunksModalVisible,
      importModalVisible,
      editChunkModalVisible,
      importLoading,
      saveChunkLoading,
      importDirectory,
      currentKnowledge,
      editingChunk,
      activeTab,
      selectedKnowledgeBase,
      refreshKnowledgeBases,
      viewContent,
      viewChunks,
      loadKnowledgeChunks,
      loadChunks,
      indexKnowledge,
      deleteKnowledge,
      editChunk,
      saveChunk,
      vectorizeChunk,
      deleteChunk,
      importKnowledge,
      beforeUpload,
      customUploadRequest,
      submitImport
    };
  }
};
</script>

<style scoped>
.knowledge-base {
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

.knowledge-content-preview {
  max-height: 500px;
  overflow: auto;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  padding: 16px;
  background-color: #fafafa;
}

.knowledge-content-preview pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style> 