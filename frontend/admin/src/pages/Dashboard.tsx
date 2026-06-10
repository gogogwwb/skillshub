import { useEffect, useState } from 'react';
import { Card, Col, Row, Statistic } from 'antd';
import { UserOutlined, AppstoreOutlined, ToolOutlined, AuditOutlined } from '@ant-design/icons';
import { userApi, skillApi, toolApi, approvalApi } from '../api';

export default function Dashboard() {
  const [stats, setStats] = useState({ users: 0, skills: 0, tools: 0, pendingApprovals: 0 });

  useEffect(() => {
    async function loadStats() {
      try {
        const [usersRes, skillsRes, toolsRes, approvalsRes]: any[] = await Promise.all([
          userApi.getList({ page: 1, page_size: 1 }),
          skillApi.getList({ page: 1, page_size: 1 }),
          toolApi.getList({ page: 1, page_size: 1 }),
          approvalApi.getList({ page: 1, page_size: 1, status: 'pending' }),
        ]);
        setStats({
          users: usersRes.data?.total || 0,
          skills: skillsRes.data?.total || 0,
          tools: toolsRes.data?.total || 0,
          pendingApprovals: approvalsRes.data?.total || 0,
        });
      } catch (e) {
        console.error(e);
      }
    }
    loadStats();
  }, []);

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Dashboard</h2>
      <Row gutter={16}>
        <Col span={6}>
          <Card><Statistic title="用户总数" value={stats.users} prefix={<UserOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Skills数量" value={stats.skills} prefix={<AppstoreOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Tools数量" value={stats.tools} prefix={<ToolOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="待审批" value={stats.pendingApprovals} prefix={<AuditOutlined />} valueStyle={{ color: stats.pendingApprovals > 0 ? '#cf1322' : undefined }} /></Card>
        </Col>
      </Row>
    </div>
  );
}
