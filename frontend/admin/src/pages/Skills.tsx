import { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Tag, Space, message } from 'antd';
import { skillApi } from '../api';

export default function Skills() {
  const [skills, setSkills] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingSkill, setEditingSkill] = useState<any>(null);
  const [form] = Form.useForm();

  const loadSkills = async () => {
    const res: any = await skillApi.getList({ page, page_size: 20 });
    setSkills(res.data?.items || []);
    setTotal(res.data?.total || 0);
  };

  useEffect(() => { loadSkills(); }, [page]);

  const handleSubmit = async (values: any) => {
    if (editingSkill) {
      await skillApi.update(editingSkill.id, values);
      message.success('更新成功');
    } else {
      await skillApi.create(values);
      message.success('创建成功');
    }
    setModalOpen(false);
    setEditingSkill(null);
    form.resetFields();
    loadSkills();
  };

  const handleDelete = async (id: number) => {
    await skillApi.delete(id);
    message.success('删除成功');
    loadSkills();
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
    { title: '工具数', dataIndex: 'tool_count', key: 'tool_count', width: 80 },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 80,
      render: (s: string) => <Tag color={s === 'active' ? 'green' : 'red'}>{s === 'active' ? '启用' : '停用'}</Tag>,
    },
    {
      title: '操作', key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button size="small" onClick={() => { setEditingSkill(record); form.setFieldsValue(record); setModalOpen(true); }}>编辑</Button>
          <Button size="small" danger onClick={() => handleDelete(record.id)}>删除</Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Skills 管理</h2>
        <Button type="primary" onClick={() => { setEditingSkill(null); form.resetFields(); setModalOpen(true); }}>新建 Skill</Button>
      </div>
      <Table rowKey="id" columns={columns} dataSource={skills} pagination={{ current: page, total, pageSize: 20, onChange: setPage }} />
      <Modal title={editingSkill ? '编辑 Skill' : '新建 Skill'} open={modalOpen} onCancel={() => { setModalOpen(false); setEditingSkill(null); }} onOk={() => form.submit()}>
        <Form form={form} onFinish={handleSubmit}>
          <Form.Item name="name" label="名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="description" label="描述"><Input.TextArea /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
