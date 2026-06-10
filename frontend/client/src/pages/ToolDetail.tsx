import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Tag, Button } from 'antd';
import { toolApi } from '../api';

export default function ToolDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tool, setTool] = useState<any>(null);

  useEffect(() => {
    toolApi.getDetail(Number(id)).then((res: any) => setTool(res.data));
  }, [id]);

  if (!tool) return <div>加载中...</div>;

  return (
    <div>
      <Button onClick={() => navigate('/tools')} style={{ marginBottom: 16 }}>返回列表</Button>
      <Card>
        <Descriptions title={tool.name}>
          <Descriptions.Item label="描述">{tool.description || '-'}</Descriptions.Item>
          <Descriptions.Item label="所属Skill">{tool.skill_name || '-'}</Descriptions.Item>
          <Descriptions.Item label="端点">{tool.endpoint || '-'}</Descriptions.Item>
          <Descriptions.Item label="方法">{tool.method || '-'}</Descriptions.Item>
          <Descriptions.Item label="状态"><Tag color={tool.status === 'active' ? 'green' : 'red'}>{tool.status}</Tag></Descriptions.Item>
          <Descriptions.Item label="权限">{tool.has_permission ? <Tag color="green">已授权</Tag> : <Tag color="orange">未授权</Tag>}</Descriptions.Item>
        </Descriptions>
        {tool.parameters && (
          <div style={{ marginTop: 16 }}>
            <h4>参数定义</h4>
            <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4 }}>{JSON.stringify(tool.parameters, null, 2)}</pre>
          </div>
        )}
      </Card>
    </div>
  );
}
