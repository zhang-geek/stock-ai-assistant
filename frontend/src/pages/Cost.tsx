import { useState, useEffect } from 'react';
import { Card, Select, Spin } from 'antd';
import { costApi } from '../api/cost';
import type { CostSummary } from '../types';

export default function Cost() {
  const [data, setData] = useState<CostSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [days, setDays] = useState(30);

  useEffect(() => {
    loadData();
  }, [days]);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await costApi.getSummary(days);
      setData(res.data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card
        title="费用统计"
        extra={
          <Select value={days} onChange={setDays} style={{ width: 120 }}>
            <Select.Option value={7}>最近7天</Select.Option>
            <Select.Option value={30}>最近30天</Select.Option>
            <Select.Option value={90}>最近90天</Select.Option>
          </Select>
        }
      >
        {loading && <Spin />}
        {data && (
          <div>
            <h3>总费用: ${data.total_cost_usd.toFixed(4)}</h3>
            <h3>总调用: {data.total_calls} 次</h3>

            <h4>按Provider</h4>
            {Object.entries(data.by_provider).map(([name, info]) => (
              <p key={name}>
                {name}: {info.calls} 次, ${info.cost.toFixed(4)}
              </p>
            ))}

            <h4>按任务类型</h4>
            {Object.entries(data.by_task).map(([name, info]) => (
              <p key={name}>
                {name}: {info.calls} 次, ${info.cost.toFixed(4)}
              </p>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
