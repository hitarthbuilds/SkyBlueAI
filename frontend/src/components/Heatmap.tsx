import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

interface HeatmapProps {
  data?: number[][];
}

const sampleData: number[][] = Array.from({ length: 8 }).map(() =>
  Array.from({ length: 12 }).map(() => Math.floor(Math.random() * 9))
);

export default function Heatmap({ data = sampleData }: HeatmapProps) {
  const ref = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (!ref.current) return;

    const width = 420;
    const height = 260;
    const rows = data.length;
    const cols = data[0]?.length ?? 0;

    const svg = d3.select(ref.current);
    svg.selectAll("*").remove();

    if (rows === 0 || cols === 0) {
      return;
    }

    const maxVal = d3.max(data.flat()) ?? 1;
    const color = d3.scaleLinear<string>()
      .domain([0, maxVal])
      .range(["#0b1c2f", "#2ab7ff"]);

    const cellW = width / cols;
    const cellH = height / rows;

    svg
      .attr("viewBox", `0 0 ${width} ${height}`)
      .style("width", "100%")
      .style("height", "100%");

    const g = svg.append("g");

    data.forEach((row, y) => {
      row.forEach((val, x) => {
        g.append("rect")
          .attr("x", x * cellW)
          .attr("y", y * cellH)
          .attr("width", cellW - 2)
          .attr("height", cellH - 2)
          .attr("rx", 4)
          .attr("fill", color(val));
      });
    });
  }, [data]);

  return (
    <div className="glass rounded-2xl p-4 border border-white/10">
      <h3 className="text-sm font-semibold text-white">Opponent Weak Zones</h3>
      <p className="text-xs text-slate-300/70 mt-1">Heat intensity by zone</p>
      <div className="mt-4">
        <svg ref={ref} />
      </div>
    </div>
  );
}
