<template>
  <div class="prompt-editor">
    <a-form layout="vertical">
      <a-row :gutter="16">
        <a-col :span="6">
          <a-form-item label="类别">
            <a-select 
              v-model:value="currentCategory" 
              @change="handleCategoryChange" 
              style="width: 100%"
              placeholder="选择类别"
              :disabled="!editMode"
            >
              <a-select-option 
                v-for="category in categories" 
                :key="category" 
                :value="category"
              >
                {{ category }}
              </a-select-option>
            </a-select>
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item label="类型">
            <a-select 
              v-model:value="currentType" 
              @change="handleTypeChange" 
              style="width: 100%"
              placeholder="选择类型"
              :disabled="!currentCategory || !editMode"
            >
              <a-select-option 
                v-for="(_, type) in types[currentCategory] || {}" 
                :key="type" 
                :value="type"
              >
                {{ type }}
              </a-select-option>
            </a-select>
          </a-form-item>
        </a-col>
        <a-col :span="6">
          <a-form-item label="操作">
            <div class="actions-container">
              <a-button 
                v-if="!editMode" 
                type="primary" 
                @click="enableEdit"
              >
                编辑
              </a-button>
              <template v-else>
                <a-button type="primary" @click="saveChanges">保存</a-button>
                <a-button @click="cancelEdit">取消</a-button>
              </template>
            </div>
          </a-form-item>
        </a-col>
      </a-row>

      <a-form-item label="提示词内容">
        <a-textarea 
          v-model:value="currentContent" 
          placeholder="请输入提示词模板内容..." 
          :rows="10"
          :disabled="!editMode || !currentCategory || !currentType"
        />
      </a-form-item>

      <div class="template-info">
        <h3>可用变量:</h3>
        <a-tag v-if="currentCategory === 'chat'" color="blue">{query}</a-tag>
        <a-tag v-if="currentCategory === 'chat'" color="green">{history}</a-tag>
        <a-tag v-if="currentCategory === 'search'" color="blue">{query}</a-tag>
        <a-tag v-if="currentCategory === 'search'" color="purple">{content}</a-tag>
        <a-tag v-if="currentCategory === 'image_analysis'" color="blue">{query}</a-tag>
        <a-tag v-if="currentCategory === 'topic_matching'" color="blue">{query}</a-tag>
        <a-tag v-if="currentCategory === 'topic_matching'" color="orange">{topics}</a-tag>
      </div>

      <a-divider orientation="left">批量操作</a-divider>
      
      <div class="batch-actions">
        <a-button type="primary" @click="saveAllChanges">保存所有更改</a-button>
        <a-button danger @click="resetToDefaults">重置为默认值</a-button>
        <a-button @click="refreshCache">刷新缓存</a-button>
      </div>
    </a-form>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import promptTemplateApi from '../api/promptTemplates';

export default {
  name: 'PromptTemplateEditor',
  
  setup() {
    // 数据
    const categories = ref([]);
    const types = reactive({});
    const templates = reactive({});
    const originalTemplates = reactive({});
    
    const currentCategory = ref('');
    const currentType = ref('');
    const currentContent = ref('');
    const editMode = ref(false);
    
    // 加载模板数据
    const loadTemplates = async () => {
      try {
        const response = await promptTemplateApi.getTemplateCategories();
        const templateCategories = response.data;
        
        // 重置数据
        categories.value = [];
        Object.keys(types).forEach(key => delete types[key]);
        Object.keys(templates).forEach(key => delete templates[key]);
        Object.keys(originalTemplates).forEach(key => delete originalTemplates[key]);
        
        // 设置新数据
        templateCategories.forEach(item => {
          const category = item.category;
          categories.value.push(category);
          types[category] = {};
          templates[category] = {};
          originalTemplates[category] = {};
          
          Object.entries(item.types).forEach(([type, content]) => {
            types[category][type] = type;
            templates[category][type] = content;
            originalTemplates[category][type] = content;
          });
        });
        
        // 默认选择第一个类别和类型
        if (categories.value.length > 0) {
          currentCategory.value = categories.value[0];
          const typeKeys = Object.keys(types[currentCategory.value] || {});
          if (typeKeys.length > 0) {
            currentType.value = typeKeys[0];
            currentContent.value = templates[currentCategory.value][currentType.value];
          }
        }
      } catch (error) {
        message.error('加载提示词模板失败: ' + error.message);
      }
    };
    
    // 处理类别变化
    const handleCategoryChange = (value) => {
      currentCategory.value = value;
      const typeKeys = Object.keys(types[value] || {});
      if (typeKeys.length > 0) {
        currentType.value = typeKeys[0];
        currentContent.value = templates[currentCategory.value][currentType.value];
      } else {
        currentType.value = '';
        currentContent.value = '';
      }
    };
    
    // 处理类型变化
    const handleTypeChange = (value) => {
      currentType.value = value;
      currentContent.value = templates[currentCategory.value][currentType.value];
    };
    
    // 启用编辑模式
    const enableEdit = () => {
      editMode.value = true;
    };
    
    // 取消编辑
    const cancelEdit = () => {
      // 恢复原始内容
      if (currentCategory.value && currentType.value) {
        currentContent.value = originalTemplates[currentCategory.value][currentType.value];
        templates[currentCategory.value][currentType.value] = originalTemplates[currentCategory.value][currentType.value];
      }
      editMode.value = false;
    };
    
    // 保存当前模板
    const saveChanges = () => {
      if (currentCategory.value && currentType.value) {
        templates[currentCategory.value][currentType.value] = currentContent.value;
        message.success('模板已更新，请点击"保存所有更改"以保存到服务器');
        editMode.value = false;
      }
    };
    
    // 保存所有更改
    const saveAllChanges = async () => {
      try {
        await promptTemplateApi.batchUpdateTemplates(templates);
        await loadTemplates();
        message.success('所有模板已保存');
      } catch (error) {
        message.error('保存模板失败: ' + error.message);
      }
    };
    
    // 重置为默认值
    const resetToDefaults = async () => {
      try {
        await promptTemplateApi.resetTemplates();
        await loadTemplates();
        message.success('所有模板已重置为默认值');
      } catch (error) {
        message.error('重置模板失败: ' + error.message);
      }
    };
    
    // 刷新缓存
    const refreshCache = async () => {
      try {
        await promptTemplateApi.refreshCache();
        message.success('缓存已刷新');
      } catch (error) {
        message.error('刷新缓存失败: ' + error.message);
      }
    };
    
    // 初始化
    onMounted(() => {
      loadTemplates();
    });
    
    return {
      categories,
      types,
      currentCategory,
      currentType,
      currentContent,
      editMode,
      handleCategoryChange,
      handleTypeChange,
      enableEdit,
      cancelEdit,
      saveChanges,
      saveAllChanges,
      resetToDefaults,
      refreshCache
    };
  }
};
</script>

<style scoped>
.prompt-editor {
  padding: 20px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}

.actions-container {
  display: flex;
  gap: 8px;
}

.template-info {
  margin-top: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.template-info h3 {
  margin-bottom: 8px;
}

.batch-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}
</style> 