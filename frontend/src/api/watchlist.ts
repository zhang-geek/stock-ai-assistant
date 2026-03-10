import client from './client';
import type { WatchlistItem } from '../types';

export const watchlistApi = {
  list: () => client.get<{ data: WatchlistItem[] }>('/watchlist'),

  add: (data: {
    symbol: string;
    name?: string;
    sector?: string;
    notes?: string;
  }) => client.post<{ success: boolean }>('/watchlist', data),

  remove: (symbol: string) =>
    client.delete<{ success: boolean }>(`/watchlist/${symbol}`),
};
