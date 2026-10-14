<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="brand-logo">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
            <rect x="2" y="9" width="4" height="12"></rect>
            <circle cx="4" cy="4" r="2"></circle>
          </svg>
        </div>
        <div class="brand-text">
          <span class="brand-title">InPost</span>
          <span class="brand-badge">AI Studio</span>
        </div>
      </div>
    </div>

    <nav class="nav-menu">
      <button 
        class="nav-item" 
        :class="{ active: activeTab === 'studio' }"
        @click="activeTab = 'studio'"
      >
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3z"></path>
        </svg>
        <span>Creation Studio</span>
      </button>

      <button 
        class="nav-item" 
        :class="{ active: activeTab === 'queue' }"
        @click="activeTab = 'queue'"
      >
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        <span>Queue & Scheduled</span>
        <span class="nav-pill">{{ queueStats.scheduled }}</span>
      </button>

      <button 
        class="nav-item" 
        :class="{ active: activeTab === 'settings' }"
        @click="activeTab = 'settings'"
      >
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
        <span>Settings</span>
      </button>
    </nav>

    <!-- User Profile Card in Sidebar -->
    <div class="sidebar-user-card" @click="activeTab = 'settings'" style="cursor: pointer;">
      <div class="user-avatar-wrap">
        <img 
          :src="settings.user_avatar_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80'" 
          alt="Avatar" 
          class="user-avatar"
          @error="handleAvatarError"
        />
        <span class="user-status-dot online"></span>
      </div>
      <div class="user-info">
        <span class="user-name">{{ settings.user_name || 'Your Name' }}</span>
        <span class="user-headline">{{ settings.user_headline || 'Configure Profile' }}</span>
      </div>
    </div>

    <!-- Status Box -->
    <div class="sidebar-status-box">
      <div class="status-indicator-item">
        <span class="pulse-dot" :class="{ online: settings.ollama_online }"></span>
        <span class="status-label">
          {{ settings.ollama_online ? `Ollama (${settings.ollama_model})` : 'Ollama Local' }}
        </span>
      </div>
      <div class="status-indicator-item">
        <span class="pulse-dot" :class="{ online: settings.has_linkedin_token || settings.linkedin_configured }"></span>
        <span class="status-label">
          {{ (settings.has_linkedin_token || settings.linkedin_configured) ? 'LinkedIn Connected' : 'LinkedIn API' }}
        </span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useApp } from '@/composables/useApp';

const { activeTab, settings, queueStats } = useApp();

function handleAvatarError(e) {
  e.target.src = 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80';
}
</script>
