import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Strategies from "./pages/Strategies";
import Backtest from "./pages/Backtest";
import Orders from "./pages/Orders";
import Market from "./pages/Market";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/market" element={<Market />} />
        <Route path="/strategies" element={<Strategies />} />
        <Route path="/backtest" element={<Backtest />} />
        <Route path="/orders" element={<Orders />} />
      </Route>
    </Routes>
  );
}
