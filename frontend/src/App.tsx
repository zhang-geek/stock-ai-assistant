import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import {
  HomeOutlined,
  LineChartOutlined,
  CommentOutlined,
  BarChartOutlined,
  ExperimentOutlined,
  WalletOutlined,
  FileTextOutlined,
  DollarOutlined,
  StarOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import Dashboard from './pages/Dashboard';
import Quote from './pages/Quote';
import Chat from './pages/Chat';
import Market from './pages/Market';
import Sentiment from './pages/Sentiment';
import Backtest from './pages/Backtest';
import Style from './pages/Style';
import Paper from './pages/Paper';
import Financial from './pages/Financial';
import Cost from './pages/Cost';

const { Header, Sider, Content } = Layout;

const menuItems = [
  { key: '/', icon: <HomeOutlined />, label: <Link to="/">首页</Link> },
  { key: '/quote', icon: <LineChartOutlined />, label: <Link to="/quote">行情</Link> },
  { key: '/chat', icon: <CommentOutlined />, label: <Link to="/chat">AI问答</Link> },
  { key: '/market', icon: <RiseOutlined />, label: <Link to="/market">市场监控</Link> },
  { key: '/sentiment', icon: <StarOutlined />, label: <Link to="/sentiment">舆情分析</Link> },
  { key: '/backtest', icon: <BarChartOutlined />, label: <Link to="/backtest">交易回测</Link> },
  { key: '/style', icon: <ExperimentOutlined />, label: <Link to="/style">风格探索</Link> },
  { key: '/paper', icon: <WalletOutlined />, label: <Link to="/paper">模拟交易</Link> },
  { key: '/financial', icon: <FileTextOutlined />, label: <Link to="/financial">财报分析</Link> },
  { key: '/cost', icon: <DollarOutlined />, label: <Link to="/cost">费用统计</Link> },
];

function App() {
  return (
    <BrowserRouter>
      <Layout style={{ minHeight: '100vh' }}>
        <Header style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
          A股AI助手
        </Header>
        <Layout>
          <Sider width={200} theme="light">
            <Menu mode="inline" items={menuItems} defaultSelectedKeys={['/']} />
          </Sider>
          <Content style={{ padding: '24px', background: '#f0f2f5' }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/quote" element={<Quote />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/market" element={<Market />} />
              <Route path="/sentiment" element={<Sentiment />} />
              <Route path="/backtest" element={<Backtest />} />
              <Route path="/style" element={<Style />} />
              <Route path="/paper" element={<Paper />} />
              <Route path="/financial" element={<Financial />} />
              <Route path="/cost" element={<Cost />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </BrowserRouter>
  );
}

export default App
