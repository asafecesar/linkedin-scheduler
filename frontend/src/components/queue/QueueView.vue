<script setup>
import { ref, computed } from 'vue';
import { useApp } from '@/composables/useApp';

const {
  state,
  queueStats,
  deletePost,
  publishPostDirectly,
  openScheduleModal,
  showToast
} = useApp();

const activeFilter = ref('all');
const searchQuery = ref('');

const filterTabs = [
  { id: 'all', label: 'All' },
  { id: 'scheduled', label: 'Scheduled' },
  { id: 'draft', label: 'Drafts' },
  { id: 'published', label: 'Published' },
  { id: 'failed', label: 'Failed' }
];

const filteredPosts = computed(() => {
  let list = state.posts || [];

  if (activeFilter.value !== 'all') {
    list = list.filter(p => p.status === activeFilter.value);
  }

  const query = searchQuery.value.trim().toLowerCase();
  if (query) {
    list = list.filter(p =>
      (p.topic && p.topic.toLowerCase().includes(query)) ||
      (p.content && p.content.toLowerCase().includes(query))
    );
  }

  return list;
});

function getStatusBadge(status) {
  const map = {
    scheduled: { label: 'Scheduled', class: 'scheduled' },
    published: { label: 'Published', class: 'published' },
    draft: { label: 'Draft', class: 'draft' },
    failed: { label: 'Failed', class: 'failed' }
  };
  return map[status] || { label: status, class: 'draft' };
}

function formatDate(post) {
  const ts = post.scheduled_at || post.published_at || post.created_at;
  if (!ts) return 'Not scheduled';
  try {
    return new Date(ts).toLocaleString('en-US', { dateStyle: 'short', timeStyle: 'short' });
  } catch {
    return ts;
  }
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast('Post content copied to clipboard!', 'success');
  } catch {
    showToast('Failed to copy text.', 'error');
  }
}

function handleReschedule(post) {
  openScheduleModal({
    id: post.id,
    topic: post.topic,
    content: post.content,
    image_url: post.image_url,
    scheduled_at: post.scheduled_at
  });
}
</script>

<template>
  <section class="tab-panel active" id="tabQueue">
    <!-- Stat cards -->
    <div class="queue-overview-grid">
      <div class="stat-card glass-card">
        <div class="stat-icon scheduled">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-label">In Schedule Queue</span>
          <span class="stat-value" id="statScheduled">{{ queueStats.scheduled }}</span>
        </div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon published">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-label">Successfully Published</span>
          <span class="stat-value" id="statPublished">{{ queueStats.published }}</span>
        </div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon draft">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 20h9"></path>
            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-label">Saved Drafts</span>
          <span class="stat-value" id="statDrafts">{{ queueStats.drafts }}</span>
        </div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon total">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-label">Total Created</span>
          <span class="stat-value" id="statTotal">{{ queueStats.total }}</span>
        </div>
      </div>
    </div>

    <!-- Filter bar -->
    <div class="filter-bar glass-card">
      <div class="filter-tabs" id="queueFilterTabs">
        <button
          v-for="tab in filterTabs"
          :key="tab.id"
          type="button"
          class="filter-tab-btn"
          :class="{ active: activeFilter === tab.id }"
          @click="activeFilter = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="queue-search">
        <input
          type="text"
          v-model="searchQuery"
          id="queueSearchInput"
          class="search-input"
          placeholder="Filter by keyword..."
        />
      </div>
    </div>

    <!-- Posts List -->
    <div class="posts-list-container" id="postsListContainer">
      <div v-if="filteredPosts.length === 0" class="empty-state-card glass-card">
        <h3>No posts found</h3>
        <p>No posts match this category. Create a new post in the AI Studio to schedule.</p>
      </div>

      <div
        v-for="post in filteredPosts"
        :key="post.id"
        class="queue-item-card"
        :id="`postCard_${post.id}`"
      >
        <div class="queue-item-header">
          <span class="queue-topic-title">{{ post.topic || 'Untitled Post' }}</span>
          <span class="status-badge" :class="getStatusBadge(post.status).class">
            ● {{ getStatusBadge(post.status).label }}
          </span>
        </div>

        <div class="queue-item-body">{{ post.content }}</div>

        <div v-if="post.image_url" class="queue-item-media">
          <img :src="post.image_url" alt="Post Media" class="queue-thumb-img" />
          <span class="queue-media-badge">📷 Image attached</span>
        </div>

        <div v-if="post.error_message" class="queue-error-alert" style="color: var(--rose-danger); font-size: 0.8rem; margin-bottom: 0.75rem;">
          ⚠️ Error: {{ post.error_message }}
        </div>

        <div class="queue-item-footer">
          <div class="queue-time-info">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            <span>
              {{
                post.status === 'scheduled'
                  ? `Scheduled for: ${formatDate(post)}`
                  : (post.status === 'published' ? `Published on: ${formatDate(post)}` : `Created: ${formatDate(post)}`)
              }}
            </span>
          </div>

          <div class="queue-actions-group">
            <button class="btn-ghost btn-sm" @click="copyText(post.content)">Copy</button>
            <button class="btn-ghost btn-sm" @click="handleReschedule(post)">Reschedule</button>
            <button
              v-if="post.status !== 'published'"
              class="btn-primary btn-sm"
              @click="publishPostDirectly(post.id)"
            >
              Publish Now
            </button>
            <button
              class="btn-ghost btn-sm"
              style="color: var(--rose-danger)"
              @click="deletePost(post.id)"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
