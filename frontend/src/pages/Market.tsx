import { useEffect, useRef, useState } from "react";
import { Card, Select, DatePicker, Space, Spin, message } from "antd";
import { createChart, ColorType } from "lightweight-charts";
import dayjs from "dayjs";

interface SymbolOption {
  value: string;
  label: string;
}

export default function Market() {
  const [symbols, setSymbols] = useState<SymbolOption[]>([]);
  const [symbol, setSymbol] = useState("000001");
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(6, "month"),
    dayjs(),
  ]);

  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<any>(null);

  // Load symbol list
  useEffect(() => {
    fetch("/api/data/symbols?market=sh")
      .then((r) => r.json())
      .then((data) => {
        const opts: SymbolOption[] = (data.symbols || []).map(
          (s: { code: string; name: string; market: string }) => ({
            value: s.code,
            label: `${s.code} ${s.name} (${s.market.toUpperCase()})`,
          })
        );
        // Add SZ stocks too
        fetch("/api/data/symbols?market=sz")
          .then((r) => r.json())
          .then((data2) => {
            const sz = (data2.symbols || []).map(
              (s: { code: string; name: string; market: string }) => ({
                value: s.code,
                label: `${s.code} ${s.name} (${s.market.toUpperCase()})`,
              })
            );
            setSymbols([...opts, ...sz]);
          });
      })
      .catch(() => message.error("Failed to load symbol list"));
  }, []);

  // Fetch bars and render chart
  useEffect(() => {
    if (!symbol || !dateRange) return;
    setLoading(true);

    const start = dateRange[0].format("YYYY-MM-DD");
    const end = dateRange[1].format("YYYY-MM-DD");

    fetch(`/api/data/bars/${symbol}?start=${start}&end=${end}`)
      .then((r) => r.json())
      .then((data) => {
        const bars = data.bars || [];
        if (bars.length === 0) {
          message.warning("No data for this period");
          setLoading(false);
          return;
        }
        renderChart(bars);
        setLoading(false);
      })
      .catch(() => {
        message.error("Failed to fetch market data");
        setLoading(false);
      });
  }, [symbol, dateRange]);

  function renderChart(bars: any[]) {
    if (!chartRef.current) return;

    // Destroy previous chart
    if (chartInstance.current) {
      chartInstance.current.remove();
      chartInstance.current = null;
    }

    const chart = createChart(chartRef.current, {
      width: chartRef.current.clientWidth,
      height: 500,
      layout: {
        background: { type: ColorType.Solid, color: "#ffffff" },
        textColor: "#333",
      },
      grid: {
        vertLines: { color: "#f0f0f0" },
        horzLines: { color: "#f0f0f0" },
      },
      crosshair: { mode: 0 },
      rightPriceScale: { borderColor: "#d9d9d9" },
      timeScale: { borderColor: "#d9d9d9", timeVisible: true },
    });

    // Candlestick series
    const candleSeries = chart.addCandlestickSeries({
      upColor: "#ef4444",
      downColor: "#22c55e",
      borderUpColor: "#ef4444",
      borderDownColor: "#22c55e",
      wickUpColor: "#ef4444",
      wickDownColor: "#22c55e",
    });

    const candleData = bars.map((b: any) => ({
      time: b.date,
      open: b.open,
      high: b.high,
      low: b.low,
      close: b.close,
    }));
    candleSeries.setData(candleData);

    // Volume histogram
    const volumeSeries = chart.addHistogramSeries({
      color: "#d1d5db",
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    });
    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    const volumeData = bars.map((b: any) => ({
      time: b.date,
      value: b.volume,
      color: b.close >= b.open ? "rgba(239,68,68,0.3)" : "rgba(34,197,94,0.3)",
    }));
    volumeSeries.setData(volumeData);

    chart.timeScale().fitContent();
    chartInstance.current = chart;

    // Handle resize
    const handleResize = () => {
      if (chartRef.current && chartInstance.current) {
        chartInstance.current.applyOptions({
          width: chartRef.current.clientWidth,
        });
      }
    };
    window.addEventListener("resize", handleResize);
  }

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Select
            showSearch
            value={symbol}
            onChange={setSymbol}
            options={symbols}
            placeholder="Search stock symbol..."
            style={{ width: 320 }}
            filterOption={(input, option) =>
              (option?.label ?? "").toLowerCase().includes(input.toLowerCase())
            }
          />
          <DatePicker.RangePicker
            value={dateRange}
            onChange={(dates) => {
              if (dates && dates[0] && dates[1]) setDateRange([dates[0], dates[1]]);
            }}
            allowClear={false}
          />
        </Space>
      </Card>

      <Card>
        {loading ? (
          <Spin
            size="large"
            style={{ display: "block", textAlign: "center", padding: 100 }}
          />
        ) : (
          <div ref={chartRef} style={{ width: "100%", minHeight: 500 }} />
        )}
      </Card>
    </div>
  );
}
