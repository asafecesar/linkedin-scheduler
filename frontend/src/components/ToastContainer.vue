<template>
  <div class="toast-container">
    <transition-group name="toast">
      <div 
        v-for="toast in toasts" 
        :key="toast.id" 
        class="toast" 
        :class="toast.type"
        @click="removeToast(toast.id)"
      >
        <span>{{ getIcon(toast.type) }}</span>
        <span>{{ toast.message }}</span>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useApp } from '@/composables/useApp';

const { toasts, removeToast } = useApp();

function getIcon(type) {
  const map = {
    success: '✅',
    error: '❌',
    info: '💡'
  };
  return map[type] || '💡';
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(50px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(50px);
}
</style>
