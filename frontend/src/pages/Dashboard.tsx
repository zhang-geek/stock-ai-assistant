import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Table, Statistic, Spin, message, Tag, Space } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, ReloadOutlined } from '@ant-design/icons';
import { quoteApi } from '../api/quote';
import type { IndexQuote, Quote, Sector } from '../types';

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [indices, setIndices] = useState<IndexQuote[]>([]);
  const [gainers, setGainers] = useState<Quote[]>([]);
  const [losers, setLosers] = useState<Quote[]>([]);
  const [sectors, setSectors] = useState<Sector[]>([]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
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
    } catch (error) {
      message.error('数据加载失败');
    } finally {
      setLoading(false);
    }
  };

  const formatPercent = (value: number) => {
    const color = value >= 0 ? '#ff4d4f' : '#52c41a';
    const prefix = value >= 0 ? '+' : '';
    return (
      <Tag color={value >= 0 ? 'red' : 'green'} style={{ fontWeight: 600, fontSize: '13px' }}>
        {prefix}{value.toFixed(2)}%
      </Tag>
    );
  };

  const stockColumns = [
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
  ];

  const sectorColumns = [
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
      render: (_: any, record: Sector) => (
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
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '120px 0' }}>
        <Spin size="large" tip="加载市场数据中..." />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: 28, fontWeight: 700, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          市场概览
        </h1>
        <ReloadOutlined
          onClick={fetchData}
          style={{ fontSize: 20, cursor: 'pointer', color: '#667eea' }}
          spin={loading}
        />
      </div>

      <Row gutter={[24, 24]}>
        {indices.map((index) => (
          <Col xs={24} sm={12} lg={8} key={index.symbol}>
            <Card
              hoverable
              style={{
                background: index.change_pct >= 0
                  ? 'linear-gradient(135deg, #fff5f5 0%, #ffe7e7 100%)'
                  : 'linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%)',
                borderLeft: `4px solid ${index.change_pct >= 0 ? '#ff4d4f' : '#52c41a'}`
              }}
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
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <ArrowUpOutlined style={{ color: '#ff4d4f', fontSize: 18 }} />
                <span style={{ fontSize: 18, fontWeight: 600 }}>涨幅榜</span>
              </Space>
            }
            extra={<Tag color="red">TOP 10</Tag>}
            hoverable
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
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <ArrowDownOutlined style={{ color: '#52c41a', fontSize: 18 }} />
                <span style={{ fontSize: 18, fontWeight: 600 }}>跌幅榜</span>
              </Space>
            }
            extra={<Tag color="green">TOP 10</Tag>}
            hoverable
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
        <Col span={24}>
          <Card
            title={<span style={{ fontSize: 18, fontWeight: 600 }}>板块表现</span>}
            extra={<Tag color="blue">实时更新</Tag>}
            hoverable
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
