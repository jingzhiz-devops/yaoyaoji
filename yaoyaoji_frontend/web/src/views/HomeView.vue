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
          <!-- 浮动装饰元素 -->
          <div class="floating-decorations">
            <div class="float-circle float-1"></div>
            <div class="float-circle float-2"></div>
            <div class="float-circle float-3"></div>
            <div class="float-circle float-4"></div>
            <div class="float-circle float-5"></div>
          </div>
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
  background: linear-gradient(180deg, #e8f7f3 0%, #f0faf7 50%, #e6f5f0 100%);
  border-right: 1px solid rgba(42, 157, 143, 0.15);
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  z-index: 10;
  position: relative;
  overflow: hidden;
}

/* 侧边栏浮动装饰 */
.sidebar::before {
  content: '';
  position: absolute;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(42, 157, 143, 0.1), rgba(42, 157, 143, 0.02));
  top: -60px;
  right: -60px;
  animation: sideFloat 18s infinite ease-in-out;
  pointer-events: none;
}

.sidebar::after {
  content: '';
  position: absolute;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(42, 157, 143, 0.08), rgba(42, 157, 143, 0.01));
  bottom: 80px;
  left: -40px;
  animation: sideFloat 24s infinite ease-in-out reverse;
  pointer-events: none;
}

@keyframes sideFloat {
  0%, 100% { transform: translate(0, 0); }
  33% { transform: translate(10px, -15px); }
  66% { transform: translate(-8px, 10px); }
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
  background-color: rgba(42, 157, 143, 0.08);
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
  background: linear-gradient(135deg, #e8f5f1 0%, #f0faf7 40%, #e6f7f2 70%, #f5fdf9 100%);
  position: relative;
}

/* 浮动装饰元素 */
.floating-decorations {
  position: fixed;
  top: 0;
  left: 260px;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.float-circle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(42, 157, 143, 0.08), rgba(42, 157, 143, 0.02));
  animation: floatUp 20s infinite ease-in-out;
}

.float-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  right: 5%;
  animation-duration: 18s;
  animation-delay: 0s;
}

.float-2 {
  width: 120px;
  height: 120px;
  top: 60%;
  right: 20%;
  animation-duration: 22s;
  animation-delay: -4s;
}

.float-3 {
  width: 160px;
  height: 160px;
  top: 30%;
  left: 10%;
  animation-duration: 25s;
  animation-delay: -8s;
}

.float-4 {
  width: 80px;
  height: 80px;
  bottom: 15%;
  left: 30%;
  animation-duration: 16s;
  animation-delay: -2s;
}

.float-5 {
  width: 100px;
  height: 100px;
  top: 70%;
  right: 40%;
  animation-duration: 20s;
  animation-delay: -6s;
}

@keyframes floatUp {
  0%, 100% {
    transform: translate(0, 0) scale(1);
    opacity: 0.6;
  }
  25% {
    transform: translate(15px, -20px) scale(1.05);
    opacity: 0.8;
  }
  50% {
    transform: translate(-10px, -35px) scale(1.1);
    opacity: 0.5;
  }
  75% {
    transform: translate(20px, -15px) scale(0.95);
    opacity: 0.7;
  }
}

.main-content > :not(.floating-decorations) {
  position: relative;
  z-index: 1;
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
