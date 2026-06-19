import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { Layout as AntLayout, Menu } from "antd";
import { DashboardOutlined, CodeOutlined, BarChartOutlined, OrderedListOutlined, StockOutlined } from "@ant-design/icons";

const { Header, Content } = AntLayout;

const menuItems = [
  { key: "/", icon: <DashboardOutlined />, label: "看板" },
  { key: "/market", icon: <StockOutlined />, label: "行情" },
  { key: "/strategies", icon: <CodeOutlined />, label: "策略" },
  { key: "/backtest", icon: <BarChartOutlined />, label: "回测" },
  { key: "/orders", icon: <OrderedListOutlined />, label: "订单" },
];

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <AntLayout style={{ minHeight: "100vh" }}>
      <Header style={{ display: "flex", alignItems: "center" }}>
        <div style={{ color: "white", fontSize: 18, fontWeight: "bold", marginRight: 32 }}>FIB-Invest</div>
        <Menu
          theme="dark" mode="horizontal" selectedKeys={[location.pathname]}
          items={menuItems} onClick={({ key }) => navigate(key)}
          style={{ flex: 1 }}
        />
      </Header>
      <Content style={{ padding: 24 }}><Outlet /></Content>
    </AntLayout>
  );
}
