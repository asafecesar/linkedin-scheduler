import { describe, it, expect, beforeEach } from 'vitest';
import { useApp } from '../composables/useApp';

describe('useApp composable', () => {
  let app;

  beforeEach(() => {
    app = useApp();
    app.posts.value = [];
    app.toasts.value = [];
    app.activeTab.value = 'studio';
  });

  it('initializes with default active tab and empty lists', () => {
    expect(app.activeTab.value).toBe('studio');
    expect(app.posts.value).toEqual([]);
    expect(app.toasts.value).toEqual([]);
  });

  it('computes queueStats accurately based on posts array', () => {
    app.posts.value = [
      { id: 1, status: 'scheduled' },
      { id: 2, status: 'scheduled' },
      { id: 3, status: 'published' },
      { id: 4, status: 'draft' },
      { id: 5, status: 'failed' }
    ];

    expect(app.queueStats.value.total).toBe(5);
    expect(app.queueStats.value.scheduled).toBe(2);
    expect(app.queueStats.value.published).toBe(1);
    expect(app.queueStats.value.drafts).toBe(1);
  });

  it('manages toast notifications', () => {
    app.showToast('Test notification', 'success');
    expect(app.toasts.value.length).toBe(1);
    expect(app.toasts.value[0].message).toBe('Test notification');
    expect(app.toasts.value[0].type).toBe('success');

    const toastId = app.toasts.value[0].id;
    app.removeToast(toastId);
    expect(app.toasts.value.length).toBe(0);
  });

  it('controls schedule modal open and close states', () => {
    const post = {
      id: 10,
      topic: 'My Topic',
      content: 'Post Content',
      image_url: null,
      scheduled_at: '2026-11-01T10:00:00'
    };

    app.openScheduleModalForPost(post);
    expect(app.scheduleModal.isOpen).toBe(true);
    expect(app.scheduleModal.postId).toBe(10);
    expect(app.scheduleModal.topic).toBe('My Topic');
    expect(app.scheduleModal.content).toBe('Post Content');

    app.closeScheduleModal();
    expect(app.scheduleModal.isOpen).toBe(false);
  });

  it('controls refine modal open and close states', () => {
    app.generatedDrafts.value = [
      { content: 'Draft to refine' }
    ];

    app.openRefineModal(0);
    expect(app.refineModal.isOpen).toBe(true);
    expect(app.refineModal.draftIdx).toBe(0);
    expect(app.refineModal.content).toBe('Draft to refine');

    app.closeRefineModal();
    expect(app.refineModal.isOpen).toBe(false);
  });
});
