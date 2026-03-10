import client from './client';

export const chatApi = {
  ask: (question: string, system = '你是一个专业的A股投资助手。') =>
    client.post<{ data: string }>('/chat/ask', { question, system }),

  // SSE stream handled separately in component
};
