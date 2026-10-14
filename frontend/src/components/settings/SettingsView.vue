<script setup>
import { ref, computed, watch } from 'vue';
import { useApp } from '@/composables/useApp';
import { api } from '@/services/api';

const { state, fetchHealthAndSettings, showToast } = useApp();

// Ollama fields
const ollamaUrl = ref('http://127.0.0.1:11434');
const selectedModel = ref('qwen2.5:14b');
const availableModels = ref(['qwen2.5:14b']);
const testingOllama = ref(false);

// LinkedIn fields
const linkedinToken = ref('');
const linkedinUrn = ref('');
const showTokenMask = ref(false);
const testingLinkedIn = ref(false);

// Profile Visual fields
const userName = ref('');
const userHeadline = ref('');
const userAvatar = ref('');

// Populate from state.settings
watch(
  () => state.settings,
  (s) => {
    if (!s) return;
    if (s.ollama_base_url) ollamaUrl.value = s.ollama_base_url;
    if (s.ollama_model) selectedModel.value = s.ollama_model;
    if (s.ollama_available_models && s.ollama_available_models.length) {
      availableModels.value = s.ollama_available_models;
    }
    if (s.linkedin_person_urn) linkedinUrn.value = s.linkedin_person_urn;
    if (s.user_name) userName.value = s.user_name;
    if (s.user_headline) userHeadline.value = s.user_headline;
    if (s.user_avatar_url) userAvatar.value = s.user_avatar_url;
  },
  { immediate: true }
);

const ollamaStatusText = computed(() => {
  if (state.settings?.ollama_online) return 'Online & Connected';
  return 'Offline';
});

const linkedinStatusText = computed(() => {
  if (state.settings?.linkedin_connected) {
    return state.settings?.user_name ? `Connected (${state.settings.user_name})` : 'Connected';
  }
  return 'Not connected';
});

// Test & List Ollama Models
async function testOllama() {
  testingOllama.value = true;
  showToast('Querying local Ollama server...', 'info');
  try {
    const data = await api.getOllamaStatus();
    if (data.online) {
      availableModels.value = data.available_models || [];
      if (data.current_model) selectedModel.value = data.current_model;
      showToast(`Ollama connected! Models: ${(data.available_models || []).join(', ')}`, 'success');
    } else {
      showToast(`Ollama offline or unreachable (${data.error || 'Ensure ollama serve is running'})`, 'error');
    }
    await fetchHealthAndSettings();
  } catch (err) {
    showToast('Failed to connect to Ollama.', 'error');
  } finally {
    testingOllama.value = false;
  }
}

// Save Ollama Config
async function saveOllama() {
  try {
    await api.saveSettings({
      ollama_base_url: ollamaUrl.value.trim(),
      ollama_model: selectedModel.value,
      ai_provider: 'ollama'
    });
    showToast('Ollama configuration saved successfully!', 'success');
    await fetchHealthAndSettings();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Verify LinkedIn Token
async function verifyLinkedIn() {
  testingLinkedIn.value = true;
  showToast('Testing connection to LinkedIn API...', 'info');
  try {
    const token = linkedinToken.value.trim() || undefined;
    const data = await api.verifyLinkedIn(token);
    showToast(`Connected successfully as: ${data.name}!`, 'success');
    if (data.person_urn) {
      linkedinUrn.value = data.person_urn;
    }
    await fetchHealthAndSettings();
  } catch (err) {
    showToast(err.message || 'Failed to validate LinkedIn token.', 'error');
  } finally {
    testingLinkedIn.value = false;
  }
}

// Save LinkedIn Settings
async function saveLinkedIn() {
  const payload = {};
  if (linkedinToken.value.trim()) payload.linkedin_access_token = linkedinToken.value.trim();
  if (linkedinUrn.value.trim()) payload.linkedin_person_urn = linkedinUrn.value.trim();

  try {
    await api.saveSettings(payload);
    showToast('LinkedIn settings saved!', 'success');
    linkedinToken.value = '';
    await fetchHealthAndSettings();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Save Profile Visual
async function saveProfile() {
  try {
    await api.saveSettings({
      user_name: userName.value.trim(),
      user_headline: userHeadline.value.trim(),
      user_avatar_url: userAvatar.value.trim()
    });
    showToast('Author profile updated successfully!', 'success');
    await fetchHealthAndSettings();
  } catch (err) {
    showToast(err.message, 'error');
  }
}
</script>

<template>
  <section class="tab-panel active" id="tabSettings">
    <div class="settings-grid">
      <!-- Ollama Local AI Integration -->
      <div class="panel-card glass-card">
        <div class="card-header-styled">
          <div class="header-title-group">
            <div class="gradient-badge purple">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
                <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
                <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
                <line x1="6" y1="6" x2="6.01" y2="6"></line>
                <line x1="6" y1="18" x2="6.01" y2="18"></line>
              </svg>
              <span>Local AI (Offline & Private)</span>
            </div>
            <h2>Ollama Server (Local)</h2>
          </div>
          <span class="status-pill-badge" :class="state.settings?.ollama_online ? 'active' : 'inactive'" id="ollamaBadge">
            {{ ollamaStatusText }}
          </span>
        </div>

        <p class="panel-subtitle">
          100% private, hardware-accelerated local execution. Active role: <strong>LinkedIn Content Creator & Ghostwriter</strong>.
        </p>

        <form @submit.prevent="saveOllama" id="formOllamaConfig">
          <div class="form-group">
            <label for="inputOllamaUrl" class="form-label">Ollama Address</label>
            <input
              type="text"
              id="inputOllamaUrl"
              v-model="ollamaUrl"
              class="form-input code-font"
              placeholder="http://127.0.0.1:11434"
            />
          </div>

          <div class="form-group">
            <label for="selectOllamaModel" class="form-label">Active Ollama Model</label>
            <select id="selectOllamaModel" v-model="selectedModel" class="form-select">
              <option v-for="model in availableModels" :key="model" :value="model">
                {{ model }}
              </option>
            </select>
          </div>

          <div class="form-actions-split">
            <button
              type="button"
              class="btn-secondary"
              id="btnTestOllama"
              :disabled="testingOllama"
              @click="testOllama"
            >
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 4 23 10 17 10"></polyline>
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
              </svg>
              <span>{{ testingOllama ? 'Testing...' : 'Test & List Models' }}</span>
            </button>
            <button type="submit" class="btn-primary">Save Ollama</button>
          </div>
        </form>
      </div>

      <!-- LinkedIn API Integration -->
      <div class="panel-card glass-card">
        <div class="card-header-styled">
          <div class="header-title-group">
            <div class="gradient-badge linkedin">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"></path>
              </svg>
              <span>Official LinkedIn</span>
            </div>
            <h2>LinkedIn Account Connection</h2>
          </div>
          <span class="status-pill-badge" :class="state.settings?.linkedin_connected ? 'active' : 'inactive'" id="linkedinBadge">
            {{ linkedinStatusText }}
          </span>
        </div>

        <p class="panel-subtitle">
          Enables direct scheduling and publishing to your LinkedIn feed via REST and UGC APIs.
        </p>

        <form @submit.prevent="saveLinkedIn" id="formLinkedInToken">
          <div class="form-group">
            <label for="inputLinkedInToken" class="form-label">
              LinkedIn OAuth Access Token
              <span class="label-hint">Token with scopes <code>w_member_social</code> and <code>openid/profile</code></span>
            </label>
            <div class="input-with-button">
              <input
                :type="showTokenMask ? 'text' : 'password'"
                id="inputLinkedInToken"
                v-model="linkedinToken"
                class="form-input"
                placeholder="AQV..."
              />
              <button
                type="button"
                class="btn-toggle-mask"
                id="btnToggleLinkedInMask"
                @click="showTokenMask = !showTokenMask"
              >
                {{ showTokenMask ? '🔒' : '👁️' }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label for="inputLinkedInUrn" class="form-label">
              Author Person URN <span class="label-optional">(Automatically populated upon verification)</span>
            </label>
            <input
              type="text"
              id="inputLinkedInUrn"
              v-model="linkedinUrn"
              class="form-input code-font"
              placeholder="urn:li:person:abcdef123"
            />
          </div>

          <div class="form-actions-split">
            <button
              type="button"
              class="btn-secondary"
              id="btnVerifyLinkedInToken"
              :disabled="testingLinkedIn"
              @click="verifyLinkedIn"
            >
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              <span>{{ testingLinkedIn ? 'Verifying...' : 'Test & Sync Profile' }}</span>
            </button>
            <button type="submit" class="btn-primary">Save Settings</button>
          </div>
        </form>
      </div>

      <!-- Profile Customization -->
      <div class="panel-card glass-card col-span-2">
        <div class="card-header-styled">
          <div class="header-title-group">
            <div class="gradient-badge">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              <span>Visual Identity</span>
            </div>
            <h2>Author Profile for Feed Simulator</h2>
          </div>
        </div>

        <form @submit.prevent="saveProfile" id="formProfileVisual">
          <div class="form-row">
            <div class="form-group col-third">
              <label for="inputUserName" class="form-label">Your Full Name</label>
              <input
                type="text"
                id="inputUserName"
                v-model="userName"
                class="form-input"
                placeholder="e.g. Asafe Cesar"
              />
            </div>

            <div class="form-group col-third">
              <label for="inputUserHeadline" class="form-label">Professional Headline / Title</label>
              <input
                type="text"
                id="inputUserHeadline"
                v-model="userHeadline"
                class="form-input"
                placeholder="e.g. Software Engineer | AI & Cloud"
              />
            </div>

            <div class="form-group col-third">
              <label for="inputUserAvatar" class="form-label">Profile Photo URL</label>
              <input
                type="url"
                id="inputUserAvatar"
                v-model="userAvatar"
                class="form-input"
                placeholder="https://..."
              />
            </div>
          </div>

          <div class="form-actions-right">
            <button type="submit" class="btn-secondary">Update Simulator Profile</button>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>
