# 设计助手 - Vue + Django REST Framework 更新

## 重要更新

我们已经将设计助手项目迁移到了更现代化的技术栈，采用了Django REST框架和Vue.js前端。此次迁移主要在`vue-rest-refactor`分支中完成。

### 主要改进

1. **全新用户界面**：使用Vue.js和Ant Design Vue构建的现代化界面
2. **RESTful API**：通过Django REST框架实现的标准化API
3. **前后端分离**：更灵活的开发和部署模式
4. **改进的提示词管理**：更直观的提示词模板编辑和管理
5. **增强的知识库功能**：支持批量导入和向量化
6. **API测试工具**：内置API测试界面

### 如何访问新界面

新版界面可通过以下路径访问：

- 提示词管理：`/management/vue/#/prompts`
- 知识库管理：`/management/vue/#/knowledge`
- API测试：`/management/vue/#/api`

### 兼容性

所有原有API接口保持向后兼容，现有集成将继续正常工作。

### 详细文档

完整的迁移文档可在`docs/vue-rest-migration.md`中查看，包含：

- 技术架构变更
- API文档
- 部署指南
- 使用指南

## 后续计划

1. 添加更多高级功能
2. 改进用户体验
3. 优化性能
4. 添加更多集成测试 