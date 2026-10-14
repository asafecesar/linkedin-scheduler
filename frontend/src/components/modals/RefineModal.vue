<template>
  <div class="modal-backdrop" :class="{ open: refineModal.isOpen }" @click.self="closeRefineModal">
    <div class="modal-dialog glass-card">
      <div class="modal-header">
        <div class="modal-title-group">
          <div class="gradient-badge">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
            </svg>
            <span>AI Refiner</span>
          </div>
          <h3>1-Click AI Post Refinement</h3>
        </div>
        <button class="btn-close-modal" @click="closeRefineModal">×</button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">Choose a quick adjustment:</label>
          <div class="refine-quick-chips">
            <button 
              type="button" 
              class="btn-refine-chip"
              :disabled="isRefining"
              @click="executeRefine('Make the opening hook significantly more magnetic and shorten sentences for fast mobile reading.')"
            >
              ⚡ Punchier & High-Impact
            </button>
            <button 
              type="button" 
              class="btn-refine-chip"
              :disabled="isRefining"
              @click="executeRefine('Add an engaging, open-ended discussion question at the end to prompt thoughtful comments.')"
            >
              💬 Add Engagement Question
            </button>
            <button 
              type="button" 
              class="btn-refine-chip"
              :disabled="isRefining"
              @click="executeRefine('Format the key points into clean bullet points with scannable Unicode markers.')"
            >
              📋 Format as Bullet Points
            </button>
            <button 
              type="button" 
              class="btn-refine-chip"
              :disabled="isRefining"
              @click="executeRefine('Shorten the post by 30%, keeping only the core insights and eliminating filler words.')"
            >
              ✂️ Shorten & Condense
            </button>
          </div>
        </div>

        <div class="form-group">
          <label for="inputCustomRefinePrompt" class="form-label">Or enter a custom refinement instruction:</label>
          <input 
            type="text" 
            id="inputCustomRefinePrompt" 
            v-model="customPrompt" 
            class="form-input"
            placeholder="e.g. Make the tone slightly more candid by sharing the initial engineering frustration..."
            :disabled="isRefining"
            @keydown.enter.prevent="handleCustomRefine"
          />
        </div>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn-ghost" @click="closeRefineModal">Cancel</button>
        <button 
          type="button" 
          class="btn-primary" 
          :disabled="isRefining"
          @click="handleCustomRefine"
        >
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
          </svg>
          <span>{{ isRefining ? 'Refining...' : 'Apply Refinement' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useApp } from '@/composables/useApp';
import { api } from '@/services/api';

const { refineModal, closeRefineModal, generatedDrafts, showToast } = useApp();
const customPrompt = ref('');
const isRefining = ref(false);

function handleCustomRefine() {
  if (!customPrompt.value.trim()) {
    showToast('Please enter an instruction for the refiner.', 'error');
    return;
  }
  executeRefine(customPrompt.value.trim());
}

async function executeRefine(instruction) {
  const idx = refineModal.draftIdx;
  const draft = generatedDrafts.value[idx];
  if (!draft) return;

  isRefining.value = true;
  showToast('Refining post with AI (Role: LinkedIn Creator)...', 'info');
  closeRefineModal();

  try {
    const res = await api.refinePost({
      content: draft.content,
      instruction,
      provider: 'ollama'
    });

    draft.content = res.refined;
    customPrompt.value = '';
    showToast('Post refined successfully!', 'success');
  } catch (err) {
    showToast(err.message || 'Failed to refine post.', 'error');
  } finally {
    isRefining.value = false;
  }
}
</script>
