<script setup>
import { ref, computed } from 'vue';
import { useApp } from '@/composables/useApp';
import FeedSimulator from './FeedSimulator.vue';

const { state, generateDrafts, showToast } = useApp();

const topic = ref('');
const selectedAngle = ref('Practical Insight');
const selectedCount = ref(3);
const customNotes = ref('');

const suggestions = [
  { label: '🍁 Ottawa Tech Corridor', text: 'Building resilient software systems in the Ottawa and Canadian tech corridor' },
  { label: '⚡ Dev Leverage & Automation', text: 'How our engineering team eliminated repetitive deployment toil and reclaimed 10 hours a week' },
  { label: '🏛️ Cloud & Modernization', text: 'Navigating legacy modernizations in Canadian enterprise and GovTech without stalling delivery' },
  { label: '🚀 Shipping vs Over-Engineering', text: 'Why the simplest architecture running reliably in production always beats the theoretically perfect one' }
];

const angles = [
  { value: 'Practical Insight', label: '⚡ Practical Insight (Problem → Revelation → Action)' },
  { value: 'Framework / Strategy', label: '📐 Framework / Strategy (Step-by-step with arrows)' },
  { value: 'Story & Lessons', label: '📖 Personal Story & Real Takeaway' },
  { value: 'Contrarian View', label: '🔥 Contrarian View (Challenging conventional wisdom)' },
  { value: 'Checklist & Actionable Tips', label: '📋 Actionable Checklist & Quick Tips' }
];

function setSuggestion(text) {
  topic.value = text;
}

function setCount(count) {
  selectedCount.value = count;
}

async function handleGenerate() {
  if (!topic.value.trim()) {
    showToast('Please enter a topic or select one of the suggestions.', 'warning');
    return;
  }
  await generateDrafts(topic.value, selectedAngle.value, selectedCount.value, customNotes.value);
}

const ollamaModelName = computed(() => {
  return state.settings?.ollama_model || 'qwen2.5:14b';
});

const ollamaOnline = computed(() => {
  return !!state.settings?.ollama_online;
});
</script>

<template>
  <section class="tab-panel active" id="tabStudio">
    <div class="studio-grid">
      <!-- Left: Prompting & Controls -->
      <div class="studio-input-panel">
        <div class="panel-card glass-card">
          <div class="card-header-styled">
            <div class="header-title-group">
              <div class="gradient-badge">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                </svg>
                <span>AI Ghostwriter</span>
              </div>
              <h2>LinkedIn Post Generator</h2>
            </div>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: flex-end;">
              <div class="engine-status-pill" id="activeEngineBadge" title="Active AI engine and role">
                <span class="dot" :style="{ background: ollamaOnline ? 'var(--emerald-success)' : 'var(--rose-danger)' }"></span>
                <span>🦙 Ollama Local ({{ ollamaModelName }})</span>
              </div>
            </div>
          </div>

          <!-- Topic input -->
          <div class="form-group">
            <label for="inputTopic" class="form-label">
              What do you want to talk about today?
              <span class="label-hint">Technical topic or career lesson (Crafted in <strong>English</strong> for tech leaders & engineers)</span>
            </label>
            <textarea
              id="inputTopic"
              v-model="topic"
              class="form-textarea"
              rows="3"
              placeholder="e.g. Why over-engineering early architecture hurts SaaS velocity, or lessons building scalable systems in production..."
            ></textarea>

            <!-- Quick Inspiration Chips -->
            <div class="topic-chips-container">
              <span class="chips-label">Suggestions:</span>
              <button
                v-for="sug in suggestions"
                :key="sug.label"
                type="button"
                class="chip-btn"
                @click="setSuggestion(sug.text)"
              >
                {{ sug.label }}
              </button>
            </div>
          </div>

          <!-- Angle & Quantity Selectors -->
          <div class="form-row">
            <div class="form-group col-half">
              <label for="selectAngle" class="form-label">Post Angle / Structure</label>
              <select id="selectAngle" v-model="selectedAngle" class="form-select">
                <option v-for="ang in angles" :key="ang.value" :value="ang.value">
                  {{ ang.label }}
                </option>
              </select>
            </div>

            <div class="form-group col-half">
              <label class="form-label">Variations to Generate</label>
              <div class="toggle-group" id="countToggleGroup">
                <button
                  type="button"
                  class="toggle-btn"
                  :class="{ active: selectedCount === 1 }"
                  @click="setCount(1)"
                >
                  1 Post
                </button>
                <button
                  type="button"
                  class="toggle-btn"
                  :class="{ active: selectedCount === 3 }"
                  @click="setCount(3)"
                >
                  3 Options
                </button>
                <button
                  type="button"
                  class="toggle-btn"
                  :class="{ active: selectedCount === 5 }"
                  @click="setCount(5)"
                >
                  5 Options
                </button>
              </div>
            </div>
          </div>

          <!-- Additional constraints -->
          <div class="form-group">
            <label for="inputCustomNotes" class="form-label">
              Additional Instructions <span class="label-optional">(Optional)</span>
            </label>
            <input
              type="text"
              id="inputCustomNotes"
              v-model="customNotes"
              class="form-input"
              placeholder="e.g. Don't mention specific vendor tools, focus on the opening hook..."
            />
          </div>

          <!-- AI Engine Indicator -->
          <div class="form-group">
            <label class="form-label">
              Local AI Engine & Specialized Role
              <span class="label-hint">Role: <strong>LinkedIn Content Creator (Ottawa Tech)</strong></span>
            </label>
            <div class="active-engine-chip" id="engineActiveChip">
              <span class="engine-chip-icon">🦙</span>
              <div class="engine-chip-details">
                <span class="engine-chip-name">Ollama Local</span>
                <span class="engine-chip-model">{{ ollamaModelName }} • Private Local Execution</span>
              </div>
              <span class="status-pill-badge" :class="ollamaOnline ? 'active' : 'inactive'">
                {{ ollamaOnline ? 'Connected' : 'Offline' }}
              </span>
            </div>
          </div>

          <!-- Action Button -->
          <div class="studio-action-row">
            <button
              class="btn-primary btn-sparkle"
              id="btnGeneratePosts"
              :disabled="state.loadingPosts"
              @click="handleGenerate"
            >
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2">
                <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3z"></path>
              </svg>
              <span>{{ state.loadingPosts ? 'Crafting High-Converting Posts...' : 'Generate Drafts with AI' }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Right: Interactive Results & LinkedIn Simulator -->
      <div class="studio-preview-panel">
        <div class="preview-panel-header">
          <div class="preview-tabs">
            <span class="preview-title">Generated Drafts</span>
            <span class="results-counter" id="draftsCountBadge">{{ state.generatedDrafts.length }} drafts</span>
          </div>
          <div class="preview-actions">
            <span class="sim-badge">Official Feed Simulator</span>
          </div>
        </div>

        <!-- Drafts container -->
        <div class="drafts-container" id="draftsContainer">
          <!-- Loading skeleton -->
          <div v-if="state.loadingPosts" class="empty-state-card glass-card" style="text-align: center; padding: 3rem 1.5rem;">
            <div class="empty-icon-circle" style="animation: spin 2s linear infinite;">
              <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"></path>
              </svg>
            </div>
            <h3 style="margin-top: 1rem;">Ollama is writing your LinkedIn posts...</h3>
            <p>Structuring strong hooks, bulleted insights, and engaging CTAs designed for the algorithm.</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="state.generatedDrafts.length === 0" class="empty-state-card glass-card">
            <div class="empty-icon-circle">
              <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
            </div>
            <h3>Ready to create high-impact content?</h3>
            <p>Enter your topic on the left or select a quick suggestion, then click <strong>Generate Drafts with AI</strong>.</p>
            <div class="tips-pill">
              ✨ Tip: The AI formats posts with optimal line breaks for mobile reading and hooks designed to maximize "...see more" clicks.
            </div>
          </div>

          <!-- Render drafts -->
          <template v-else>
            <FeedSimulator
              v-for="(draft, idx) in state.generatedDrafts"
              :key="idx"
              :draft="draft"
              :index="idx"
            />
          </template>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}
</style>
