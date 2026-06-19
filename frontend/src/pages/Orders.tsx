import { useEffect, useState } from "react";
import { Card, Table, Tag, Spin } from "antd";
import { getOrders } from "../api/endpoints";

export default function Orders() {
  const [orders, setOrders] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getOrders().then((res) => setOrders(res.orders)).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" />;

  return (
    <Card title="订单管理">
      <Table
        dataSource={orders as object[]} rowKey="id"
        columns={[
          { title: "订单ID", dataIndex: "id" },
          { title: "标的", dataIndex: "symbol" },
          { title: "方向", dataIndex: "direction", render: (v: string) => (
            <Tag color={v === "BUY" ? "red" : "green"}>{v}</Tag>
          )},
          { title: "数量", dataIndex: "quantity" },
          { title: "价格", dataIndex: "price" },
          { title: "状态", dataIndex: "status", render: (v: string) => (
            <Tag color={v === "filled" ? "green" : v === "pending" ? "orange" : "default"}>{v}</Tag>
          )},
        ]}
      />
    </Card>
  );
}
