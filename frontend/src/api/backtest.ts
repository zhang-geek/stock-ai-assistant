import client from './client';
import type { TradeStats } from '../types';

export const backtestApi = {
  getStatistics: () => client.get<{ data: TradeStats }>('/backtest/statistics'),

  getAiAnalysis: () => client.get<{ data: string }>('/backtest/ai-analysis'),

  importCsv: (file: File, broker = 'generic') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('broker', broker);
    return client.post<{ imported: number }>('/backtest/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};
