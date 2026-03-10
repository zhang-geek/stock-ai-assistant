import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Table, Statistic, Spin, message } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
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
    const interval = setInterval(fetchData, 60000); // Refresh every minute
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
    const color = value >= 0 ? '#cf1322' : '#3f8600';
    const prefix = value >= 0 ? '+' : '';
    return <span style={{ color }}>{prefix}{value.toFixed(2)}%</span>;
  };

  const stockColumns = [
    {
      title: '代码',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 120,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (val: number) => val.toFixed(2),
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
        <span>
          <span style={{ color: '#cf1322' }}>{record.up_count}</span>
          {' / '}
          <span style={{ color: '#3f8600' }}>{record.down_count}</span>
        </span>
      ),
    },
    {
      title: '换手率',
      dataIndex: 'turnover',
      key: 'turnover',
      render: (val: number) => `${val.toFixed(2)}%`,
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]}>
        {indices.map((index) => (
          <Col xs={24} sm={12} lg={8} key={index.symbol}>
            <Card>
              <Statistic
                title={index.name}
                value={index.price}
                precision={2}
                valueStyle={{ color: index.change_pct >= 0 ? '#cf1322' : '#3f8600' }}
                prefix={index.change_pct >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                suffix={formatPercent(index.change_pct)}
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title="涨幅榜" bordered={false}>
            <Table
              dataSource={gainers}
              columns={stockColumns}
              rowKey="symbol"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="跌幅榜" bordered={false}>
            <Table
              dataSource={losers}
              columns={stockColumns}
              rowKey="symbol"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>

      <Row style={{ marginTop: '24px' }}>
        <Col span={24}>
          <Card title="板块表现" bordered={false}>
            <Table
              dataSource={sectors}
              columns={sectorColumns}
              rowKey="code"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
