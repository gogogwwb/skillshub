import { useEffect, useState } from 'react';
import { Table, Button, Tag, Modal, Select, Space, Input, message } from 'antd';
import { userApi, roleApi } from '../api';

export default function Users() {
  const [users, setUsers] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [keyword, setKeyword] = useState('');
  const [roles, setRoles] = useState<any[]>([]);
  const [roleModalOpen, setRoleModalOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [selectedRoles, setSelectedRoles] = useState<number[]>([]);

  const loadUsers = async () => {
    const res: any = await userApi.getList({ page, page_size: 20, keyword: keyword || undefined });
    setUsers(res.data?.items || []);
    setTotal(res.data?.total || 0);
  };

  const loadRoles = async () => {
    const res: any = await roleApi.getList();
    setRoles(res.data || []);
  };

  useEffect(() => { loadUsers(); }, [page]);
  useEffect(() => { loadRoles(); }, []);

  const handleRoleAssign = async () => {
    if (!currentUser) return;
    await userApi.updateRoles(currentUser.id, selectedRoles);
    message.success('角色更新成功');
    setRoleModalOpen(false);
    loadUsers();
  };

  const handleStatusToggle = async (user: any) => {
    const newStatus = user.status === 'active' ? 'inactive' : 'active';
    await userApi.updateStatus(user.id, newStatus);
    message.success('状态更新成功');
    loadUsers();
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '姓名', dataIndex: 'name', key: 'name' },
    { title: '邮箱', dataIndex: 'email', key: 'email' },
    { title: '部门', dataIndex: 'department_name', key: 'department_name' },
    {
      title: '角色', dataIndex: 'roles', key: 'roles',
      render: (roles: any[]) => roles?.map((r) => <Tag key={r.id}>{r.name}</Tag>),
    },
    {
      title: '状态', dataIndex: 'status', key: 'status',
      render: (status: string) => <Tag color={status === 'active' ? 'green' : 'red'}>{status === 'active' ? '启用' : '禁用'}</Tag>,
    },
    {
      title: '管理员', dataIndex: 'is_admin', key: 'is_admin',
      render: (v: boolean) => v ? <Tag color="blue">是</Tag> : '-',
    },
    {
      title: '操作', key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button size="small" onClick={() => { setCurrentUser(record); setSelectedRoles(record.roles?.map((r: any) => r.id) || []); setRoleModalOpen(true); }}>分配角色</Button>
          <Button size="small" danger={record.status === 'active'} onClick={() => handleStatusToggle(record)}>
            {record.status === 'active' ? '禁用' : '启用'}
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>用户管理</h2>
        <Space>
          <Input.Search placeholder="搜索用户" onSearch={(v) => { setKeyword(v); setPage(1); loadUsers(); }} style={{ width: 200 }} />
        </Space>
      </div>
      <Table
        rowKey="id"
        columns={columns}
        dataSource={users}
        pagination={{ current: page, total, pageSize: 20, onChange: setPage }}
      />
      <Modal title="分配角色" open={roleModalOpen} onOk={handleRoleAssign} onCancel={() => setRoleModalOpen(false)}>
        <Select mode="multiple" style={{ width: '100%' }} value={selectedRoles} onChange={setSelectedRoles}
          options={roles.map((r) => ({ label: r.name, value: r.id }))} placeholder="选择角色" />
      </Modal>
    </div>
  );
}
