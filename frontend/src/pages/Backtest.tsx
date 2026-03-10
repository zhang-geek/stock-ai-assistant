import { useState } from 'react';
import { Card, Upload, Button, message, Spin } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { backtestApi } from '../api/backtest';
import type { TradeStats } from '../types';

export default function Backtest() {
  const [stats, setStats] = useState<TradeStats | null>(null);
  const [analysis, setAnalysis] = useState('');
  const [loading, setLoading] = useState(false);

  const handleUpload = async (file: File) => {
    setLoading(true);
    try {
      const res = await backtestApi.importCsv(file);
      message.success(`导入 ${res.data.imported} 条记录`);
      loadStats();
    } catch (err) {
      message.error('导入失败');
    } finally {
      setLoading(false);
    }
    return false;
  };

  const loadStats = async () => {
    setLoading(true);
    try {
      const res = await backtestApi.getStatistics();
      setStats(res.data.data);
    } catch (err) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const loadAnalysis = async () => {
    setLoading(true);
    try {
      const res = await backtestApi.getAiAnalysis();
      setAnalysis(res.data.data);
    } catch (err) {
      message.error('分析失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card title="交易回测" style={{ marginBottom: 16 }}>
        <Upload beforeUpload={handleUpload} accept=".csv">
          <Button icon={<UploadOutlined />}>上传CSV</Button>
        </Upload>
        <Button onClick={loadStats} style={{ marginLeft: 8 }}>
          加载统计
        </Button>
        <Button onClick={loadAnalysis} style={{ marginLeft: 8 }}>
          AI分析
        </Button>
      </Card>

      {loading && <Spin />}

      {stats && (
        <Card title="统计数据" style={{ marginBottom: 16 }}>
          <p>总交易: {stats.total_trades}</p>
          <p>胜率: {(stats.win_rate * 100).toFixed(2)}%</p>
          <p>平均收益: {(stats.avg_profit * 100).toFixed(2)}%</p>
          <p>盈亏比: {stats.profit_loss_ratio.toFixed(2)}</p>
        </Card>
      )}

      {analysis && (
        <Card title="AI分析">
          <pre style={{ whiteSpace: 'pre-wrap' }}>{analysis}</pre>
        </Card>
      )}
    </div>
  );
}
