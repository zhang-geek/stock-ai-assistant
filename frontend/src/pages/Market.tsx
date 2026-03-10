import React, { useState } from 'react';
import { Card, Tabs, Button, Spin, message, InputNumber } from 'antd';
import { marketApi } from '../api/market';

const Market: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [morningBrief, setMorningBrief] = useState('');
  const [eveningReview, setEveningReview] = useState('');
  const [signals, setSignals] = useState<any[]>([]);
  const [threshold, setThreshold] = useState(5.0);

  const fetchMorningBrief = async () => {
    setLoading(true);
    try {
      const res = await marketApi.getMorningBrief();
      setMorningBrief(res.data.data);
    } catch (error) {
      message.error('获取盘前简报失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchEveningReview = async () => {
    setLoading(true);
    try {
      const res = await marketApi.getEveningReview();
      setEveningReview(res.data.data);
    } catch (error) {
      message.error('获取盘后复盘失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchSignals = async () => {
    setLoading(true);
    try {
      const res = await marketApi.getSignals(threshold);
      setSignals(res.data.data);
    } catch (error) {
      message.error('获取异动信号失败');
    } finally {
      setLoading(false);
    }
  };

  const items = [
    {
      key: 'morning',
      label: '盘前简报',
      children: (
        <div>
          <Button type="primary" onClick={fetchMorningBrief} loading={loading}>
            生成盘前简报
          </Button>
          {morningBrief && (
            <Card style={{ marginTop: 16, whiteSpace: 'pre-wrap' }}>
              {morningBrief}
            </Card>
          )}
        </div>
      ),
    },
    {
      key: 'evening',
      label: '盘后复盘',
      children: (
        <div>
          <Button type="primary" onClick={fetchEveningReview} loading={loading}>
            生成盘后复盘
          </Button>
          {eveningReview && (
            <Card style={{ marginTop: 16, whiteSpace: 'pre-wrap' }}>
              {eveningReview}
            </Card>
          )}
        </div>
      ),
    },
    {
      key: 'signals',
      label: '异动扫描',
      children: (
        <div>
          <div style={{ marginBottom: 16 }}>
            <span style={{ marginRight: 8 }}>涨跌幅阈值:</span>
            <InputNumber
              min={1}
              max={20}
              step={0.5}
              value={threshold}
              onChange={(val) => setThreshold(val || 5.0)}
              style={{ width: 120 }}
            />
            <span style={{ marginLeft: 8 }}>%</span>
            <Button
              type="primary"
              onClick={fetchSignals}
              loading={loading}
              style={{ marginLeft: 16 }}
            >
              扫描异动
            </Button>
          </div>
          {signals.length > 0 && (
            <Card>
              {signals.map((signal, idx) => (
                <div key={idx} style={{ marginBottom: 8 }}>
                  {signal.symbol} {signal.name} - {signal.change_pct?.toFixed(2)}%
                </div>
              ))}
            </Card>
          )}
        </div>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card title="市场监控" bordered={false}>
        <Spin spinning={loading}>
          <Tabs items={items} />
        </Spin>
      </Card>
    </div>
  );
};

export default Market;
