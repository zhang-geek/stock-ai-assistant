import client from './client';
import type { CostSummary } from '../types';

export const costApi = {
  getSummary: (days = 30) =>
    client.get<{ data: CostSummary }>('/cost/summary', { params: { days } }),
};
