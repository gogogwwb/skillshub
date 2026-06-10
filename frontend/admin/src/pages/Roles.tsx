import { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Tag, Space, message, Checkbox } from 'antd';
import { roleApi, skillApi, toolApi } from '../api';

export default function Roles() {
  const [roles, setRoles] = useState<any[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [permModalOpen, setPermModalOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<any>(null);
  const [allSkills, setAllSkills] = useState<any[]>([]);
  const [allTools, setAllTools] = useState<any[]>([]);
  const [selectedSkills, setSelectedSkills] = useState<number[]>([]);
  const [selectedTools, setSelectedTools] = useState<number[]>([]);
  const [form] = Form.useForm();

  const loadRoles = async () => {
    const res: any = await roleApi.getList();
    setRoles(res.data || []);
  };

  const loadAllResources = async () => {
    const [skillsRes, toolsRes]: any[] = await Promise.all([
      skillApi.getList({ page: 1, page_size: 100 }),
      toolApi.getList({ page: 1, page_size: 100 }),
    ]);
    setAllSkills(skillsRes.data?.items || []);
    setAllTools(toolsRes.data?.items || []);
  };

  useEffect(() => { loadRoles(); loadAllResources(); }, []);

  const handleCreate = async (values: any) => {
    if (editingRole) {
      await roleApi.update(editingRole.id, values);
      message.success('角色更新成功');
    } else {
      await roleApi.create(values);
      message.success('角色创建成功');
    }
    setModalOpen(false);
    setEditingRole(null);
    form.resetFields();
    loadRoles();
  };

  const handleDelete = async (id: number) => {
    await roleApi.delete(id);
    message.success('角色删除成功');
    loadRoles();
  };

  const handlePermSave = async () => {
    if (!editingRole) return;
    await Promise.all([
      roleApi.assignSkills(editingRole.id, selectedSkills),
      roleApi.assignTools(editingRole.id, selectedTools),
    ]);
    message.success('权限更新成功');
    setPermModalOpen(false);
    loadRoles();
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '角色名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description' },
    { title: '用户数', dataIndex: 'user_count', key: 'user_count', width: 80 },
    {
      title: 'Skills', dataIndex: 'skills', key: 'skills',
      render: (skills: any[]) => skills?.map((s) => <Tag key={s.id} color="blue">{s.name}</Tag>),
    },
    {
      title: 'Tools', dataIndex: 'tools', key: 'tools',
      render: (tools: any[]) => tools?.map((t) => <Tag key={t.id} color="green">{t.name}</Tag>),
    },
    {
      title: '操作', key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button size="small" onClick={() => { setEditingRole(record); form.setFieldsValue(record); setModalOpen(true); }}>编辑</Button>
          <Button size="small" type="primary" onClick={() => {
            setEditingRole(record);
            setSelectedSkills(record.skills?.map((s: any) => s.id) || []);
            setSelectedTools(record.tools?.map((t: any) => t.id) || []);
            setPermModalOpen(true);
          }}>权限</Button>
          <Button size="small" danger onClick={() => handleDelete(record.id)}>删除</Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>角色管理</h2>
        <Button type="primary" onClick={() => { setEditingRole(null); form.resetFields(); setModalOpen(true); }}>新建角色</Button>
      </div>
      <Table rowKey="id" columns={columns} dataSource={roles} pagination={false} />

      <Modal title={editingRole ? '编辑角色' : '新建角色'} open={modalOpen} onCancel={() => { setModalOpen(false); setEditingRole(null); }} onOk={() => form.submit()}>
        <Form form={form} onFinish={handleCreate}>
          <Form.Item name="name" label="角色名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="description" label="描述"><Input.TextArea /></Form.Item>
        </Form>
      </Modal>

      <Modal title={`权限分配 - ${editingRole?.name}`} open={permModalOpen} onCancel={() => setPermModalOpen(false)} onOk={handlePermSave} width={600}>
        <h4>Skills 权限</h4>
        <Checkbox.Group value={selectedSkills} onChange={(v) => setSelectedSkills(v as number[])}>
          {allSkills.map((s) => <Checkbox key={s.id} value={s.id}>{s.name}</Checkbox>)}
        </Checkbox.Group>
        <h4 style={{ marginTop: 16 }}>Tools 权限</h4>
        <Checkbox.Group value={selectedTools} onChange={(v) => setSelectedTools(v as number[])}>
          {allTools.map((t) => <Checkbox key={t.id} value={t.id}>{t.name}</Checkbox>)}
        </Checkbox.Group>
      </Modal>
    </div>
  );
}
