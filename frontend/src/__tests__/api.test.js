import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api } from '../services/api';

describe('api service client', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('calls getHealth with correct endpoint', async () => {
    const mockHealth = { status: 'ok', ollama_online: true };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => mockHealth
    });

    const data = await api.getHealth();
    expect(global.fetch).toHaveBeenCalledWith('/api/health', expect.anything());
    expect(data).toEqual(mockHealth);
  });

  it('calls createPost with POST method and stringified JSON', async () => {
    const mockPost = { id: 1, topic: 'AI Trends', content: 'Discussion on local models' };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => mockPost
    });

    const res = await api.createPost({ topic: 'AI Trends', content: 'Discussion on local models' });
    expect(global.fetch).toHaveBeenCalledWith('/api/posts', expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: 'AI Trends', content: 'Discussion on local models' })
    }));
    expect(res).toEqual(mockPost);
  });

  it('throws an error with detail message on non-ok response', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      headers: { get: () => 'application/json' },
      json: async () => ({ detail: 'Custom error detail' })
    });

    await expect(api.getPosts()).rejects.toThrow('Custom error detail');
  });
});
