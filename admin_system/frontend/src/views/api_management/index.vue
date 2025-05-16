<template>
  <div class="api-management">
    <a-page-header
      title="API 管理中心"
      sub-title="管理和测试系统 API 接口"
    />
    
    <a-tabs v-model:activeKey="activeTab" class="api-tabs">
      <a-tab-pane key="test" tab="API 测试">
        <ApiTest />
      </a-tab-pane>
      <a-tab-pane key="docs" tab="API 文档">
        <ApiDocs />
      </a-tab-pane>
      <a-tab-pane key="import" tab="API 导入">
        <ApiImport />
      </a-tab-pane>
      <a-tab-pane key="monitor" tab="API 监控">
        <ApiMonitor />
      </a-tab-pane>
      <a-tab-pane key="keys" tab="API 密钥">
        <ApiKeys />
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script>
import { ref } from 'vue';
import ApiTest from './components/ApiTest.vue';
import ApiDocs from './components/ApiDocs.vue';
import ApiImport from './components/ApiImport.vue';
import ApiMonitor from './components/ApiMonitor.vue';
import ApiKeys from './components/ApiKeys.vue';

export default {
  name: 'ApiManagement',
  
  components: {
    ApiTest,
    ApiDocs,
    ApiImport,
    ApiMonitor,
    ApiKeys
  },
  
  setup() {
    const activeTab = ref('test');
    
    return {
      activeTab
    };
  }
};
</script>

<style scoped>
.api-management {
  padding: 24px;
}

.api-tabs {
  margin-top: 24px;
  background: #fff;
  padding: 16px;
  border-radius: 4px;
}
</style>