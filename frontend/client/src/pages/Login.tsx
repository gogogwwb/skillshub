import { Button, Card, Typography, Input, Form, Divider, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api';
import { useAuthStore } from '../store/auth';

const { Title, Text } = Typography;

export default function Login() {
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();

  const handleFeishuLogin = async () => {
    try {
      const res: any = await authApi.getFeishuLoginUrl();
      if (res.data?.url) {
        window.location.href = res.data.url;
      }
    } catch (e) {
      console.error('Login failed', e);
    }
  };

  const handleDevLogin = async (values: { username: string }) => {
    try {
      const res: any = await authApi.devLogin({ username: values.username, is_admin: false });
      if (res.data?.access_token) {
        setAuth(res.data.access_token, {
          id: res.data.user_id,
          name: res.data.name,
          is_admin: res.data.is_admin,
        });
        message.success(`欢迎，${res.data.name}！`);
        navigate('/');
      }
    } catch (e: any) {
      message.error(e?.response?.data?.message || '登录失败');
    }
  };

  const params = new URLSearchParams(window.location.search);
  const code = params.get('code');
  if (code) {
    authApi.feishuCallback(code).then((res: any) => {
      if (res.data?.access_token) {
        setAuth(res.data.access_token, {
          id: res.data.user_id,
          name: res.data.name,
          is_admin: res.data.is_admin,
        });
        navigate('/');
      }
    });
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f0f2f5' }}>
      <Card style={{ width: 400, textAlign: 'center' }}>
        <Title level={3}>ToolHub</Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
          AI Skills & Tools 权限管理系统
        </Text>

        <Button type="primary" size="large" block onClick={handleFeishuLogin}>
          飞书登录
        </Button>

        <Divider plain>开发模式</Divider>

        <Form onFinish={handleDevLogin} layout="inline" style={{ justifyContent: 'center' }}>
          <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]} style={{ marginBottom: 0 }}>
            <Input placeholder="用户名" style={{ width: 150 }} />
          </Form.Item>
          <Form.Item style={{ marginBottom: 0 }}>
            <Button htmlType="submit">快速登录</Button>
          </Form.Item>
        </Form>

        <Text type="secondary" style={{ display: 'block', marginTop: 12, fontSize: 12 }}>
          已有测试账号: 管理员 / 张三 / 李四
        </Text>
      </Card>
    </div>
  );
}
