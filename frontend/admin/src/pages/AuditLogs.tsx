import { useEffect, useState } from 'react';
import { Table, Select, Tag } from 'antd';
import { auditApi } from '../api';

const actionColors: Record<string, string> = {
  create: 'green', update: 'blue', delete: 'red', approve: 'cyan', reject: 'orange', login: 'purple',
};

export default function AuditLogs() {
  const [logs, setLogs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [actionFilter, setActionFilter] = useState<string | undefined>(undefined);
  const [typeFilter, setTypeFilter] = useState<string | undefined>(undefined);

  const loadLogs = async () => {
    const res: any = await auditApi.getList({ page, page_size: 20, action: actionFilter, target_type: typeFilter });
    setLogs(res.data?.items || []);
    setTotal(res.data?.total || 0);
  };

  useEffect(() => { loadLogs(); }, [page, actionFilter, typeFilter]);

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '用户ID', dataIndex: 'user_id', key: 'user_id', width: 80 },
    {
      title: '操作', dataIndex: 'action', key: 'action', width: 100,
      render: (a: string) => <Tag color={actionColors[a]}>{a}</Tag>,
    },
    { title: '目标类型', dataIndex: 'target_type', key: 'target_type', width: 120 },
    { title: '目标ID', dataIndex: 'target_id', key: 'target_id', width: 80 },
    { title: '详情', dataIndex: 'detail', key: 'detail', ellipsis: true, render: (d: any) => JSON.stringify(d) },
    { title: 'IP', dataIndex: 'ip_address', key: 'ip_address', width: 130 },
    { title: '时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>审计日志</h2>
        <div style={{ display: 'flex', gap: 8 }}>
          <Select allowClear placeholder="操作类型" style={{ width: 130 }} value={actionFilter} onChange={(v) => { setActionFilter(v); setPage(1); }}
            options={['create', 'update', 'delete', 'approve', 'reject'].map((a) => ({ label: a, value: a }))} />
          <Select allowClear placeholder="目标类型" style={{ width: 130 }} value={typeFilter} onChange={(v) => { setTypeFilter(v); setPage(1); }}
            options={['user', 'role', 'skill', 'tool', 'permission_request'].map((t) => ({ label: t, value: t }))} />
        </div>
      </div>
      <Table rowKey="id" columns={columns} dataSource={logs} pagination={{ current: page, total, pageSize: 20, onChange: setPage }} />
    </div>
  );
}
