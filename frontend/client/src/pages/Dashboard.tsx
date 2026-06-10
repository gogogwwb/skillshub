import { useEffect, useState } from 'react';
import { Card, Col, Row, Statistic } from 'antd';
import { AppstoreOutlined, ToolOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { userApi, skillApi, toolApi } from '../api';

export default function Dashboard() {
  const [stats, setStats] = useState({ skills: 0, tools: 0, mySkills: 0, myTools: 0 });

  useEffect(() => {
    async function load() {
      try {
        const [permRes, skillsRes, toolsRes]: any[] = await Promise.all([
          userApi.getPermissions(),
          skillApi.getList({ page: 1, page_size: 1 }),
          toolApi.getList({ page: 1, page_size: 1 }),
        ]);
        setStats({
          skills: skillsRes.data?.total || 0,
          tools: toolsRes.data?.total || 0,
          mySkills: permRes.data?.skills?.length || 0,
          myTools: permRes.data?.tools?.length || 0,
        });
      } catch (e) {
        console.error(e);
      }
    }
    load();
  }, []);

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>权限概览</h2>
      <Row gutter={16}>
        <Col span={6}>
          <Card><Statistic title="可用Skills" value={stats.mySkills} prefix={<AppstoreOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="可用Tools" value={stats.myTools} prefix={<ToolOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="全部Skills" value={stats.skills} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="全部Tools" value={stats.tools} /></Card>
        </Col>
      </Row>
    </div>
  );
}
