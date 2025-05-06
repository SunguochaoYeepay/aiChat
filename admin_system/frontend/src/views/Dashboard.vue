<template>
  <div class="dashboard">
    <div class="page-title">
      <h2>仪表盘</h2>
      <p class="sub-title">系统概览</p>
      <div class="action-buttons">
        <a-button type="primary" @click="loadDashboardData">刷新数据</a-button>
      </div>
    </div>
    
    <a-spin :spinning="loading">
      <div class="dashboard-content">
        <a-row :gutter="16">
          <a-col :span="6">
            <a-card title="提示词模板" :bordered="false">
              <template #extra><router-link to="/prompts">管理</router-link></template>
              <p>{{ statistics.template_count }} 个模板</p>
              <p>{{ statistics.category_count }} 个分类</p>
            </a-card>
          </a-col>
          
          <a-col :span="6">
            <a-card title="知识库" :bordered="false">
              <template #extra><router-link to="/knowledge">管理</router-link></template>
              <p>{{ statistics.knowledge_base_count }} 个知识库</p>
              <p>{{ statistics.document_count }} 个文档</p>
            </a-card>
          </a-col>
          
          <a-col :span="6">
            <a-card title="API 调用" :bordered="false">
              <template #extra><router-link to="/api">查看</router-link></template>
              <p>今日: {{ statistics.api_calls.today }}</p>
              <p>总计: {{ statistics.api_calls.total }}</p>
            </a-card>
          </a-col>
          
          <a-col :span="6">
            <a-card title="系统状态" :bordered="false">
              <p>模型状态: 
                <a-badge 
                  :status="statistics.system_status.model_status === 'running' ? 'success' : 'error'" 
                  :text="statistics.system_status.model_status === 'running' ? '在线' : '离线'" 
                />
              </p>
              <p>API 服务: 
                <a-badge 
                  :status="statistics.system_status.api_status === 'running' ? 'success' : 'error'" 
                  :text="statistics.system_status.api_status === 'running' ? '在线' : '离线'" 
                />
              </p>
            </a-card>
          </a-col>
        </a-row>
        
        <a-divider />
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-card title="最近活动" :bordered="false">
              <a-list size="small" :bordered="false" :data-source="statistics.recent_activities">
                <template #renderItem="{ item }">
                  <a-list-item>
                    <template #actions>
                      <a-tag :color="getActivityTypeColor(item.type)">{{ getActivityTypeText(item.type) }}</a-tag>
                    </template>
                    <a-list-item-meta :title="item.title">
                      <template #description>
                        {{ item.time }}
                      </template>
                    </a-list-item-meta>
                  </a-list-item>
                </template>
              </a-list>
            </a-card>
          </a-col>
          
          <a-col :span="12">
            <a-card title="提示词使用情况" :bordered="false">
              <div ref="promptUsageChart" style="height: 300px;"></div>
            </a-card>
          </a-col>
        </a-row>
      </div>
    </a-spin>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import { message } from 'ant-design-vue';
import dashboardApi from '../api/dashboard';
import * as echarts from 'echarts';

export default {
  name: 'Dashboard',
  setup() {
    const loading = ref(false);
    const promptUsageChart = ref(null);
    let chart = null;
    
    // 统计数据
    const statistics = reactive({
      template_count: 0,
      category_count: 0,
      knowledge_base_count: 0,
      document_count: 0,
      system_status: {
        model_status: 'unknown',
        api_status: 'unknown'
      },
      api_calls: {
        today: 0,
        total: 0
      },
      recent_activities: [],
      prompt_usage: {
        chat: 0,
        search: 0,
        image_analysis: 0,
        topic_matching: 0
      }
    });
    
    // 根据活动类型获取颜色
    const getActivityTypeColor = (type) => {
      const colorMap = {
        'template': 'blue',
        'knowledge': 'green',
        'system': 'orange',
        'api': 'purple'
      };
      return colorMap[type] || 'default';
    };
    
    // 根据活动类型获取文本
    const getActivityTypeText = (type) => {
      const textMap = {
        'template': '提示词',
        'knowledge': '知识库',
        'system': '系统',
        'api': 'API'
      };
      return textMap[type] || '其他';
    };
    
    // 初始化图表
    const initChart = () => {
      if (promptUsageChart.value) {
        // 创建图表实例
        chart = echarts.init(promptUsageChart.value);
        
        // 更新图表数据
        updateChart();
        
        // 监听窗口大小变化，调整图表大小
        window.addEventListener('resize', () => {
          chart && chart.resize();
        });
      }
    };
    
    // 更新图表数据
    const updateChart = () => {
      if (!chart) return;
      
      const { prompt_usage } = statistics;
      
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: Object.keys(prompt_usage).map(key => {
            const nameMap = {
              'chat': '聊天提示词',
              'search': '搜索提示词',
              'image_analysis': '图像分析',
              'topic_matching': '主题匹配'
            };
            return nameMap[key] || key;
          })
        },
        series: [
          {
            name: '使用次数',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: Object.entries(prompt_usage).map(([key, value]) => {
              const nameMap = {
                'chat': '聊天提示词',
                'search': '搜索提示词',
                'image_analysis': '图像分析',
                'topic_matching': '主题匹配'
              };
              return { name: nameMap[key] || key, value };
            })
          }
        ]
      };
      
      chart.setOption(option);
    };
    
    // 加载仪表盘数据
    const loadDashboardData = async () => {
      loading.value = true;
      try {
        const response = await dashboardApi.getStatistics();
        const data = response.data;
        
        // 更新统计数据
        Object.assign(statistics, data);
        
        // 更新图表
        updateChart();
      } catch (error) {
        message.error('加载仪表盘数据失败: ' + error.message);
      } finally {
        loading.value = false;
      }
    };
    
    onMounted(() => {
      loadDashboardData();
      
      // 延迟初始化图表，确保DOM已渲染
      setTimeout(() => {
        initChart();
      }, 100);
    });
    
    onUnmounted(() => {
      // 销毁图表实例
      if (chart) {
        chart.dispose();
        chart = null;
      }
      
      // 移除事件监听
      window.removeEventListener('resize', () => {
        chart && chart.resize();
      });
    });
    
    return {
      loading,
      statistics,
      promptUsageChart,
      getActivityTypeColor,
      getActivityTypeText,
      loadDashboardData
    };
  }
};
</script>

<style scoped>
.dashboard {
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

.dashboard-content {
  margin-top: 16px;
}

.ant-card {
  margin-bottom: 16px;
}
</style> 