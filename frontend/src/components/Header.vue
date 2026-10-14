<template>
  <header class="top-header">
    <div class="header-breadcrumb">
      <span class="breadcrumb-root">LinkedIn AI</span>
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-active">{{ currentTitle }}</span>
    </div>

    <div class="header-actions">
      <button 
        class="btn-ghost" 
        :disabled="isCheckingScheduler"
        title="Trigger scheduled posts check"
        @click="triggerSchedulerCheck"
      >
        <svg 
          viewBox="0 0 24 24" 
          width="16" 
          height="16" 
          fill="none" 
          stroke="currentColor" 
          stroke-width="2"
          :class="{ spin: isCheckingScheduler }"
        >
          <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"></path>
        </svg>
        <span>{{ isCheckingScheduler ? 'Checking...' : 'Check Scheduler' }}</span>
      </button>

      <button class="btn-secondary" @click="handleNewManualPost">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        <span>New Manual Post</span>
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue';
import { useApp } from '@/composables/useApp';

const emit = defineEmits(['focus-topic']);
const { activeTab, isCheckingScheduler, triggerSchedulerCheck } = useApp();

const titles = {
  studio: 'Creation Studio',
  queue: 'Queue & Scheduled',
  settings: 'Settings & Connection'
};

const currentTitle = computed(() => titles[activeTab.value] || 'Creation Studio');

function handleNewManualPost() {
  activeTab.value = 'studio';
  emit('focus-topic');
}
</script>
