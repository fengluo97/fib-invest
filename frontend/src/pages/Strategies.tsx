import { useEffect, useState } from "react";
import { Card, Table, Tag, Spin, Button } from "antd";
import { getStrategies } from "../api/endpoints";

export default function Strategies() {
  const [strategies, setStrategies] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStrategies().then((res) => setStrategies(res.strategies)).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" />;

  return (
    <div>
      <Card title="策略管理" extra={<Button type="primary">新建策略</Button>}>
        <Table
          dataSource={strategies.map((s) => ({ name: s, type: s, status: "stopped" }))}
          rowKey="name"
          columns={[
            { title: "策略名称", dataIndex: "name" },
            { title: "类型", dataIndex: "type", render: (v: string) => <Tag>{v}</Tag> },
            { title: "状态", dataIndex: "status", render: (v: string) => (
              <Tag color={v === "running" ? "green" : "default"}>{v}</Tag>
            )},
            { title: "操作", render: () => <Button size="small">启动</Button> },
          ]}
        />
      </Card>
    </div>
  );
}
