import { useState } from 'react';
import { Input, Button, Card, Spin, Row, Col, Statistic, message, Space, Divider } from 'antd';
import { SearchOutlined, ArrowUpOutlined, ArrowDownOutlined, LineChartOutlined } from '@ant-design/icons';
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
      <Card
        style={{
          background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
          marginBottom: 24
        }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <h2 style={{
              margin: 0,
              fontSize: 24,
              fontWeight: 700,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              <LineChartOutlined /> 股票行情查询
            </h2>
            <p style={{ margin: '8px 0 0 0', color: '#8c8c8c' }}>
              输入股票代码查询实时行情和历史数据
            </p>
          </div>
          <Input.Search
            placeholder="输入股票代码（如：000001、600000、300750）"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            onSearch={handleSearch}
            enterButton={
              <Button
                type="primary"
                icon={<SearchOutlined />}
                size="large"
                style={{ height: 48 }}
              >
                查询
              </Button>
            }
            size="large"
            loading={loading}
            style={{ maxWidth: 600 }}
          />
        </Space>
      </Card>

      {loading && (
        <div style={{ textAlign: 'center', padding: '80px 0' }}>
          <Spin size="large" tip="正在获取行情数据..." />
        </div>
      )}

      {!loading && quote && (
        <>
          <Card
            title={
              <Space size="large">
                <span style={{ fontSize: 24, fontWeight: 700 }}>{quote.name}</span>
                <span style={{ fontSize: 18, color: '#8c8c8c' }}>{quote.symbol}</span>
              </Space>
            }
            extra={
              <span style={{ fontSize: 14, color: '#8c8c8c' }}>
                实时行情
              </span>
            }
            style={{
              marginBottom: 24,
              background: quote.change_pct >= 0
                ? 'linear-gradient(135deg, #fff5f5 0%, #ffe7e7 100%)'
                : 'linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%)',
            }}
            hoverable
          >
            <Row gutter={[24, 24]}>
              <Col xs={24} sm={12} lg={6}>
                <Card
                  style={{
                    background: '#fff',
                    borderLeft: `4px solid ${quote.change_pct >= 0 ? '#ff4d4f' : '#52c41a'}`
                  }}
                >
                  <Statistic
                    title={<span style={{ fontSize: 16, fontWeight: 600 }}>最新价</span>}
                    value={quote.price}
                    precision={2}
                    valueStyle={{
                      color: quote.change_pct >= 0 ? '#ff4d4f' : '#52c41a',
                      fontSize: 36,
                      fontWeight: 700
                    }}
                    prefix={quote.change_pct >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                    suffix={
                      <span style={{ fontSize: 18 }}>
                        ({quote.change_pct >= 0 ? '+' : ''}{quote.change_pct.toFixed(2)}%)
                      </span>
                    }
                  />
                </Card>
              </Col>
              <Col xs={12} sm={6} lg={4}>
                <Statistic
                  title="开盘"
                  value={quote.open}
                  precision={2}
                  valueStyle={{ fontSize: 20, fontWeight: 600 }}
                />
              </Col>
              <Col xs={12} sm={6} lg={4}>
                <Statistic
                  title="最高"
                  value={quote.high}
                  precision={2}
                  valueStyle={{ fontSize: 20, fontWeight: 600, color: '#ff4d4f' }}
                />
              </Col>
              <Col xs={12} sm={6} lg={4}>
                <Statistic
                  title="最低"
                  value={quote.low}
                  precision={2}
                  valueStyle={{ fontSize: 20, fontWeight: 600, color: '#52c41a' }}
                />
              </Col>
              <Col xs={12} sm={6} lg={3}>
                <Statistic
                  title="昨收"
                  value={quote.prev_close}
                  precision={2}
                  valueStyle={{ fontSize: 20, fontWeight: 600 }}
                />
              </Col>
              <Col xs={12} sm={6} lg={3}>
                {quote.turnover !== undefined && (
                  <Statistic
                    title="换手率"
                    value={quote.turnover}
                    precision={2}
                    suffix="%"
                    valueStyle={{ fontSize: 20, fontWeight: 600 }}
                  />
                )}
              </Col>
            </Row>

            <Divider />

            <Row gutter={[24, 24]}>
              <Col xs={12} sm={8}>
                <Statistic
                  title="成交量"
                  value={quote.volume}
                  suffix="手"
                  valueStyle={{ fontSize: 18, fontWeight: 600, color: '#1890ff' }}
                />
              </Col>
              <Col xs={12} sm={8}>
                <Statistic
                  title="成交额"
                  value={(quote.amount / 100000000).toFixed(2)}
                  suffix="亿"
                  valueStyle={{ fontSize: 18, fontWeight: 600, color: '#1890ff' }}
                />
              </Col>
              <Col xs={12} sm={8}>
                <Statistic
                  title="振幅"
                  value={((quote.high - quote.low) / quote.prev_close * 100).toFixed(2)}
                  suffix="%"
                  valueStyle={{ fontSize: 18, fontWeight: 600, color: '#722ed1' }}
                />
              </Col>
            </Row>
          </Card>

          <Card
            title={
              <Space>
                <LineChartOutlined style={{ fontSize: 18, color: '#667eea' }} />
                <span style={{ fontSize: 18, fontWeight: 600 }}>日K线图</span>
              </Space>
            }
            extra={<span style={{ color: '#8c8c8c' }}>共 {dailyData.length} 条数据</span>}
            hoverable
          >
            <div
              style={{
                height: 400,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%)',
                borderRadius: 8,
                border: '2px dashed #d9d9d9'
              }}
            >
              <div style={{ textAlign: 'center' }}>
                <LineChartOutlined style={{ fontSize: 48, color: '#d9d9d9', marginBottom: 16 }} />
                <p style={{ color: '#999', fontSize: 16 }}>
                  K线图功能开发中...
                </p>
                <p style={{ color: '#bfbfbf', fontSize: 14 }}>
                  已获取 {dailyData.length} 条历史数据
                </p>
              </div>
            </div>
          </Card>
        </>
      )}

      {!loading && !quote && symbol && (
        <Card style={{ textAlign: 'center', padding: '60px 0' }}>
          <SearchOutlined style={{ fontSize: 64, color: '#d9d9d9', marginBottom: 16 }} />
          <p style={{ fontSize: 18, color: '#8c8c8c' }}>
            请输入股票代码开始查询
          </p>
        </Card>
      )}
    </div>
  );
}
