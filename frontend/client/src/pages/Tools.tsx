import { useEffect, useState } from 'react';
import { Table, Tag, Button, Input, Select } from 'antd';
import { useNavigate } from 'react-router-dom';
import { toolApi, skillApi, permissionApi } from '../api';
import { message } from 'antd';

export default function Tools() {
  const [tools, setTools] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [keyword, setKeyword] = useState('');
  const [skillFilter, setSkillFilter] = useState<number | undefined>(undefined);
  const [skills, setSkills] = useState<any[]>([]);
  const navigate = useNavigate();

  const loadTools = async () => {
    const res: any = await toolApi.getList({ page, page_size: 20, keyword: keyword || undefined, skill_id: skillFilter });
    setTools(res.data?.items || []);
    setTotal(res.data?.total || 0);
  };

  const loadSkills = async () => {
    const res: any = await skillApi.getList({ page: 1, page_size: 100 });
    setSkills(res.data?.items || []);
  };

  useEffect(() => { loadTools(); loadSkills(); }, [page, skillFilter]);

  const handleApply = async (toolId: number) => {
    try {
      await permissionApi.createRequest({ type: 'tool', target_id: toolId, reason: '' });
      message.success('申请已提交');
      loadTools();
    } catch (e: any) {
      message.error(e?.message || '申请失败');
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '名称', dataIndex: 'name', key: 'name', render: (name: string, record: any) => <a onClick={() => navigate(`/tools/${record.id}`)}>{name}</a> },
    { title: '所属Skill', dataIndex: 'skill_name', key: 'skill_name' },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
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
        <h2>Tools 浏览</h2>
        <div style={{ display: 'flex', gap: 8 }}>
          <Select allowClear placeholder="按Skill筛选" style={{ width: 180 }} value={skillFilter} onChange={(v) => { setSkillFilter(v); setPage(1); }}
            options={skills.map((s) => ({ label: s.name, value: s.id }))} />
          <Input.Search placeholder="搜索" onSearch={(v) => { setKeyword(v); setPage(1); loadTools(); }} style={{ width: 200 }} />
        </div>
      </div>
      <Table rowKey="id" columns={columns} dataSource={tools} pagination={{ current: page, total, pageSize: 20, onChange: setPage }} />
    </div>
  );
}
