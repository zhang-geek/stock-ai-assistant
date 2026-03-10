import { useState, useEffect } from 'react';
import { Card, Button, Input, InputNumber, Table, message, Spin } from 'antd';
import { paperApi } from '../api/paper';
import type { Portfolio } from '../types';

export default function Paper() {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(false);
  const [symbol, setSymbol] = useState('');
  const [price, setPrice] = useState(0);
  const [quantity, setQuantity] = useState(100);

  useEffect(() => {
    loadPortfolio();
  }, []);

  const loadPortfolio = async () => {
    setLoading(true);
    try {
      const res = await paperApi.getPortfolio();
      setPortfolio(res.data.data);
    } catch (err) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleBuy = async () => {
    try {
      await paperApi.buy({ symbol, price, quantity });
      message.success('买入成功');
      loadPortfolio();
    } catch (err) {
      message.error('买入失败');
    }
  };

  const handleSell = async () => {
    try {
      await paperApi.sell({ symbol, price, quantity });
      message.success('卖出成功');
      loadPortfolio();
    } catch (err) {
      message.error('卖出失败');
    }
  };

  return (
    <div>
      <Card title="模拟交易" style={{ marginBottom: 16 }}>
        {loading && <Spin />}
        {portfolio && (
          <div>
            <p>总资产: ¥{portfolio.total_value.toFixed(2)}</p>
            <p>现金: ¥{portfolio.cash.toFixed(2)}</p>
            <p>盈亏: ¥{portfolio.total_pnl.toFixed(2)} ({(portfolio.pnl_pct * 100).toFixed(2)}%)</p>
          </div>
        )}
      </Card>

      <Card title="交易操作" style={{ marginBottom: 16 }}>
        <Input
          placeholder="股票代码"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          style={{ width: 120, marginRight: 8 }}
        />
        <InputNumber
          placeholder="价格"
          value={price}
          onChange={(v) => setPrice(v || 0)}
          style={{ width: 100, marginRight: 8 }}
        />
        <InputNumber
          placeholder="数量"
          value={quantity}
          onChange={(v) => setQuantity(v || 100)}
          style={{ width: 100, marginRight: 8 }}
        />
        <Button onClick={handleBuy} type="primary">
          买入
        </Button>
        <Button onClick={handleSell} style={{ marginLeft: 8 }}>
          卖出
        </Button>
      </Card>

      <Card title="持仓">
        <Table
          dataSource={portfolio?.positions || []}
          columns={[
            { title: '代码', dataIndex: 'symbol', key: 'symbol' },
            { title: '名称', dataIndex: 'name', key: 'name' },
            { title: '数量', dataIndex: 'quantity', key: 'quantity' },
            { title: '成本', dataIndex: 'entry_price', key: 'entry_price' },
            { title: '现价', dataIndex: 'current_price', key: 'current_price' },
            { title: '盈亏', dataIndex: 'pnl', key: 'pnl', render: (v: number) => v.toFixed(2) },
          ]}
          rowKey="id"
          pagination={false}
        />
      </Card>
    </div>
  );
}
