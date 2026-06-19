import { Card, Button, Form, Input, DatePicker, Select } from "antd";
import { PlayCircleOutlined } from "@ant-design/icons";

export default function Backtest() {
  return (
    <Card title="策略回测">
      <Form layout="inline" style={{ marginBottom: 16 }}>
        <Form.Item label="策略"><Select style={{ width: 160 }} options={[{ value: "ma_cross", label: "均线交叉" }]} /></Form.Item>
        <Form.Item label="标的"><Input placeholder="000001.sz" /></Form.Item>
        <Form.Item label="开始"><DatePicker /></Form.Item>
        <Form.Item label="结束"><DatePicker /></Form.Item>
        <Form.Item><Button type="primary" icon={<PlayCircleOutlined />}>运行回测</Button></Form.Item>
      </Form>
      <div style={{ height: 400, background: "#f5f5f5", display: "flex", alignItems: "center", justifyContent: "center" }}>
        回测结果图表区域
      </div>
    </Card>
  );
}
