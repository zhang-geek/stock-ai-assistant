import { useState } from 'react';
import { Input, Button, Card, Spin, Row, Col, Statistic, message } from 'antd';
import { SearchOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { quoteApi } from '../api/quote';
import type { Quote as QuoteType, DailyBar } from '../types';

export default function Quote() {
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [quote, setQuote] = useState<QuoteType | null>(null);
  const [dailyData, setDailyData] = useState<DailyBar[]>([]);

  const handleSearch = async () => {
    if (!symbol.trim()) return message.warning('请输入股票代码');
    setLoading(true);
    try {
      const [quoteRes, dailyRes] = await Promise.all([
        quoteApi.getRealtime([symbol]),
        quoteApi.getDaily(symbol),
      ]);
      if (quoteRes.data.data?.length > 0) {
        setQuote(quoteRes.data.data[0]);
      } else {
        message.error('未找到该股票');
        setQuote(null);
      }
      if (dailyRes.data.data) setDailyData(dailyRes.data.data);
    } catch (error) {
      message.error('获取行情失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card>
        <Input.Search
          placeholder="输入股票代码（如：000001）"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          onSearch={handleSearch}
          enterButton={<Button type="primary" icon={<SearchOutlined />}>查询</Button>}
          size="large"
          loading={loading}
        />
      </Card>

      {loading && <div style={{ textAlign: 'center', padding: '40px' }}><Spin size="large" /></div>}

      {!loading && quote && (
        <>
          <Card title={`${quote.name} (${quote.symbol})`} style={{ marginTop: 16 }}>
            <Row gutter={16}>
              <Col span={6}>
                <Statistic
                  title="最新价"
                  value={quote.price}
                  precision={2}
                  valueStyle={{ color: quote.change_pct >= 0 ? '#cf1322' : '#3f8600' }}
                  prefix={quote.change_pct >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                  suffix={`(${quote.change_pct >= 0 ? '+' : ''}${quote.change_pct.toFixed(2)}%)`}
                />
              </Col>
              <Col span={6}>
                <Statistic title="开盘" value={quote.open} precision={2} />
              </Col>
              <Col span={6}>
                <Statistic title="最高" value={quote.high} precision={2} />
              </Col>
              <Col span={6}>
                <Statistic title="最低" value={quote.low} precision={2} />
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={6}>
                <Statistic title="昨收" value={quote.prev_close} precision={2} />
              </Col>
              <Col span={6}>
                <Statistic title="成交量" value={quote.volume} suffix="手" />
              </Col>
              <Col span={6}>
                <Statistic title="成交额" value={(quote.amount / 100000000).toFixed(2)} suffix="亿" />
              </Col>
              <Col span={6}>
                {quote.turnover !== undefined && (
                  <Statistic title="换手率" value={quote.turnover} precision={2} suffix="%" />
                )}
              </Col>
            </Row>
          </Card>

          <Card title="日K线图" style={{ marginTop: 16 }}>
            <div style={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f5f5f5' }}>
              {/* TODO: Add ECharts candlestick chart */}
              <p style={{ color: '#999' }}>K线图占位（共 {dailyData.length} 条数据）</p>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
