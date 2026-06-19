import { api } from "./client";
import type { SymbolInfo, DailyBar, DashboardSummary } from "../types";

export const getSymbols = (market?: string) =>
  api.get<{ symbols: SymbolInfo[] }>(`/data/symbols${market ? `?market=${market}` : ""}`);

export const getBars = (symbol: string, start: string, end: string) =>
  api.get<{ bars: DailyBar[] }>(`/data/bars/${symbol}?start=${start}&end=${end}`);

export const getStrategies = () =>
  api.get<{ strategies: string[] }>("/strategies");

export const getDashboard = () =>
  api.get<DashboardSummary>("/dashboard/summary");

export const getOrders = () =>
  api.get<{ orders: unknown[] }>("/orders");
