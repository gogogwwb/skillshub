import { useEffect, useState } from 'react';
import { Table, Button, Tag, Space, Modal, Input, Select, message } from 'antd';
import { approvalApi } from '../api';

export default function Approvals() {
  const [items, setItems] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const [commentModalOpen, setCommentModalOpen] = useState(false);
  const [currentAction, setCurrentAction] = useState<{ id: number; action: 'approve' | 'reject' } | null>(null);
  const [comment, setComment] = useState('');

  const loadData = async () => {
    const res: any = await approvalApi.getList({ page, page_size: 20, status: statusFilter });
    setItems(res.data?.items || []);
    setTotal(res.data?.total || 0);
  };

  useEffect(() => { loadData(); }, [page, statusFilter]);

  const handleAction = async () => {
    if (!currentAction) return;
    if (currentAction.action === 'approve') {
      await approvalApi.approve(currentAction.id, comment);
      message.success('已通过');
    } else {
      await approvalApi.reject(currentAction.id, comment);
      message.success('已拒绝');
    }
    setCommentModalOpen(false);
    setCurrentAction(null);
    setComment('');
    loadData();
  };

  const statusColors: Record<string, string> = { pending: 'orange', approved: 'green', rejected: 'red', cancelled: 'default' };
  const statusLabels: Record<string, string> = { pending: '待审批', approved: '已通过', rejected: '已拒绝', cancelled: '已撤销' };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '申请人', dataIndex: 'user_name', key: 'user_name' },
    { title: '类型', dataIndex: 'type', key: 'type', render: (t: string) => <Tag>{t}</Tag> },
    { title: '目标', dataIndex: 'target_name', key: 'target_name' },
    { title: '理由', dataIndex: 'reason', key: 'reason', ellipsis: true },
    {
      title: '状态', dataIndex: 'status', key: 'status',
      render: (s: string) => <Tag color={statusColors[s]}>{statusLabels[s]}</Tag>,
    },
    { title: '审批人', dataIndex: 'reviewer_name', key: 'reviewer_name' },
    { title: '审批备注', dataIndex: 'review_comment', key: 'review_comment', ellipsis: true },
    {
      title: '操作', key: 'action',
      render: (_: any, record: any) => record.status === 'pending' ? (
        <Space>
          <Button size="small" type="primary" onClick={() => { setCurrentAction({ id: record.id, action: 'approve' }); setCommentModalOpen(true); }}>通过</Button>
          <Button size="small" danger onClick={() => { setCurrentAction({ id: record.id, action: 'reject' }); setCommentModalOpen(true); }}>拒绝</Button>
        </Space>
      ) : '-',
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>审批管理</h2>
        <Select allowClear placeholder="筛选状态" style={{ width: 150 }} value={statusFilter} onChange={(v) => { setStatusFilter(v); setPage(1); }}
          options={[{ label: '待审批', value: 'pending' }, { label: '已通过', value: 'approved' }, { label: '已拒绝', value: 'rejected' }]} />
      </div>
      <Table rowKey="id" columns={columns} dataSource={items} pagination={{ current: page, total, pageSize: 20, onChange: setPage }} />
      <Modal title="审批备注" open={commentModalOpen} onOk={handleAction} onCancel={() => { setCommentModalOpen(false); setCurrentAction(null); setComment(''); }}>
        <Input.TextArea rows={3} value={comment} onChange={(e) => setComment(e.target.value)} placeholder="审批备注（可选）" />
      </Modal>
    </div>
  );
}
