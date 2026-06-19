import { useEffect, useState } from "react";
import { Card, Row, Col, Statistic, Table, Spin } from "antd";
import { ArrowUpOutlined, ArrowDownOutlined } from "@ant-design/icons";
import { getDashboard } from "../api/endpoints";
import type { DashboardSummary } from "../types";

export default function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" />;

  const { account, positions, daily_pnl } = data!;
  const totalPnl = account.total_value - account.cash;

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}><Card><Statistic title="总资产" value={account.total_value.toLocaleString()} precision={2} suffix="¥" /></Card></Col>
        <Col span={6}><Card><Statistic title="可用资金" value={account.cash.toLocaleString()} precision={2} suffix="¥" /></Card></Col>
        <Col span={6}>
          <Card>
            <Statistic title="持仓盈亏" value={totalPnl} precision={2}
              prefix={totalPnl >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              valueStyle={{ color: totalPnl >= 0 ? "#3f8600" : "#cf1322" }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="当日盈亏" value={daily_pnl} precision={2}
              prefix={daily_pnl >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              valueStyle={{ color: daily_pnl >= 0 ? "#3f8600" : "#cf1322" }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="持仓明细">
        <Table
          dataSource={positions} rowKey="symbol"
          columns={[
            { title: "代码", dataIndex: "symbol" },
            { title: "数量", dataIndex: "quantity" },
            { title: "成本价", dataIndex: "avg_cost", render: (v: number) => v.toFixed(2) },
            { title: "现价", dataIndex: "current_price", render: (v: number) => v.toFixed(2) },
            { title: "市值", dataIndex: "market_value", render: (v: number) => v.toLocaleString() },
            { title: "盈亏", dataIndex: "pnl", render: (v: number) => (
              <span style={{ color: v >= 0 ? "#3f8600" : "#cf1322" }}>{v.toFixed(2)}</span>
            )},
          ]}
        />
      </Card>
    </div>
  );
}
