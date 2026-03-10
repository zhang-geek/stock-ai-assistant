import client from './client';
import type { StyleData } from '../types';

export const styleApi = {
  analyze: () => client.get<{ data: StyleData }>('/style/analyze'),

  coach: (question = '') =>
    client.post<{ data: string }>('/style/coach', { question }),
};
