<template>
  <div class="home-container">
    <el-container class="main-layout">
      <el-aside width="260px" class="sidebar">
        <div class="brand">
          <div class="logo-icon">
            <el-icon :size="24" color="white"><FirstAidKit /></el-icon>
          </div>
          <h2>药药记</h2>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          router
          class="custom-menu"
          :collapse-transition="false"
        >
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/medication-box">
            <el-icon><Box /></el-icon>
            <span>我的药箱</span>
          </el-menu-item>
          <el-menu-item index="/schedules">
            <el-icon><Clock /></el-icon>
            <span>用药提醒</span>
          </el-menu-item>
          <el-menu-item index="/symptoms">
            <el-icon><Document /></el-icon>
            <span>症状记录</span>
          </el-menu-item>
          <el-menu-item index="/doctor">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI 医生</span>
          </el-menu-item>
          <el-menu-item index="/health-profile">
            <el-icon><User /></el-icon>
            <span>健康档案</span>
          </el-menu-item>
          <el-menu-item index="/chronic-disease">
            <el-icon><CircleCheck /></el-icon>
            <span>慢性病管理</span>
          </el-menu-item>
          <el-menu-item index="/family">
            <el-icon><UserFilled /></el-icon>
            <span>家庭管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container class="content-container">
        <el-main class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { 
  House, Box, Clock, Document, ChatDotRound, User, UserFilled, 
  SwitchButton, FirstAidKit, CircleCheck
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const activeMenu = computed(() => route.path)

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
  background-color: var(--color-bg-page);
  display: flex;
}

.main-layout {
  height: 100%;
  width: 100%;
}

/* Sidebar Styling */
.sidebar {
  background-color: var(--color-bg-sidebar);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  z-index: 10;
}

.brand {
  height: 80px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
}

.brand h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-main);
  margin: 0;
  letter-spacing: 0.5px;
}

.custom-menu {
  border-right: none;
  flex: 1;
  padding: 12px;
  background: transparent;
}

:deep(.el-menu-item) {
  border-radius: var(--radius-md);
  margin-bottom: 4px;
  height: 50px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

:deep(.el-menu-item:hover) {
  background-color: var(--color-bg-page);
  color: var(--color-primary);
}

:deep(.el-menu-item.is-active) {
  background-color: var(--color-primary-light);
  color: white;
  box-shadow: var(--shadow-sm);
}

:deep(.el-menu-item.is-active:hover) {
  background-color: var(--color-primary);
}

:deep(.el-menu-item .el-icon) {
  font-size: 20px;
  margin-right: 12px;
}

/* Main Content Area */
.content-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  padding: 40px;
  overflow-y: auto;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
