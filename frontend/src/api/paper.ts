import client from './client';
import type { Portfolio, Transaction } from '../types';

export const paperApi = {
  getPortfolio: () => client.get<{ data: Portfolio }>('/paper/portfolio'),

  buy: (data: {
    symbol: string;
    price: number;
    quantity: number;
    reasoning?: string;
    strategy?: string;
  }) => client.post<{ success: boolean }>('/paper/buy', data),

  sell: (data: {
    symbol: string;
    price: number;
    quantity: number;
    reasoning?: string;
    strategy?: string;
  }) => client.post<{ success: boolean }>('/paper/sell', data),

  getHistory: (n = 20) =>
    client.get<{ data: Transaction[] }>('/paper/history', { params: { n } }),

  getAiDecision: (symbol: string) =>
    client.get<{ data: any }>(`/paper/decision/${symbol}`),
};
