import { useState, useEffect } from 'react';
import { Card, Form, Select, Input, Button, message } from 'antd';
import { skillApi, toolApi, permissionApi } from '../api';

export default function ApplyPermission() {
  const [skills, setSkills] = useState<any[]>([]);
  const [tools, setTools] = useState<any[]>([]);
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Promise.all([
      skillApi.getList({ page: 1, page_size: 100 }),
      toolApi.getList({ page: 1, page_size: 100 }),
    ]).then(([skillsRes, toolsRes]: any[]) => {
      setSkills(skillsRes.data?.items || []);
      setTools(toolsRes.data?.items || []);
    });
  }, []);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      await permissionApi.createRequest({
        type: values.type,
        target_id: values.target_id,
        reason: values.reason,
      });
      message.success('权限申请已提交');
      form.resetFields();
    } catch (e: any) {
      message.error(e?.message || '申请失败');
    } finally {
      setLoading(false);
    }
  };

  const type = Form.useWatch('type', form);

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>权限申请</h2>
      <Card style={{ maxWidth: 600 }}>
        <Form form={form} onFinish={handleSubmit} layout="vertical">
          <Form.Item name="type" label="申请类型" rules={[{ required: true }]}>
            <Select options={[{ label: 'Skill', value: 'skill' }, { label: 'Tool', value: 'tool' }]} placeholder="选择类型" />
          </Form.Item>
          <Form.Item name="target_id" label="目标" rules={[{ required: true }]}>
            <Select
              showSearch
              optionFilterProp="label"
              placeholder="选择目标"
              options={
                type === 'skill'
                  ? skills.map((s) => ({ label: s.name, value: s.id }))
                  : tools.map((t) => ({ label: `${t.name}${t.skill_name ? ` (${t.skill_name})` : ''}`, value: t.id }))
              }
            />
          </Form.Item>
          <Form.Item name="reason" label="申请理由">
            <Input.TextArea rows={3} placeholder="请说明申请理由" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>提交申请</Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
