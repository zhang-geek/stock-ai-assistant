import { useState } from 'react';
import { Card, Button, Spin } from 'antd';
import { styleApi } from '../api/style';
import type { StyleData } from '../types';

export default function Style() {
  const [data, setData] = useState<StyleData | null>(null);
  const [coach, setCoach] = useState('');
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    setLoading(true);
    try {
      const res = await styleApi.analyze();
      setData(res.data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getCoach = async () => {
    setLoading(true);
    try {
      const res = await styleApi.coach();
      setCoach(res.data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card title="风格探索" style={{ marginBottom: 16 }}>
        <Button onClick={analyze}>分析风格</Button>
        <Button onClick={getCoach} style={{ marginLeft: 8 }}>
          AI教练
        </Button>
      </Card>

      {loading && <Spin />}

      {data && (
        <Card title="风格数据" style={{ marginBottom: 16 }}>
          <p>风格标签: {data.style_label}</p>
          <p>平均持仓天数: {data.avg_holding_days.toFixed(1)}</p>
          <p>交易频率: {data.trading_frequency.toFixed(1)} 次/月</p>
          <p>时间偏好: {data.time_pattern}</p>
        </Card>
      )}

      {coach && (
        <Card title="AI教练建议">
          <pre style={{ whiteSpace: 'pre-wrap' }}>{coach}</pre>
        </Card>
      )}
    </div>
  );
}
