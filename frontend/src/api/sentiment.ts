import client from './client';

export const sentimentApi = {
  analyze: (symbol: string, limit = 20) =>
    client.post<{ data: any[]; saved_count: number }>('/sentiment/analyze', {
      symbol,
      limit,
    }),

  getDailySummary: (symbol?: string) =>
    client.get<{ data: string }>('/sentiment/daily-summary', {
      params: { symbol },
    }),
};
