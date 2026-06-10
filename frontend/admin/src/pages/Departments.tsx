import { useEffect, useState } from 'react';
import { Tree, Button, Card, message, Spin } from 'antd';
import { departmentApi } from '../api';

export default function Departments() {
  const [treeData, setTreeData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const loadTree = async () => {
    setLoading(true);
    try {
      const res: any = await departmentApi.getTree();
      setTreeData(buildTree(res.data || []));
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setLoading(true);
    try {
      await departmentApi.sync();
      message.success('同步成功');
      loadTree();
    } catch {
      message.error('同步失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadTree(); }, []);

  const buildTree = (data: any[]): any[] =>
    data.map((item) => ({
      title: item.name,
      key: item.id,
      children: item.children ? buildTree(item.children) : [],
    }));

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>部门管理</h2>
        <Button type="primary" onClick={handleSync} loading={loading}>同步飞书组织架构</Button>
      </div>
      <Card>
        <Spin spinning={loading}>
          {treeData.length > 0 ? <Tree treeData={treeData} defaultExpandAll /> : <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>暂无部门数据，请点击"同步飞书组织架构"</div>}
        </Spin>
      </Card>
    </div>
  );
}
