import { useEffect, useState } from 'react';
import { Table, Tag, Button, Input, Space } from 'antd';
import { useNavigate } from 'react-router-dom';
import { skillApi, permissionApi } from '../api';
import { message } from 'antd';

export default function Skills() {
  const [skills, setSkills] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [keyword, setKeyword] = useState('');
  const navigate = useNavigate();

  const loadSkills = async () => {
    const res: any = await skillApi.getList({ page, page_size: 20, keyword: keyword || undefined });
    setSkills(res.data?.items || []);
    setTotal(res.data?.total || 0);
  };

  useEffect(() => { loadSkills(); }, [page]);

  const handleApply = async (skillId: number) => {
    try {
      await permissionApi.createRequest({ type: 'skill', target_id: skillId, reason: '' });
      message.success('申请已提交');
      loadSkills();
    } catch (e: any) {
      message.error(e?.message || '申请失败');
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '名称', dataIndex: 'name', key: 'name', render: (name: string, record: any) => <a onClick={() => navigate(`/skills/${record.id}`)}>{name}</a> },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
    { title: '工具数', dataIndex: 'tool_count', key: 'tool_count', width: 80 },
    {
      title: '权限', dataIndex: 'has_permission', key: 'has_permission', width: 100,
      render: (v: boolean) => v ? <Tag color="green">已授权</Tag> : <Tag color="orange">未授权</Tag>,
    },
    {
      title: '操作', key: 'action', width: 100,
      render: (_: any, record: any) => record.has_permission ? '-' : (
        <Button size="small" type="link" onClick={() => handleApply(record.id)}>申请权限</Button>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Skills 浏览</h2>
        <Input.Search placeholder="搜索" onSearch={(v) => { setKeyword(v); setPage(1); loadSkills(); }} style={{ width: 250 }} />
      </div>
      <Table rowKey="id" columns={columns} dataSource={skills} pagination={{ current: page, total, pageSize: 20, onChange: setPage }} />
    </div>
  );
}
