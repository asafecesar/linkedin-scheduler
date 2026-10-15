/**
 * API Service for LinkedIn AI Scheduler
 */

async function request(url, options = {}) {
  const defaultHeaders = {};
  if (!(options.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers
    }
  });

  const contentType = (response.headers && typeof response.headers.get === 'function')
    ? (response.headers.get('content-type') || '')
    : '';
  const data = contentType.includes('application/json') ? await response.json() : await response.text();

  if (!response.ok) {
    const errorMsg = (typeof data === 'object' && data.detail) || (typeof data === 'object' && data.message) || data || 'Request failed';
    throw new Error(errorMsg);
  }

  return data;
}

export const api = {
  // System & Health
  getHealth: () => request('/api/health'),
  getOllamaStatus: () => request('/api/ollama/status'),
  checkScheduler: () => request('/api/scheduler/check', { method: 'POST' }),

  // Settings
  getSettings: () => request('/api/settings'),
  updateSettings: (payload) => request('/api/settings', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  verifyLinkedIn: (token) => request('/api/linkedin/verify', {
    method: 'POST',
    body: JSON.stringify({ token })
  }),

  // AI Studio Generation
  generateBatch: ({ topic, count, angle, custom_notes, provider = 'ollama' }) => request('/api/generate/batch', {
    method: 'POST',
    body: JSON.stringify({
      topic,
      count,
      angle,
      custom_notes,
      provider
    })
  }),
  refinePost: ({ content, instruction, provider = 'ollama' }) => request('/api/generate/refine', {
    method: 'POST',
    body: JSON.stringify({
      content,
      instruction,
      provider
    })
  }),

  // Posts & Scheduling
  getPosts: () => request('/api/posts'),
  getPost: (id) => request(`/api/posts/${id}`),
  createPost: (postData) => request('/api/posts', {
    method: 'POST',
    body: JSON.stringify(postData)
  }),
  updatePost: (id, updates) => request(`/api/posts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(updates)
  }),
  deletePost: (id) => request(`/api/posts/${id}`, {
    method: 'DELETE'
  }),
  publishPostNow: (id) => request(`/api/posts/${id}/publish-now`, {
    method: 'POST'
  }),

  // Image Upload
  uploadImage: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request('/api/posts/upload-image', {
      method: 'POST',
      body: formData
    });
  }
};
