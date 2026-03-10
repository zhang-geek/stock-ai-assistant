import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, Row, Col, Table, Statistic, message, Tag, Space } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, ReloadOutlined } from '@ant-design/icons';
import { quoteApi } from '../api/quote';
import type { IndexQuote, Quote, Sector } from '../types';
import { SkeletonDashboard } from '../components/Skeleton';
import '../styles/animations.css';

// 常量定义
const REFRESH_INTERVAL = 60000; // 60 seconds
const ANIMATION_DELAY_STEP = 100; // milliseconds
const MAX_ANIMATION_DELAY = 500; // milliseconds

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [indices, setIndices] = useState<IndexQuote[]>([]);
  const [gainers, setGainers] = useState<Quote[]>([]);
  const [losers, setLosers] = useState<Quote[]>([]);
  const [sectors, setSectors] = useState<Sector[]>([]);

  // 使用 useCallback 避免依赖问题
  const fetchData = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    }

    try {
      const [indexRes, gainersRes, losersRes, sectorsRes] = await Promise.all([
        quoteApi.getIndex(),
        quoteApi.getTopGainers(10),
        quoteApi.getTopLosers(10),
        quoteApi.getSectors(15),
      ]);

      setIndices(indexRes.data.data);
      setGainers(gainersRes.data.data);
      setLosers(losersRes.data.data);
      setSectors(sectorsRes.data.data);

      if (isRefresh) {
        message.success('数据已更新');
      }
    } catch (error) {
      console.error('Dashboard data fetch failed:', error);
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      message.error(`数据加载失败: ${errorMessage}`);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => fetchData(), REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchData]);

  // 格式化百分比 - 使用 useCallback 避免重复创建
  const formatPercent = useCallback((value: number) => {
    const prefix = value >= 0 ? '+' : '';
    return (
      <Tag color={value >= 0 ? 'red' : 'green'} style={{ fontWeight: 600, fontSize: '13px' }}>
        {prefix}{value.toFixed(2)}%
      </Tag>
    );
  }, []);

  // 使用 useMemo 缓存列定义
  const stockColumns = useMemo(() => [
    {
      title: '代码',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
      render: (text: string) => <span style={{ fontWeight: 600, color: '#1890ff' }}>{text}</span>,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 120,
      render: (text: string) => <span style={{ fontWeight: 500 }}>{text}</span>,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (val: number) => <span style={{ fontSize: '15px', fontWeight: 600 }}>¥{val.toFixed(2)}</span>,
      width: 100,
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_pct',
      key: 'change_pct',
      render: formatPercent,
      width: 100,
    },
  ], [formatPercent]);

  const sectorColumns = useMemo(() => [
    {
      title: '板块',
      dataIndex: 'sector',
      key: 'sector',
      render: (text: string) => <span style={{ fontWeight: 600 }}>{text}</span>,
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_pct',
      key: 'change_pct',
      render: formatPercent,
      sorter: (a: Sector, b: Sector) => a.change_pct - b.change_pct,
    },
    {
      title: '上涨/下跌',
      key: 'updown',
      render: (_: unknown, record: Sector) => (
        <Space size="small">
          <Tag color="red">{record.up_count}↑</Tag>
          <Tag color="green">{record.down_count}↓</Tag>
        </Space>
      ),
    },
    {
      title: '换手率',
      dataIndex: 'turnover',
      key: 'turnover',
      render: (val: number) => <span style={{ fontWeight: 500 }}>{val.toFixed(2)}%</span>,
    },
  ], [formatPercent]);

  // 辅助函数：获取动画类名
  const getAnimationClass = useCallback((index: number, baseClass: string) => {
    const delay = Math.min((index + 1) * ANIMATION_DELAY_STEP, MAX_ANIMATION_DELAY);
    return `${baseClass} delay-${delay}`;
  }, []);

  // 辅助函数：获取卡片样式
  const getCardStyle = useCallback((changePct: number) => ({
    background: changePct >= 0
      ? 'linear-gradient(135deg, #fff5f5 0%, #ffe7e7 100%)'
      : 'linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%)',
    borderLeft: `4px solid ${changePct >= 0 ? '#ff4d4f' : '#52c41a'}`
  }), []);

  if (loading) {
    return <SkeletonDashboard />;
  }

  return (
    <div>
      <div
        style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
        className="fade-in-up"
      >
        <h1 style={{
          margin: 0,
          fontSize: 28,
          fontWeight: 700,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          市场概览
        </h1>
        <ReloadOutlined
          onClick={() => fetchData(true)}
          className={`refresh-icon ${refreshing ? 'spinning' : ''}`}
          style={{ fontSize: 20, cursor: 'pointer', color: '#667eea' }}
          role="button"
          aria-label="刷新数据"
          tabIndex={0}
          onKeyPress={(e) => e.key === 'Enter' && fetchData(true)}
        />
      </div>

      <Row gutter={[24, 24]}>
        {indices.map((index, i) => (
          <Col
            xs={24}
            sm={12}
            lg={8}
            key={index.symbol}
            className={getAnimationClass(i, 'fade-in-up')}
          >
            <Card
              hoverable
              className="interactive-card"
              style={getCardStyle(index.change_pct)}
            >
              <Statistic
                title={<span style={{ fontSize: 16, fontWeight: 600 }}>{index.name}</span>}
                value={index.price}
                precision={2}
                valueStyle={{
                  color: index.change_pct >= 0 ? '#ff4d4f' : '#52c41a',
                  fontSize: 32,
                  fontWeight: 700
                }}
                prefix={index.change_pct >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                suffix={
                  <span style={{ fontSize: 18, marginLeft: 8 }}>
                    {formatPercent(index.change_pct)}
                  </span>
                }
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: 32 }}>
        <Col xs={24} lg={12} className="slide-in-left delay-400">
          <Card
            title={
              <Space>
                <ArrowUpOutlined style={{ color: '#ff4d4f', fontSize: 18 }} />
                <span style={{ fontSize: 18, fontWeight: 600 }}>涨幅榜</span>
              </Space>
            }
            extra={<Tag color="red">TOP 10</Tag>}
            hoverable
            className="interactive-card"
          >
            <Table
              dataSource={gainers}
              columns={stockColumns}
              rowKey="symbol"
              pagination={false}
              size="middle"
            />
          </Card>
        </Col>
        <Col xs={24} lg={12} className="slide-in-right delay-400">
          <Card
            title={
              <Space>
                <ArrowDownOutlined style={{ color: '#52c41a', fontSize: 18 }} />
                <span style={{ fontSize: 18, fontWeight: 600 }}>跌幅榜</span>
              </Space>
            }
            extra={<Tag color="green">TOP 10</Tag>}
            hoverable
            className="interactive-card"
          >
            <Table
              dataSource={losers}
              columns={stockColumns}
              rowKey="symbol"
              pagination={false}
              size="middle"
            />
          </Card>
        </Col>
      </Row>

      <Row style={{ marginTop: 32 }}>
        <Col span={24} className="fade-in-up delay-500">
          <Card
            title={<span style={{ fontSize: 18, fontWeight: 600 }}>板块表现</span>}
            extra={<Tag color="blue">实时更新</Tag>}
            hoverable
            className="interactive-card"
          >
            <Table
              dataSource={sectors}
              columns={sectorColumns}
              rowKey="code"
              pagination={false}
              size="middle"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
