import React from 'react';
import { Card, Row, Col } from 'antd';
import '../styles/animations.css';

interface SkeletonProps {
  type?: 'card' | 'table' | 'stat' | 'text';
  rows?: number;
  loading?: boolean;
  children?: React.ReactNode;
}

export const SkeletonCard: React.FC = () => (
  <Card className="fade-in">
    <div className="skeleton skeleton-title" />
    <div className="skeleton skeleton-text" style={{ width: '90%' }} />
    <div className="skeleton skeleton-text" style={{ width: '75%' }} />
    <div className="skeleton skeleton-text" style={{ width: '85%' }} />
  </Card>
);

export const SkeletonStat: React.FC = () => (
  <Card className="fade-in">
    <div className="skeleton skeleton-text" style={{ width: '40%', marginBottom: 8 }} />
    <div className="skeleton" style={{ height: 32, width: '60%' }} />
  </Card>
);

export const SkeletonTable: React.FC<{ rows?: number }> = ({ rows = 5 }) => (
  <Card className="fade-in">
    <div className="skeleton skeleton-title" style={{ marginBottom: 24 }} />
    {Array.from({ length: rows }).map((_, index) => (
      <div key={index} style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={6}>
            <div className="skeleton skeleton-text" />
          </Col>
          <Col span={6}>
            <div className="skeleton skeleton-text" />
          </Col>
          <Col span={6}>
            <div className="skeleton skeleton-text" />
          </Col>
          <Col span={6}>
            <div className="skeleton skeleton-text" />
          </Col>
        </Row>
      </div>
    ))}
  </Card>
);

export const SkeletonDashboard: React.FC = () => (
  <div>
    <Row gutter={[24, 24]} className="fade-in-up">
      {[1, 2, 3].map((i) => (
        <Col xs={24} sm={12} lg={8} key={i} className={`fade-in-up delay-${i}00`}>
          <SkeletonStat />
        </Col>
      ))}
    </Row>
    <Row gutter={[24, 24]} style={{ marginTop: 32 }}>
      <Col xs={24} lg={12} className="fade-in-up delay-400">
        <SkeletonTable rows={10} />
      </Col>
      <Col xs={24} lg={12} className="fade-in-up delay-500">
        <SkeletonTable rows={10} />
      </Col>
    </Row>
  </div>
);

export const Skeleton: React.FC<SkeletonProps> = ({
  type = 'card',
  rows = 3,
  loading = true,
  children,
}) => {
  if (!loading && children) {
    return <>{children}</>;
  }

  if (!loading) {
    return null;
  }

  switch (type) {
    case 'stat':
      return <SkeletonStat />;
    case 'table':
      return <SkeletonTable rows={rows} />;
    case 'text':
      return (
        <div>
          {Array.from({ length: rows }).map((_, i) => (
            <div key={i} className="skeleton skeleton-text" />
          ))}
        </div>
      );
    case 'card':
    default:
      return <SkeletonCard />;
  }
};

export default Skeleton;
