import { ref, reactive, computed } from 'vue';
import { api } from '@/services/api';

// Global shared reactive state
const activeTab = ref('studio');
const isCheckingScheduler = ref(false);
const loadingPosts = ref(false);

const settings = reactive({
  ai_provider: 'ollama',
  ollama_base_url: 'http://127.0.0.1:11434',
  ollama_model: 'qwen2.5:14b',
  ollama_online: false,
  ollama_available_models: [],
  has_linkedin_token: false,
  linkedin_configured: false,
  linkedin_person_urn: '',
  user_name: 'Your Name',
  user_headline: 'Software Engineer & Tech Builder',
  user_avatar_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80'
});

const generatedDrafts = ref([]);
const posts = ref([]);
const activeFilter = ref('all');
const searchQuery = ref('');

// Modals State
const scheduleModal = reactive({
  isOpen: false,
  postId: null,
  draftIdx: null,
  topic: '',
  content: '',
  imageUrl: null,
  dateTime: ''
});

const refineModal = reactive({
  isOpen: false,
  draftIdx: null,
  content: ''
});

// Toasts State
const toasts = ref([]);
let toastIdCounter = 0;

// Computed queue statistics
const queueStats = computed(() => {
  const scheduled = posts.value.filter(p => p.status === 'scheduled').length;
  const published = posts.value.filter(p => p.status === 'published').length;
  const drafts = posts.value.filter(p => p.status === 'draft').length;
  const total = posts.value.length;
  return { scheduled, published, drafts, total };
});

// Unified state wrapper
const state = reactive({
  activeTab,
  isCheckingScheduler,
  loadingPosts,
  settings,
  generatedDrafts,
  posts,
  activeFilter,
  searchQuery
});

export function useApp() {
  function showToast(message, type = 'info') {
    const id = ++toastIdCounter;
    toasts.value.push({ id, message, type });
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id);
    }, 4000);
  }

  function removeToast(id) {
    toasts.value = toasts.value.filter(t => t.id !== id);
  }

  async function fetchSettings() {
    try {
      const [health, data] = await Promise.all([
        api.getHealth(),
        api.getSettings()
      ]);
      Object.assign(settings, data);
      settings.linkedin_configured = health.linkedin_configured;
      if (health.user_urn && !settings.linkedin_person_urn) {
        settings.linkedin_person_urn = health.user_urn;
      }
    } catch (err) {
      console.error('Failed to load settings:', err);
    }
  }

  async function fetchPosts() {
    try {
      const data = await api.getPosts();
      posts.value = data || [];
    } catch (err) {
      console.error('Failed to load posts:', err);
    }
  }

  async function fetchHealthAndSettings() {
    await fetchSettings();
  }

  async function refreshAll() {
    await Promise.all([fetchSettings(), fetchPosts()]);
  }

  async function generateDrafts(topic, angle, count = 3, customNotes = '') {
    loadingPosts.value = true;
    showToast('Consulting Ollama ghostwriter...', 'info');

    try {
      const payload = {
        topic: topic.trim(),
        angle: angle || 'Practical Insight',
        count: parseInt(count, 10) || 3,
        custom_notes: customNotes.trim() || undefined
      };

      const res = await api.generateDrafts(payload);
      if (res && res.drafts) {
        generatedDrafts.value = res.drafts;
        showToast(`Generated ${res.drafts.length} posts with ${res.model_used || 'Ollama'}!`, 'success');
      } else {
        throw new Error('No drafts returned by AI server.');
      }
    } catch (err) {
      showToast(err.message || 'Generation failed. Check if Ollama is running.', 'error');
    } finally {
      loadingPosts.value = false;
    }
  }

  async function deletePost(id) {
    if (!confirm('Are you sure you want to delete this post?')) return;
    try {
      await api.deletePost(id);
      showToast('Post deleted.', 'info');
      await fetchPosts();
    } catch (err) {
      showToast(err.message || 'Failed to delete post.', 'error');
    }
  }

  async function publishPostDirectly(id) {
    if (!confirm('Publish this post to LinkedIn now?')) return;
    showToast('Sending post to LinkedIn...', 'info');

    try {
      const res = await api.publishPostNow(id);
      showToast('Post published successfully to LinkedIn!', 'success');
      await fetchPosts();
    } catch (err) {
      showToast(err.message || 'Failed to publish post.', 'error');
      await fetchPosts();
    }
  }

  async function triggerSchedulerCheck() {
    isCheckingScheduler.value = true;
    showToast('Running scheduler check...', 'info');
    try {
      await api.checkScheduler();
      showToast('Scheduler checked successfully!', 'success');
      await fetchPosts();
    } catch (err) {
      showToast(err.message || 'Error checking scheduler.', 'error');
    } finally {
      isCheckingScheduler.value = false;
    }
  }

  // Schedule Modal Actions
  function openScheduleModalForDraft(idx) {
    const draft = generatedDrafts.value[idx];
    if (!draft) return;

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(8, 30, 0, 0);
    const pad = n => String(n).padStart(2, '0');
    const defaultTime = `${tomorrow.getFullYear()}-${pad(tomorrow.getMonth() + 1)}-${pad(tomorrow.getDate())}T${pad(tomorrow.getHours())}:${pad(tomorrow.getMinutes())}`;

    scheduleModal.postId = null;
    scheduleModal.draftIdx = idx;
    scheduleModal.topic = draft.angle ? `[${draft.angle}] Scheduled Post` : 'Scheduled LinkedIn Post';
    scheduleModal.content = draft.content;
    scheduleModal.imageUrl = draft.image_url || null;
    scheduleModal.dateTime = defaultTime;
    scheduleModal.isOpen = true;
  }

  function openScheduleModalForPost(post) {
    scheduleModal.postId = post.id;
    scheduleModal.draftIdx = null;
    scheduleModal.topic = post.topic || 'Scheduled Post';
    scheduleModal.content = post.content;
    scheduleModal.imageUrl = post.image_url || null;

    const initialTime = post.scheduled_at ? new Date(post.scheduled_at) : new Date();
    if (!post.scheduled_at) {
      initialTime.setDate(initialTime.getDate() + 1);
      initialTime.setHours(8, 30, 0, 0);
    }
    const pad = n => String(n).padStart(2, '0');
    scheduleModal.dateTime = `${initialTime.getFullYear()}-${pad(initialTime.getMonth() + 1)}-${pad(initialTime.getDate())}T${pad(initialTime.getHours())}:${pad(initialTime.getMinutes())}`;
    scheduleModal.isOpen = true;
  }

  function closeScheduleModal() {
    scheduleModal.isOpen = false;
  }

  // Refine Modal Actions
  function openRefineModal(idx) {
    const draft = generatedDrafts.value[idx];
    if (!draft) return;
    refineModal.draftIdx = idx;
    refineModal.content = draft.content;
    refineModal.isOpen = true;
  }

  function closeRefineModal() {
    refineModal.isOpen = false;
  }

  return {
    state,
    activeTab,
    isCheckingScheduler,
    loadingPosts,
    settings,
    generatedDrafts,
    posts,
    activeFilter,
    searchQuery,
    queueStats,
    scheduleModal,
    refineModal,
    toasts,
    showToast,
    removeToast,
    fetchSettings,
    fetchPosts,
    fetchHealthAndSettings,
    refreshAll,
    generateDrafts,
    deletePost,
    publishPostDirectly,
    triggerSchedulerCheck,
    openScheduleModalForDraft,
    openScheduleModalForPost,
    openScheduleModal: openScheduleModalForPost,
    closeScheduleModal,
    openRefineModal,
    closeRefineModal
  };
}
