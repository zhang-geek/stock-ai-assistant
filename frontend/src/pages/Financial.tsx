import { useState } from 'react';
import { Card, Upload, Button, Input, message, Spin } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { financialApi } from '../api/financial';

export default function Financial() {
  const [analysis, setAnalysis] = useState('');
  const [comparison, setComparison] = useState('');
  const [loading, setLoading] = useState(false);
  const [symbols, setSymbols] = useState('');

  const handleUpload = async (file: File) => {
    setLoading(true);
    try {
      const res = await financialApi.analyze(file);
      setAnalysis(res.data.data);
      message.success('分析完成');
    } catch (err) {
      message.error('分析失败');
    } finally {
      setLoading(false);
    }
    return false;
  };

  const handleCompare = async () => {
    setLoading(true);
    try {
      const symbolList = symbols.split(',').map((s) => s.trim());
      const res = await financialApi.compare(symbolList);
      setComparison(res.data.data);
    } catch (err) {
      message.error('对比失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card title="财报分析" style={{ marginBottom: 16 }}>
        <Upload beforeUpload={handleUpload} accept=".pdf">
          <Button icon={<UploadOutlined />}>上传PDF财报</Button>
        </Upload>
      </Card>

      <Card title="股票对比" style={{ marginBottom: 16 }}>
        <Input
          placeholder="股票代码，逗号分隔"
          value={symbols}
          onChange={(e) => setSymbols(e.target.value)}
          style={{ width: 300, marginRight: 8 }}
        />
        <Button onClick={handleCompare}>对比</Button>
      </Card>

      {loading && <Spin />}

      {analysis && (
        <Card title="财报分析结果" style={{ marginBottom: 16 }}>
          <pre style={{ whiteSpace: 'pre-wrap' }}>{analysis}</pre>
        </Card>
      )}

      {comparison && (
        <Card title="对比结果">
          <pre style={{ whiteSpace: 'pre-wrap' }}>{comparison}</pre>
        </Card>
      )}
    </div>
  );
}
