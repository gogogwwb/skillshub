import { useEffect, useState } from 'react';
import { Table, Tag, Button, message } from 'antd';
import { permissionApi } from '../api';

const statusColors: Record<string, string> = { pending: 'orange', approved: 'green', rejected: 'red', cancelled: 'default' };
const statusLabels: Record<string, string> = { pending: '待审批', approved: '已通过', rejected: '已拒绝', cancelled: '已撤销' };

export default function MyRequests() {
  const [items, setItems] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);

  const loadData = async () => {
    const res: any = await permissionApi.getMyRequests({ page, page_size: 20 });
    setItems(res.data?.items || []);
    setTotal(res.data?.total || 0);
  };

  useEffect(() => { loadData(); }, [page]);

  const handleCancel = async (id: number) => {
    try {
      await permissionApi.cancelRequest(id);
      message.success('已撤销');
      loadData();
    } catch (e: any) {
      message.error(e?.message || '操作失败');
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '类型', dataIndex: 'type', key: 'type', render: (t: string) => <Tag>{t}</Tag> },
    { title: '目标', dataIndex: 'target_name', key: 'target_name' },
    { title: '理由', dataIndex: 'reason', key: 'reason', ellipsis: true },
    {
      title: '状态', dataIndex: 'status', key: 'status',
      render: (s: string) => <Tag color={statusColors[s]}>{statusLabels[s]}</Tag>,
    },
    { title: '审批备注', dataIndex: 'review_comment', key: 'review_comment', ellipsis: true },
    {
      title: '操作', key: 'action', width: 80,
      render: (_: any, record: any) => record.status === 'pending' ? (
        <Button size="small" danger onClick={() => handleCancel(record.id)}>撤销</Button>
      ) : '-',
    },
  ];

  return (
    <div>
      <h2 style={{ marginBottom: 16 }}>我的申请</h2>
      <Table rowKey="id" columns={columns} dataSource={items} pagination={{ current: page, total, pageSize: 20, onChange: setPage }} />
    </div>
  );
}
