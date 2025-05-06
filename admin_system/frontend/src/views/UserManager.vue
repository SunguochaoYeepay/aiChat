<template>
  <div class="user-manager-container">
    <a-card title="用户管理" :bordered="false">
      <template #extra>
        <a-button type="primary" @click="showCreateModal">
          <template #icon><plus-outlined /></template>
          创建用户
        </a-button>
      </template>

      <a-table
        :columns="columns"
        :data-source="users"
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
          <template v-else-if="column.dataIndex === 'is_staff'">
            <a-tag :color="record.is_staff ? 'blue' : 'default'">
              {{ record.is_staff ? '管理员' : '普通用户' }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'action'">
            <a-space>
              <a-button type="link" @click="showEditModal(record)">编辑</a-button>
              <a-popconfirm
                title="确定要删除这个用户吗？"
                ok-text="确定"
                cancel-text="取消"
                @confirm="deleteUser(record)"
              >
                <a-button type="link" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>

      <!-- 创建用户弹窗 -->
      <a-modal
        v-model:visible="createModalVisible"
        title="创建用户"
        @ok="handleCreateUser"
        :confirmLoading="modalLoading"
      >
        <a-form
          :model="userForm"
          :rules="rules"
          ref="createFormRef"
          layout="vertical"
        >
          <a-form-item label="用户名" name="username">
            <a-input v-model:value="userForm.username" placeholder="请输入用户名" />
          </a-form-item>
          <a-form-item label="邮箱" name="email">
            <a-input v-model:value="userForm.email" placeholder="请输入邮箱" />
          </a-form-item>
          <a-form-item label="密码" name="password">
            <a-input-password v-model:value="userForm.password" placeholder="请输入密码" />
          </a-form-item>
          <a-form-item name="is_staff">
            <a-checkbox v-model:checked="userForm.is_staff">设为管理员</a-checkbox>
          </a-form-item>
        </a-form>
      </a-modal>

      <!-- 编辑用户弹窗 -->
      <a-modal
        v-model:visible="editModalVisible"
        title="编辑用户"
        @ok="handleUpdateUser"
        :confirmLoading="modalLoading"
      >
        <a-form
          :model="userForm"
          :rules="editRules"
          ref="editFormRef"
          layout="vertical"
        >
          <a-form-item label="用户名" name="username">
            <a-input v-model:value="userForm.username" placeholder="请输入用户名" />
          </a-form-item>
          <a-form-item label="邮箱" name="email">
            <a-input v-model:value="userForm.email" placeholder="请输入邮箱" />
          </a-form-item>
          <a-form-item label="密码" name="password" extra="如不修改密码请留空">
            <a-input-password v-model:value="userForm.password" placeholder="请输入新密码" />
          </a-form-item>
          <a-form-item name="is_active">
            <a-checkbox v-model:checked="userForm.is_active">启用账户</a-checkbox>
          </a-form-item>
          <a-form-item name="is_staff">
            <a-checkbox v-model:checked="userForm.is_staff">设为管理员</a-checkbox>
          </a-form-item>
        </a-form>
      </a-modal>
    </a-card>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { PlusOutlined } from '@ant-design/icons-vue';
import { getUserList, createUser, updateUser, deleteUser as apiDeleteUser } from '../api/auth';

export default defineComponent({
  name: 'UserManager',
  components: {
    PlusOutlined
  },
  setup() {
    const users = ref([]);
    const loading = ref(false);
    const createModalVisible = ref(false);
    const editModalVisible = ref(false);
    const modalLoading = ref(false);
    const currentUserId = ref(null);
    const createFormRef = ref(null);
    const editFormRef = ref(null);
    
    const columns = [
      { title: 'ID', dataIndex: 'id', key: 'id' },
      { title: '用户名', dataIndex: 'username', key: 'username' },
      { title: '邮箱', dataIndex: 'email', key: 'email' },
      { title: '状态', dataIndex: 'is_active', key: 'is_active' },
      { title: '角色', dataIndex: 'is_staff', key: 'is_staff' },
      { title: '创建时间', dataIndex: 'date_joined', key: 'date_joined' },
      { title: '最后登录', dataIndex: 'last_login', key: 'last_login' },
      { title: '操作', dataIndex: 'action', key: 'action' }
    ];
    
    const userForm = reactive({
      username: '',
      email: '',
      password: '',
      is_active: true,
      is_staff: false
    });
    
    const rules = {
      username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
      password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
    };
    
    const editRules = {
      username: [{ required: true, message: '请输入用户名', trigger: 'blur' }]
    };
    
    // 获取用户列表
    const fetchUsers = async () => {
      loading.value = true;
      try {
        const response = await getUserList();
        users.value = response.data.users;
      } catch (error) {
        console.error('获取用户列表失败:', error);
        message.error('获取用户列表失败');
      } finally {
        loading.value = false;
      }
    };
    
    // 显示创建用户弹窗
    const showCreateModal = () => {
      resetUserForm();
      createModalVisible.value = true;
    };
    
    // 显示编辑用户弹窗
    const showEditModal = (user) => {
      resetUserForm();
      currentUserId.value = user.id;
      userForm.username = user.username;
      userForm.email = user.email;
      userForm.password = ''; // 密码不回显
      userForm.is_active = user.is_active;
      userForm.is_staff = user.is_staff;
      editModalVisible.value = true;
    };
    
    // 重置表单
    const resetUserForm = () => {
      userForm.username = '';
      userForm.email = '';
      userForm.password = '';
      userForm.is_active = true;
      userForm.is_staff = false;
      currentUserId.value = null;
    };
    
    // 创建用户
    const handleCreateUser = async () => {
      try {
        await createFormRef.value.validate();
        modalLoading.value = true;
        
        await createUser({
          username: userForm.username,
          email: userForm.email,
          password: userForm.password,
          is_staff: userForm.is_staff
        });
        
        message.success('创建用户成功');
        createModalVisible.value = false;
        fetchUsers(); // 刷新用户列表
      } catch (error) {
        if (error.response && error.response.data) {
          message.error(error.response.data.error || '创建用户失败');
        } else if (error.message) {
          // 表单验证错误
          console.error('表单验证失败', error);
        } else {
          message.error('创建用户失败');
        }
      } finally {
        modalLoading.value = false;
      }
    };
    
    // 更新用户
    const handleUpdateUser = async () => {
      try {
        await editFormRef.value.validate();
        modalLoading.value = true;
        
        const updateData = {
          username: userForm.username,
          email: userForm.email,
          is_active: userForm.is_active,
          is_staff: userForm.is_staff
        };
        
        // 如果输入了密码，则更新密码
        if (userForm.password) {
          updateData.password = userForm.password;
        }
        
        await updateUser(currentUserId.value, updateData);
        
        message.success('更新用户成功');
        editModalVisible.value = false;
        fetchUsers(); // 刷新用户列表
      } catch (error) {
        if (error.response && error.response.data) {
          message.error(error.response.data.error || '更新用户失败');
        } else if (error.message) {
          // 表单验证错误
          console.error('表单验证失败', error);
        } else {
          message.error('更新用户失败');
        }
      } finally {
        modalLoading.value = false;
      }
    };
    
    // 删除用户
    const deleteUser = async (user) => {
      loading.value = true;
      try {
        await apiDeleteUser(user.id);
        message.success(`用户 ${user.username} 已删除`);
        fetchUsers(); // 刷新用户列表
      } catch (error) {
        if (error.response && error.response.data) {
          message.error(error.response.data.error || '删除用户失败');
        } else {
          message.error('删除用户失败');
        }
      } finally {
        loading.value = false;
      }
    };
    
    onMounted(() => {
      fetchUsers();
    });
    
    return {
      users,
      loading,
      columns,
      userForm,
      rules,
      editRules,
      createModalVisible,
      editModalVisible,
      modalLoading,
      createFormRef,
      editFormRef,
      showCreateModal,
      showEditModal,
      handleCreateUser,
      handleUpdateUser,
      deleteUser
    };
  }
});
</script>

<style scoped>
.user-manager-container {
  padding: 24px;
}
</style> 