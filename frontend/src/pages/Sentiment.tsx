import React, { useState } from 'react';
import { Card, Input, Button, Table, Space, message } from 'antd';
import { sentimentApi } from '../api/sentiment';

interface NewsItem {
  title: string;
  sentiment_label: string;
  sentiment_score: number;
  published_at?: string;
}

const Sentiment: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [symbol, setSymbol] = useState('');
  const [newsData, setNewsData] = useState<NewsItem[]>([]);
  const [summary, setSummary] = useState('');

  const handleAnalyze = async () => {
    if (!symbol.trim()) {
      message.warning('请输入股票代码');
      return;
    }
    setLoading(true);
    try {
      const res = await sentimentApi.analyze(symbol, 20);
      setNewsData(res.data.data || []);
      message.success(`已分析 ${res.data.saved_count} 条新闻`);
    } catch (error) {
      message.error('舆情分析失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDailySummary = async () => {
    setLoading(true);
    try {
      const res = await sentimentApi.getDailySummary(symbol || undefined);
      setSummary(res.data.data);
    } catch (error) {
      message.error('获取每日总结失败');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: '50%',
    },
    {
      title: '情感标签',
      dataIndex: 'sentiment_label',
      key: 'sentiment_label',
      width: '15%',
      render: (label: string) => {
        const color = label === 'positive' ? '#3f8600' : label === 'negative' ? '#cf1322' : '#666';
        return <span style={{ color }}>{label}</span>;
      },
    },
    {
      title: '情感分数',
      dataIndex: 'sentiment_score',
      key: 'sentiment_score',
      width: '15%',
      render: (score: number) => score?.toFixed(3) || '-',
    },
    {
      title: '发布时间',
      dataIndex: 'published_at',
      key: 'published_at',
      width: '20%',
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card title="舆情分析" bordered={false}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Space>
            <Input
              placeholder="输入股票代码（可选）"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              onPressEnter={handleAnalyze}
              style={{ width: 200 }}
            />
            <Button type="primary" onClick={handleAnalyze} loading={loading}>
              分析舆情
            </Button>
            <Button onClick={handleDailySummary} loading={loading}>
              每日总结
            </Button>
          </Space>

          {newsData.length > 0 && (
            <Table
              dataSource={newsData}
              columns={columns}
              rowKey={(record, idx) => `${record.title}-${idx}`}
              pagination={{ pageSize: 10 }}
              size="small"
              loading={loading}
            />
          )}

          {summary && (
            <Card title="每日舆情总结" style={{ whiteSpace: 'pre-wrap' }}>
              {summary}
            </Card>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default Sentiment;
