import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue')
    },
    {
      path: '/',
      component: () => import('@/views/HomeView.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue')
        },
        {
          path: 'medication-box',
          name: 'medicationBox',
          component: () => import('@/views/medication/MedicationBoxView.vue')
        },
        {
          path: 'schedules',
          name: 'schedules',
          component: () => import('@/views/medication/ScheduleView.vue')
        },
        {
          path: 'symptoms',
          name: 'symptoms',
          component: () => import('@/views/medication/SymptomView.vue')
        },
        {
          path: 'doctor',
          name: 'doctor',
          component: () => import('@/views/DoctorView.vue')
        },
        {
          path: 'health-profile',
          name: 'healthProfile',
          component: () => import('@/views/HealthProfileView.vue')
        },
        {
          path: 'family',
          name: 'family',
          component: () => import('@/views/FamilyView.vue')
        },
        {
          path: 'user-profile',
          name: 'userProfile',
          component: () => import('@/views/UserProfileView.vue')
        },
        {
          path: 'chronic-disease',
          name: 'chronicDisease',
          component: () => import('@/views/ChronicDiseaseView.vue')
        },
        {
          path: 'chronic-disease/:id',
          name: 'chronicDiseaseDetail',
          component: () => import('@/views/ChronicDiseaseDetailView.vue')
        },
        {
          path: 'followup-schedule',
          name: 'followupSchedule',
          component: () => import('@/views/FollowupScheduleView.vue')
        }
      ]
    },
    // 管理员后台路由
    {
      path: '/admin/login',
      name: 'adminLogin',
      component: () => import('@/views/admin/AdminLoginView.vue')
    },
    {
      path: '/admin',
      component: () => import('@/views/admin/AdminLayout.vue'),
      redirect: '/admin/dashboard',
      meta: { requiresAdmin: true },
      children: [
        {
          path: 'dashboard',
          name: 'adminDashboard',
          component: () => import('@/views/admin/DashboardView.vue')
        },
        {
          path: 'users',
          name: 'adminUsers',
          component: () => import('@/views/admin/UsersView.vue')
        },
        {
          path: 'medicines',
          name: 'adminMedicines',
          component: () => import('@/views/admin/MedicinesView.vue')
        },
        {
          path: 'diseases',
          name: 'adminDiseases',
          component: () => import('@/views/admin/DiseasesView.vue')
        },
        {
          path: 'chronic',
          name: 'adminChronic',
          component: () => import('@/views/admin/ChronicView.vue')
        },
        {
          path: 'system',
          name: 'adminSystem',
          component: () => import('@/views/admin/SystemView.vue')
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // 管理员后台路由守卫
  if (to.path.startsWith('/admin')) {
    // 有 admin token 但 admin user 信息未加载时（如页面刷新），先获取
    if (userStore.adminToken && !userStore.adminUser) {
      try {
        await userStore.fetchAdminInfo()
      } catch {
        userStore.adminLogout()
        next('/admin/login')
        return
      }
    }

    // 管理员登录页不需要验证
    if (to.path === '/admin/login') {
      if (userStore.adminToken && userStore.adminUser?.is_admin) {
        next('/admin/dashboard')
      } else {
        next()
      }
      return
    }
    
    // 其他管理员页面需要验证
    if (!userStore.adminToken) {
      next('/admin/login')
      return
    }
    
    if (!userStore.adminUser?.is_admin) {
      next('/admin/login')
      return
    }
    
    next()
    return
  }

  // 普通用户路由：有 token 但 user 信息未加载时先获取
  if (userStore.token && !userStore.user) {
    try {
      await userStore.fetchUserInfo()
    } catch {
      userStore.logout()
      next('/login')
      return
    }
  }
  
  // 普通用户路由守卫
  if (to.path !== '/login' && !userStore.token) {
    next('/login')
  } else if (to.path === '/login' && userStore.token) {
    next('/')
  } else {
    next()
  }
})

export default router
