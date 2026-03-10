import client from './client';

export const marketApi = {
  getMorningBrief: () => client.get<{ data: string }>('/market/morning-brief'),
  getEveningReview: () => client.get<{ data: string }>('/market/evening-review'),
  getSignals: (threshold = 5.0) =>
    client.get<{ data: any[] }>('/market/signals', { params: { threshold } }),
};
