import client from './client';

export const financialApi = {
  analyze: (file: File, symbol = '', report_date = '') => {
    const formData = new FormData();
    formData.append('file', file);
    if (symbol) formData.append('symbol', symbol);
    if (report_date) formData.append('report_date', report_date);
    return client.post<{ data: string }>('/financial/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  compare: (symbols: string[]) =>
    client.post<{ data: string }>('/financial/compare', { symbols }),
};
