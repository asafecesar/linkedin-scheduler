<template>
  <div class="modal-backdrop" :class="{ open: scheduleModal.isOpen }" @click.self="closeScheduleModal">
    <div class="modal-dialog glass-card">
      <div class="modal-header">
        <div class="modal-title-group">
          <div class="gradient-badge">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            <span>Automation</span>
          </div>
          <h3>Schedule LinkedIn Post</h3>
        </div>
        <button class="btn-close-modal" @click="closeScheduleModal">×</button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label for="inputScheduleDateTime" class="form-label">Publish Date and Time</label>
          <input 
            type="datetime-local" 
            id="inputScheduleDateTime" 
            v-model="scheduleModal.dateTime" 
            class="form-input" 
          />
        </div>

        <!-- High Engagement Shortcuts -->
        <div class="quick-times-box">
          <span class="quick-times-label">High-Engagement Times on LinkedIn:</span>
          <div class="quick-time-buttons">
            <button type="button" class="btn-time-chip" @click="setTimePreset('08:30')">☀️ Morning (08:30)</button>
            <button type="button" class="btn-time-chip" @click="setTimePreset('12:15')">🥪 Lunch (12:15)</button>
            <button type="button" class="btn-time-chip" @click="setTimePreset('17:45')">🌆 End of Day (17:45)</button>
            <button type="button" class="btn-time-chip" @click="setOffsetPreset(2)">⏱️ In 2 Minutes (Test)</button>
          </div>
        </div>

        <div class="schedule-preview-snippet">
          {{ snippetText }}
        </div>

        <div v-if="scheduleModal.imageUrl" class="schedule-image-preview-box">
          <img :src="scheduleModal.imageUrl" alt="Media Preview" class="modal-preview-thumb" />
          <span class="modal-thumb-label">📷 Image attached for publishing</span>
        </div>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn-ghost" @click="closeScheduleModal">Cancel</button>
        <button 
          type="button" 
          class="btn-primary" 
          :disabled="isSubmitting"
          @click="confirmSchedule"
        >
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
          <span>{{ isSubmitting ? 'Scheduling...' : 'Confirm Schedule' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useApp } from '@/composables/useApp';
import { api } from '@/services/api';

const { scheduleModal, closeScheduleModal, showToast, fetchPosts } = useApp();
const isSubmitting = ref(false);

const snippetText = computed(() => {
  const content = scheduleModal.content || '';
  return content.length > 150 ? content.substring(0, 150) + '...' : content;
});

function setTimePreset(timeStr) {
  const [hours, minutes] = timeStr.split(':').map(Number);
  const target = new Date();
  target.setHours(hours, minutes, 0, 0);
  if (target < new Date()) {
    target.setDate(target.getDate() + 1);
  }
  formatAndSet(target);
}

function setOffsetPreset(minutes) {
  const target = new Date();
  target.setMinutes(target.getMinutes() + minutes);
  formatAndSet(target);
}

function formatAndSet(date) {
  const pad = n => String(n).padStart(2, '0');
  scheduleModal.dateTime = `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

async function confirmSchedule() {
  if (!scheduleModal.dateTime) {
    showToast('Please select a valid date and time.', 'error');
    return;
  }

  const scheduledIso = new Date(scheduleModal.dateTime).toISOString();
  isSubmitting.value = true;

  try {
    if (scheduleModal.postId) {
      await api.updatePost(scheduleModal.postId, {
        status: 'scheduled',
        scheduled_at: scheduledIso,
        image_url: scheduleModal.imageUrl,
        error_message: null
      });
    } else {
      await api.createPost({
        topic: scheduleModal.topic || 'Scheduled Post',
        content: scheduleModal.content,
        status: 'scheduled',
        scheduled_at: scheduledIso,
        image_url: scheduleModal.imageUrl
      });
    }

    showToast('Post scheduled successfully!', 'success');
    closeScheduleModal();
    await fetchPosts();
  } catch (err) {
    showToast(err.message || 'Failed to schedule post.', 'error');
  } finally {
    isSubmitting.value = false;
  }
}
</script>
