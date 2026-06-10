import { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, Tag, Space, message } from 'antd';
import { toolApi, skillApi } from '../api';

export default function Tools() {
  const [tools, setTools] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [skills, setSkills] = useState<any[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingTool, setEditingTool] = useState<any>(null);
  const [form] = Form.useForm();

  const loadTools = async () => {
    const res: any = await toolApi.getList({ page, page_size: 20 });
    setTools(res.data?.items || []);
    setTotal(res.data?.total || 0);
  };

  const loadSkills = async () => {
    const res: any = await skillApi.getList({ page: 1, page_size: 100 });
    setSkills(res.data?.items || []);
  };

  useEffect(() => { loadTools(); loadSkills(); }, [page]);

  const handleSubmit = async (values: any) => {
    if (editingTool) {
      await toolApi.update(editingTool.id, values);
      message.success('更新成功');
    } else {
      await toolApi.create(values);
      message.success('创建成功');
    }
    setModalOpen(false);
    setEditingTool(null);
    form.resetFields();
    loadTools();
  };

  const handleDelete = async (id: number) => {
    await toolApi.delete(id);
    message.success('删除成功');
    loadTools();
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: '所属Skill', dataIndex: 'skill_name', key: 'skill_name' },
    { title: '端点', dataIndex: 'endpoint', key: 'endpoint', ellipsis: true },
    { title: '方法', dataIndex: 'method', key: 'method', width: 80 },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 80,
      render: (s: string) => <Tag color={s === 'active' ? 'green' : 'red'}>{s === 'active' ? '启用' : '停用'}</Tag>,
    },
    {
      title: '操作', key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button size="small" onClick={() => { setEditingTool(record); form.setFieldsValue(record); setModalOpen(true); }}>编辑</Button>
          <Button size="small" danger onClick={() => handleDelete(record.id)}>删除</Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Tools 管理</h2>
        <Button type="primary" onClick={() => { setEditingTool(null); form.resetFields(); setModalOpen(true); }}>新建 Tool</Button>
      </div>
      <Table rowKey="id" columns={columns} dataSource={tools} pagination={{ current: page, total, pageSize: 20, onChange: setPage }} />
      <Modal title={editingTool ? '编辑 Tool' : '新建 Tool'} open={modalOpen} onCancel={() => { setModalOpen(false); setEditingTool(null); }} onOk={() => form.submit()} width={600}>
        <Form form={form} onFinish={handleSubmit}>
          <Form.Item name="name" label="名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="description" label="描述"><Input.TextArea /></Form.Item>
          <Form.Item name="skill_id" label="所属Skill">
            <Select allowClear placeholder="选择Skill" options={skills.map((s) => ({ label: s.name, value: s.id }))} />
          </Form.Item>
          <Form.Item name="endpoint" label="端点"><Input placeholder="https://..." /></Form.Item>
          <Form.Item name="method" label="方法">
            <Select options={[{ label: 'POST', value: 'POST' }, { label: 'GET', value: 'GET' }]} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
