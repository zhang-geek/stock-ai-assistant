import client from './client';
import type { Quote, DailyBar, IndexQuote, Sector } from '../types';

export const quoteApi = {
  getRealtime: (symbols: string[]) =>
    client.get<{ data: Quote[] }>('/quote/realtime', {
      params: { symbols: symbols.join(',') },
    }),

  getDaily: (symbol: string, start = '', end = '', adjust = 'qfq') =>
    client.get<{ data: DailyBar[] }>(`/quote/daily/${symbol}`, {
      params: { start, end, adjust },
    }),

  getIndex: () => client.get<{ data: IndexQuote[] }>('/quote/index'),

  getSectors: (n = 20) =>
    client.get<{ data: Sector[] }>('/quote/sectors', { params: { n } }),

  getTopGainers: (n = 20) =>
    client.get<{ data: Quote[] }>('/quote/top/gainers', { params: { n } }),

  getTopLosers: (n = 20) =>
    client.get<{ data: Quote[] }>('/quote/top/losers', { params: { n } }),

  getNews: (symbol = '') =>
    client.get<{ data: any[] }>('/quote/news', { params: { symbol } }),

  getInfo: (symbol: string) =>
    client.get<{ data: Record<string, any> }>(`/quote/info/${symbol}`),
};
