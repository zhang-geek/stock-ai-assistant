import { useState, useRef, useEffect } from 'react';
import { Input, Button, Card, message, Space, Tag } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons';
import { chatApi } from '../api/chat';
import EmptyState from '../components/EmptyState';
import '../styles/animations.css';

const { TextArea } = Input;

interface Message {
  role: 'user' | 'assistant';
  content: string;
  metadata?: {
    provider?: string;
    task_type?: string;
    tokens?: number;
    cost_usd?: number;
  };
}

export default function Chat() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async () => {
    if (!question.trim()) {
      message.warning('请输入问题');
      return;
    }

    const userMessage: Message = {
      role: 'user',
      content: question,
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuestion('');
    setLoading(true);

    try {
      const response = await chatApi.ask(question);

      if (response.data.data) {
        const assistantMessage: Message = {
          role: 'assistant',
          content: response.data.data,
          metadata: {
            provider: 'DeepSeek',
            task_type: 'chat',
          },
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }
    } catch (error) {
      message.error('AI 回答失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleSubmit();
    }
  };

  return (
    <div className="fade-in-up" style={{ height: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column' }}>
      <Card
        title={
          <Space>
            <RobotOutlined style={{ fontSize: 20, color: '#667eea' }} />
            <span style={{ fontSize: 20, fontWeight: 600 }}>AI 智能问答</span>
          </Space>
        }
        extra={<Tag color="purple">DeepSeek</Tag>}
        style={{ flex: 1, display: 'flex', flexDirection: 'column', marginBottom: 16 }}
        bodyStyle={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column' }}
        className="interactive-card"
      >
        {messages.length === 0 ? (
          <EmptyState
            type="no-data"
            title="开始对话"
            description="向AI提问关于股票市场的任何问题"
          />
        ) : (
          <div style={{ flex: 1, overflow: 'auto', padding: '16px 0' }}>
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`fade-in-up delay-${Math.min(index * 100, 500)}`}
                style={{
                  marginBottom: 24,
                  display: 'flex',
                  gap: 12,
                  alignItems: 'flex-start',
                }}
              >
                <div
                  style={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    background: msg.role === 'user'
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                      : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    fontSize: 18,
                    flexShrink: 0,
                  }}
                >
                  {msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                </div>
                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      background: msg.role === 'user' ? '#f0f0f0' : '#fff',
                      padding: '12px 16px',
                      borderRadius: 12,
                      border: msg.role === 'assistant' ? '1px solid #e8e8e8' : 'none',
                      boxShadow: msg.role === 'assistant' ? '0 2px 8px rgba(0,0,0,0.05)' : 'none',
                    }}
                  >
                    <pre
                      style={{
                        whiteSpace: 'pre-wrap',
                        wordWrap: 'break-word',
                        fontFamily: 'inherit',
                        margin: 0,
                        fontSize: 14,
                        lineHeight: 1.6,
                      }}
                    >
                      {msg.content}
                    </pre>
                  </div>
                  {msg.metadata && (
                    <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
                      <Space size="small">
                        {msg.metadata.provider && <Tag color="blue">{msg.metadata.provider}</Tag>}
                        {msg.metadata.tokens && <span>{msg.metadata.tokens} tokens</span>}
                        {msg.metadata.cost_usd && <span>${msg.metadata.cost_usd.toFixed(4)}</span>}
                      </Space>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="fade-in" style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                <div
                  style={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    fontSize: 18,
                  }}
                >
                  <RobotOutlined />
                </div>
                <div
                  style={{
                    background: '#fff',
                    padding: '12px 16px',
                    borderRadius: 12,
                    border: '1px solid #e8e8e8',
                  }}
                >
                  <div className="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </Card>

      <Card className="interactive-card">
        <Space.Compact style={{ width: '100%' }} size="large">
          <div className="enhanced-input" style={{ flex: 1 }}>
            <TextArea
              placeholder="输入您的问题（Ctrl+Enter 提交）"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyPress}
              rows={3}
              disabled={loading}
              style={{ resize: 'none' }}
            />
          </div>
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSubmit}
            loading={loading}
            size="large"
            className="ripple-button"
            style={{ height: 'auto', minHeight: 88 }}
          >
            提问
          </Button>
        </Space.Compact>
      </Card>
    </div>
  );
}
