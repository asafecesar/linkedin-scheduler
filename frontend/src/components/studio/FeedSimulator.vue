<template>
  <div class="linkedin-sim-card">
    <!-- Top Bar -->
    <div class="sim-top-bar">
      <span class="sim-angle-tag">📌 Option #{{ index + 1 }} — {{ draft.angle || 'Practical Insight' }}</span>
      <span class="sim-read-time">Read time: {{ draft.estimated_read_time || '1 min' }}</span>
    </div>

    <!-- Author Header -->
    <div class="sim-card-header">
      <img 
        :src="settings.user_avatar_url || defaultAvatar" 
        alt="Avatar" 
        class="sim-avatar"
        @error="$event.target.src = defaultAvatar"
      />
      <div class="sim-author-meta">
        <div class="sim-author-name-row">
          <span class="sim-author-name">{{ settings.user_name || 'Your Name' }}</span>
          <span class="sim-degree-badge">• 1st</span>
        </div>
        <div class="sim-author-headline">{{ settings.user_headline || 'LinkedIn Professional' }}</div>
        <div class="sim-post-time">
          <span>Just now</span>
          <span>•</span>
          <svg class="sim-globe-icon" viewBox="0 0 16 16" width="12" height="12" fill="currentColor">
            <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm0 14.5a6.5 6.5 0 0 1-5.6-3.2A7.1 7.1 0 0 1 8 9.5a7.1 7.1 0 0 1 5.6 1.8A6.5 6.5 0 0 1 8 14.5zm0-6A5.5 5.5 0 0 0 2.6 10a6.5 6.5 0 1 1 10.8 0A5.5 5.5 0 0 0 8 8.5z"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Post Body -->
    <div class="sim-card-body">
      <!-- Normal Text Mode -->
      <div v-if="!isEditing" class="sim-post-text" :class="{ folded: isFolded }">
        {{ draft.content }}
      </div>

      <!-- Inline Edit Mode -->
      <div v-else class="sim-edit-box">
        <textarea v-model="editContent" class="sim-edit-textarea"></textarea>
        <div class="sim-edit-actions">
          <button type="button" class="btn-ghost btn-sm" @click="cancelInlineEdit">Cancel</button>
          <button type="button" class="btn-primary btn-sm" @click="saveInlineEdit">Save Edit</button>
        </div>
      </div>

      <!-- Fold Button -->
      <button v-if="!isEditing" class="sim-see-more-btn" @click="isFolded = !isFolded">
        {{ isFolded ? '...see more' : '...see less' }}
      </button>

      <!-- Suggested Hashtags Box -->
      <div class="sim-hashtags-box">
        <div class="hashtags-header-row">
          <span class="hashtags-title">🏷️ Suggested Hashtags</span>
          <span class="hashtags-counter">{{ (draft.hashtags || []).length }} tags</span>
        </div>
        <div class="hashtags-chips-wrap">
          <span v-for="tag in (draft.hashtags || [])" :key="tag" class="hashtag-pill">
            <span>{{ tag }}</span>
            <button type="button" class="btn-remove-tag" title="Remove hashtag" @click="removeTag(tag)">×</button>
          </span>

          <div class="add-tag-form">
            <input 
              type="text" 
              v-model="newTagInput" 
              class="input-tag-inline" 
              placeholder="+ tag..." 
              @keydown.enter.prevent="addTag"
            />
            <button type="button" class="btn-tag-add" title="Add hashtag" @click="addTag">+</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Attached Image Preview -->
    <div v-if="draft.image_url" class="sim-media-preview-box">
      <img :src="draft.image_url" alt="Post Image" class="sim-post-image" />
      <button type="button" class="btn-remove-media" title="Remove image from this post" @click="removeImage">
        <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
        <span>Remove Image</span>
      </button>
    </div>

    <!-- Social Stats Simulation -->
    <div class="sim-engagement-stats">
      <div class="sim-reactions-group">
        <span class="reaction-bubble like">👍</span>
        <span class="reaction-bubble heart">❤️</span>
        <span class="reaction-bubble insight">💡</span>
        <span>42</span>
      </div>
      <div class="sim-comments-count">
        <span>12 comments</span>
      </div>
    </div>

    <!-- Social Action Bar -->
    <div class="sim-actions-bar">
      <button class="sim-action-btn">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
        </svg>
        <span>Like</span>
      </button>
      <button class="sim-action-btn">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        <span>Comment</span>
      </button>
      <button class="sim-action-btn">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="17 1 21 5 17 9"></polyline>
          <path d="M3 11V9a4 4 0 0 1 4-4h14"></path>
          <polyline points="7 23 3 19 7 15"></polyline>
          <path d="M21 13v2a4 4 0 0 1-4 4H3"></path>
        </svg>
        <span>Share</span>
      </button>
    </div>

    <!-- Pilot Actions Toolbar -->
    <div class="sim-pilot-toolbar">
      <div class="pilot-left-actions">
        <button class="btn-ghost btn-sm" @click="toggleInlineEdit">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
          </svg>
          <span>Edit</span>
        </button>

        <button class="btn-ghost btn-sm" title="Attach image from your computer" @click="triggerFileInput">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
          </svg>
          <span>{{ draft.image_url ? 'Change Image' : 'Attach Image' }}</span>
        </button>

        <button class="btn-ghost btn-sm" title="Paste external image link" @click="promptImageLink">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
          </svg>
          <span>Link</span>
        </button>

        <button class="btn-ghost btn-sm" @click="openRefineModal(index)">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
          </svg>
          <span>Refine</span>
        </button>

        <button class="btn-ghost btn-sm" @click="copyContent">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
          <span>Copy</span>
        </button>
      </div>

      <div class="pilot-right-actions">
        <button class="btn-secondary btn-sm" :disabled="isSaving" @click="saveDraft">
          <span>Save Draft</span>
        </button>

        <button class="btn-secondary btn-sm" @click="openScheduleModalForDraft(index)">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
          <span>Schedule</span>
        </button>

        <button class="btn-primary btn-sm" :disabled="isPublishing" @click="publishImmediately">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
          <span>Publish Now</span>
        </button>
      </div>
    </div>

    <!-- Hidden native file input for this card -->
    <input 
      type="file" 
      ref="fileInputRef" 
      accept="image/png, image/jpeg, image/webp, image/gif" 
      style="display: none;" 
      @change="handleFileChange"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useApp } from '@/composables/useApp';
import { api } from '@/services/api';

const props = defineProps({
  draft: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  }
});

const defaultAvatar = 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80';
const { settings, showToast, openScheduleModalForDraft, openRefineModal, fetchPosts } = useApp();

const isFolded = ref(true);
const isEditing = ref(false);
const editContent = ref('');
const newTagInput = ref('');
const isSaving = ref(false);
const isPublishing = ref(false);
const fileInputRef = ref(null);

function toggleInlineEdit() {
  if (isEditing.value) {
    cancelInlineEdit();
  } else {
    editContent.value = props.draft.content;
    isEditing.value = true;
  }
}

function cancelInlineEdit() {
  isEditing.value = false;
  editContent.value = '';
}

function saveInlineEdit() {
  props.draft.content = editContent.value.trim();
  const foundTags = props.draft.content.match(/#[a-zA-Z0-9_]+/g) || [];
  props.draft.hashtags = [...new Set(foundTags)];
  isEditing.value = false;
  showToast('Changes saved to draft!', 'success');
}

function addTag() {
  let raw = newTagInput.value.trim().replace(/^#+/, '').replace(/[^a-zA-Z0-9_]/g, '');
  if (!raw) return;

  const formatted = `#${raw}`;
  if (!props.draft.hashtags) props.draft.hashtags = [];

  if (!props.draft.hashtags.some(t => t.toLowerCase() === formatted.toLowerCase())) {
    props.draft.hashtags.push(formatted);
    if (!props.draft.content.toLowerCase().includes(formatted.toLowerCase())) {
      props.draft.content = `${props.draft.content.trimEnd()}\n\n${formatted}`;
    }
    showToast(`Tag ${formatted} added to post!`, 'success');
  }
  newTagInput.value = '';
}

function removeTag(tag) {
  props.draft.hashtags = (props.draft.hashtags || []).filter(t => t.toLowerCase() !== tag.toLowerCase());
  const escaped = tag.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(^|\\s)${escaped}\\b`, 'gi');
  props.draft.content = props.draft.content.replace(regex, '').replace(/\n{3,}/g, '\n\n').trimEnd();
  showToast(`Tag ${tag} removed!`, 'info');
}

function triggerFileInput() {
  fileInputRef.value?.click();
}

async function handleFileChange(e) {
  const file = e.target.files?.[0];
  if (!file) return;

  showToast('Uploading image...', 'info');
  try {
    const res = await api.uploadImage(file);
    props.draft.image_url = res.url;
    showToast('Image attached successfully!', 'success');
  } catch (err) {
    showToast(`Error uploading image: ${err.message}`, 'error');
  } finally {
    if (fileInputRef.value) fileInputRef.value.value = '';
  }
}

function promptImageLink() {
  const url = prompt('Paste the image URL:\n(e.g. https://images.unsplash.com/...)', props.draft.image_url || '');
  if (url !== null) {
    const trimmed = url.trim();
    props.draft.image_url = trimmed || null;
    if (trimmed) showToast('Image linked successfully!', 'success');
  }
}

function removeImage() {
  props.draft.image_url = null;
  showToast('Image removed from post.', 'info');
}

function copyContent() {
  navigator.clipboard.writeText(props.draft.content)
    .then(() => showToast('Text copied to clipboard!', 'success'))
    .catch(() => showToast('Failed to copy text.', 'error'));
}

async function saveDraft() {
  isSaving.value = true;
  try {
    await api.createPost({
      topic: props.draft.angle ? `[${props.draft.angle}] Generated Post` : 'Post Draft',
      content: props.draft.content,
      status: 'draft',
      image_url: props.draft.image_url || null
    });
    showToast('Draft saved to queue successfully!', 'success');
    await fetchPosts();
  } catch (err) {
    showToast(err.message || 'Error saving draft.', 'error');
  } finally {
    isSaving.value = false;
  }
}

async function publishImmediately() {
  if (!confirm('Publish this post immediately to LinkedIn?')) return;

  isPublishing.value = true;
  showToast('Publishing post to LinkedIn...', 'info');

  try {
    const created = await api.createPost({
      topic: props.draft.angle ? `[${props.draft.angle}] Immediate publish` : 'LinkedIn Post',
      content: props.draft.content,
      status: 'draft',
      image_url: props.draft.image_url || null
    });

    await api.publishPostNow(created.id);
    showToast('🎉 Post published successfully to LinkedIn!', 'success');
    await fetchPosts();
  } catch (err) {
    showToast(`Publishing error: ${err.message}`, 'error');
  } finally {
    isPublishing.value = false;
  }
}
</script>
