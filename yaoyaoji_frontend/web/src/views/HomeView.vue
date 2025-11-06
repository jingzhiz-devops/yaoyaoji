<template>
  <div class="home-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>💊 药药记</h2>
          <div class="user-info">
            <el-dropdown @command="handleCommand">
              <span class="user-dropdown">
                {{ userStore.user?.username }}
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="userProfile">
                    <el-icon><User /></el-icon>
                    用户信息
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <el-container>
        <el-aside width="200px">
          <el-menu :default-active="activeMenu" router>
            <el-menu-item index="/dashboard">
              <template #title>
                <el-icon><House /></el-icon>
                <span>首页</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/medication-box">
              <template #title>
                <el-icon><Box /></el-icon>
                <span>我的药箱</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/schedules">
              <template #title>
                <el-icon><Clock /></el-icon>
                <span>用药提醒</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/symptoms">
              <template #title>
                <el-icon><Document /></el-icon>
                <span>症状记录</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/doctor">
              <template #title>
                <el-icon><ChatDotRound /></el-icon>
                <span>AI 医生</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/health-profile">
              <template #title>
                <el-icon><User /></el-icon>
                <span>健康档案</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/family">
              <template #title>
                <el-icon><UserFilled /></el-icon>
                <span>家庭管理</span>
              </template>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { House, Box, Clock, Document, ChatDotRound, User, UserFilled, ArrowDown, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref(route.path)

onMounted(async () => {
  if (userStore.token && !userStore.user) {
    await userStore.fetchUserInfo()
  }
})

function handleCommand(command: string) {
  if (command === 'logout') {
    handleLogout()
  } else if (command === 'userProfile') {
    router.push('/user-profile')
  }
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.home-container {
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
}

.el-container {
  height: 100%;
}

.el-header {
  background-color: #667eea;
  color: white;
  display: flex;
  align-items: center;
  height: 60px;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-dropdown:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.el-aside {
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

.el-main {
  background-color: #fff;
  padding: 20px;
  height: calc(100vh - 60px);
  overflow-y: auto;
}
</style>
