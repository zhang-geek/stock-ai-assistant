import React from 'react';
import { Button, Space } from 'antd';
import {
  InboxOutlined,
  SearchOutlined,
  FrownOutlined,
  DisconnectOutlined,
  FileSearchOutlined,
} from '@ant-design/icons';
import '../styles/animations.css';

interface EmptyStateProps {
  type?: 'no-data' | 'search' | 'error' | 'offline' | 'not-found';
  title?: string;
  description?: string;
  action?: {
    text: string;
    onClick: () => void;
  };
}

const emptyStateConfig = {
  'no-data': {
    icon: <InboxOutlined />,
    title: '暂无数据',
    description: '当前没有可显示的内容',
  },
  search: {
    icon: <SearchOutlined />,
    title: '未找到结果',
    description: '请尝试其他搜索条件',
  },
  error: {
    icon: <FrownOutlined />,
    title: '出错了',
    description: '数据加载失败，请稍后重试',
  },
  offline: {
    icon: <DisconnectOutlined />,
    title: '网络连接失败',
    description: '请检查您的网络连接',
  },
  'not-found': {
    icon: <FileSearchOutlined />,
    title: '页面不存在',
    description: '您访问的页面不存在或已被删除',
  },
};

export const EmptyState: React.FC<EmptyStateProps> = ({
  type = 'no-data',
  title,
  description,
  action,
}) => {
  const config = emptyStateConfig[type];

  return (
    <div className="empty-state">
      <div className="empty-state-icon">{config.icon}</div>
      <h3
        style={{
          fontSize: 20,
          fontWeight: 600,
          color: '#262626',
          marginBottom: 8,
        }}
      >
        {title || config.title}
      </h3>
      <p
        style={{
          fontSize: 14,
          color: '#8c8c8c',
          marginBottom: action ? 24 : 0,
        }}
      >
        {description || config.description}
      </p>
      {action && (
        <Button type="primary" size="large" onClick={action.onClick}>
          {action.text}
        </Button>
      )}
    </div>
  );
};

export default EmptyState;
