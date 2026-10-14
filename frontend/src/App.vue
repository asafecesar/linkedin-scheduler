<script setup>
import { onMounted } from 'vue';
import { useApp } from '@/composables/useApp';
import Sidebar from '@/components/Sidebar.vue';
import Header from '@/components/Header.vue';
import StudioView from '@/components/studio/StudioView.vue';
import QueueView from '@/components/queue/QueueView.vue';
import SettingsView from '@/components/settings/SettingsView.vue';
import ScheduleModal from '@/components/modals/ScheduleModal.vue';
import RefineModal from '@/components/modals/RefineModal.vue';
import ToastContainer from '@/components/ToastContainer.vue';

const { activeTab, refreshAll } = useApp();

onMounted(async () => {
  await refreshAll();
});
</script>

<template>
  <div class="app-layout">
    <!-- Sidebar Navigation -->
    <Sidebar />

    <!-- Main Content Area -->
    <main class="main-content">
      <Header />

      <!-- View Panels -->
      <StudioView v-if="activeTab === 'studio'" />
      <QueueView v-if="activeTab === 'queue'" />
      <SettingsView v-if="activeTab === 'settings'" />
    </main>
  </div>

  <!-- Global Modals -->
  <ScheduleModal />
  <RefineModal />

  <!-- Toast Notifications -->
  <ToastContainer />
</template>
