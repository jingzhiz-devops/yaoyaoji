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
        },
        {
          path: 'chronic-disease-stats',
          name: 'chronicDiseaseStats',
          component: () => import('@/views/ChronicDiseaseStatsView.vue')
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.path !== '/login' && !userStore.token) {
    next('/login')
  } else if (to.path === '/login' && userStore.token) {
    next('/')
  } else {
    next()
  }
})

export default router
