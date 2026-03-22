<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { heartbeatService } from '@/services/heartbeat'

onMounted(() => {
  const token = localStorage.getItem('token') || localStorage.getItem('admin_token')
  if (token) {
    heartbeatService.connect(token)
  }
})
</script>

<template>
  <RouterView />
</template>

<style>
#app {
  margin: 0;
  padding: 0;
  min-height: 100vh;
}

body {
  margin: 0;
  padding: 0;
}
</style>
