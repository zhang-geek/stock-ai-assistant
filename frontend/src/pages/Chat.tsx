import { useState } from 'react';
import { Input, Button, Card, Spin, message } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import { chatApi } from '../api/chat';

const { TextArea } = Input;

export default function Chat() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState('');
  const [metadata, setMetadata] = useState<{
    provider?: string;
    task_type?: string;
    tokens?: number;
    cost_usd?: number;
  }>({});

  const handleSubmit = async () => {
    if (!question.trim()) {
      message.warning('请输入问题');
      return;
    }

    setLoading(true);
    setAnswer('');
    setMetadata({});

    try {
      const response = await chatApi.ask(question);

      if (response.data.data) {
        setAnswer(response.data.data);
        // Extract metadata if available from response headers or body
        setMetadata({
          provider: 'DeepSeek',
          task_type: 'chat',
        });
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
    <div>
      <Card title="AI 问答">
        <TextArea
          placeholder="输入您的问题（Ctrl+Enter 提交）"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyPress={handleKeyPress}
          rows={4}
          style={{ marginBottom: 16 }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSubmit}
          loading={loading}
          size="large"
        >
          提问
        </Button>
      </Card>

      {loading && (
        <Card style={{ marginTop: 16 }}>
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Spin size="large" tip="AI 正在思考..." />
          </div>
        </Card>
      )}

      {!loading && answer && (
        <Card
          title="AI 回答"
          style={{ marginTop: 16 }}
          extra={
            metadata.provider && (
              <span style={{ fontSize: 12, color: '#999' }}>
                {metadata.provider}
                {metadata.tokens && ` · ${metadata.tokens} tokens`}
                {metadata.cost_usd && ` · $${metadata.cost_usd.toFixed(4)}`}
              </span>
            )
          }
        >
          <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word', fontFamily: 'inherit' }}>
            {answer}
          </pre>
        </Card>
      )}
    </div>
  );
}
