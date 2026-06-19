import { useEffect, useRef } from "react";

interface EquityChartProps {
  data: { time: string; value: number }[];
}

export default function EquityChart({ data }: EquityChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return;
    const el = document.createElement("div");
    el.style.width = "100%";
    el.style.height = "100%";
    el.style.display = "flex";
    el.style.alignItems = "center";
    el.style.justifyContent = "center";
    el.style.color = "#999";
    el.innerText = `权益曲线: ${data.length} 个数据点`;
    containerRef.current.innerHTML = "";
    containerRef.current.appendChild(el);
  }, [data]);

  return <div ref={containerRef} style={{ width: "100%", height: 400 }} />;
}
