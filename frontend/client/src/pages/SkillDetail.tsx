import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Tag, Table, Button, message } from 'antd';
import { skillApi, permissionApi } from '../api';

export default function SkillDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [skill, setSkill] = useState<any>(null);
  const [tools, setTools] = useState<any[]>([]);

  useEffect(() => {
    async function load() {
      const [skillRes, toolsRes]: any[] = await Promise.all([
        skillApi.getDetail(Number(id)),
        skillApi.getTools(Number(id)),
      ]);
      setSkill(skillRes.data);
      setTools(toolsRes.data || []);
    }
    load();
  }, [id]);

  if (!skill) return <div>加载中...</div>;

  const handleApply = async (toolId: number) => {
    try {
      await permissionApi.createRequest({ type: 'tool', target_id: toolId, reason: '' });
      message.success('申请已提交');
    } catch (e: any) {
      message.error(e?.message || '申请失败');
    }
  };

  const toolColumns = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
    {
      title: '权限', dataIndex: 'has_permission', key: 'has_permission', width: 100,
      render: (v: boolean) => v ? <Tag color="green">已授权</Tag> : <Tag color="orange">未授权</Tag>,
    },
    {
      title: '操作', key: 'action', width: 100,
      render: (_: any, record: any) => record.has_permission ? '-' : (
        <Button size="small" type="link" onClick={() => handleApply(record.id)}>申请</Button>
      ),
    },
  ];

  return (
    <div>
      <Button onClick={() => navigate('/skills')} style={{ marginBottom: 16 }}>返回列表</Button>
      <Card>
        <Descriptions title={skill.name}>
          <Descriptions.Item label="描述">{skill.description || '-'}</Descriptions.Item>
          <Descriptions.Item label="状态"><Tag color={skill.status === 'active' ? 'green' : 'red'}>{skill.status}</Tag></Descriptions.Item>
          <Descriptions.Item label="权限">{skill.has_permission ? <Tag color="green">已授权</Tag> : <Tag color="orange">未授权</Tag>}</Descriptions.Item>
        </Descriptions>
      </Card>
      <Card title="包含的 Tools" style={{ marginTop: 16 }}>
        <Table rowKey="id" columns={toolColumns} dataSource={tools} pagination={false} />
      </Card>
    </div>
  );
}
