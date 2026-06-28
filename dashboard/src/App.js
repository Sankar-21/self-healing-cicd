import { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const STATUS_COLOR = {
  success: "#1D9E75",
  failure: "#D85A30",
  running: "#BA7517",
  unknown: "#888780",
};

const CATEGORY_COLOR = {
  test_failure: "#D85A30",
  dependency_missing: "#BA7517",
  build_error: "#D4537E",
  infra_flap: "#378ADD",
  auth_error: "#7F77DD",
  unknown: "#888780",
};

function StatCard({ label, value, color }) {
  return (
    <div
      style={{
        background: "var(--surface-1, #f9f9f8)",
        border: "1px solid #d3d1c7",
        borderRadius: 12,
        padding: "20px 24px",
        minWidth: 140,
        flex: 1,
      }}
    >
      <div style={{ fontSize: 13, color: "#5f5e5a", marginBottom: 6 }}>
        {label}
      </div>
      <div style={{ fontSize: 32, fontWeight: 500, color }}>{value}</div>
    </div>
  );
}

function Badge({ text, color }) {
  return (
    <span
      style={{
        background: color + "22",
        color,
        border: `1px solid ${color}55`,
        borderRadius: 6,
        padding: "2px 10px",
        fontSize: 12,
        fontWeight: 500,
      }}
    >
      {text}
    </span>
  );
}

export default function App() {
  const [runs, setRuns] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [runsRes, statsRes] = await Promise.all([
        fetch("http://localhost:8000/api/runs"),
        fetch("http://localhost:8000/api/stats"),
      ]);
      setRuns(await runsRes.json());
      setStats(await statsRes.json());
    } catch (e) {
      console.error("API error:", e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const chartData = runs
    .filter((r) => r.status === "failure")
    .reduce((acc, r) => {
      const found = acc.find((x) => x.name === r.category);
      if (found) found.count++;
      else acc.push({ name: r.category, count: 1 });
      return acc;
    }, []);

  return (
    <div
      style={{
        fontFamily: "sans-serif",
        maxWidth: 1100,
        margin: "0 auto",
        padding: "32px 24px",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 32,
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: 24, fontWeight: 500 }}>
            Self-Healing CI/CD
          </h1>
          <p style={{ margin: "4px 0 0", fontSize: 14, color: "#5f5e5a" }}>
            Pipeline monitor · Sankar-21/self-healing-cicd
          </p>
        </div>
        <button
          onClick={fetchData}
          style={{
            padding: "8px 18px",
            borderRadius: 8,
            border: "1px solid #d3d1c7",
            background: "#fff",
            cursor: "pointer",
            fontSize: 13,
          }}
        >
          ↻ Refresh
        </button>
      </div>

      {loading ? (
        <p style={{ color: "#888" }}>Loading pipeline data...</p>
      ) : (
        <>
          {/* Stat cards */}
          {stats && (
            <div
              style={{
                display: "flex",
                gap: 16,
                marginBottom: 32,
                flexWrap: "wrap",
              }}
            >
              <StatCard
                label="Total runs"
                value={stats.total}
                color="#2c2c2a"
              />
              <StatCard
                label="Successful"
                value={stats.success}
                color="#1D9E75"
              />
              <StatCard label="Failed" value={stats.failed} color="#D85A30" />
              <StatCard
                label="Health rate"
                value={`${stats.health_rate}%`}
                color="#378ADD"
              />
            </div>
          )}

          {/* Failure breakdown chart */}
          {chartData.length > 0 && (
            <div
              style={{
                background: "#f9f9f8",
                border: "1px solid #d3d1c7",
                borderRadius: 12,
                padding: 24,
                marginBottom: 32,
              }}
            >
              <h2 style={{ margin: "0 0 20px", fontSize: 16, fontWeight: 500 }}>
                Failure breakdown
              </h2>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={chartData}>
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {chartData.map((entry, i) => (
                      <Cell
                        key={i}
                        fill={CATEGORY_COLOR[entry.name] || "#888"}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Run table */}
          <div
            style={{
              background: "#f9f9f8",
              border: "1px solid #d3d1c7",
              borderRadius: 12,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                padding: "16px 24px",
                borderBottom: "1px solid #d3d1c7",
              }}
            >
              <h2 style={{ margin: 0, fontSize: 16, fontWeight: 500 }}>
                Recent runs
              </h2>
            </div>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: 13,
              }}
            >
              <thead>
                <tr style={{ background: "#f1efe8" }}>
                  {[
                    "Commit",
                    "Name",
                    "Branch",
                    "Status",
                    "Category",
                    "Confidence",
                    "Time",
                  ].map((h) => (
                    <th
                      key={h}
                      style={{
                        padding: "10px 16px",
                        textAlign: "left",
                        fontWeight: 500,
                        color: "#5f5e5a",
                      }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {runs.map((run, i) => (
                  <tr
                    key={run.id}
                    style={{
                      borderTop: "1px solid #e8e6df",
                      background: i % 2 === 0 ? "#fff" : "#fafaf8",
                    }}
                  >
                    <td style={{ padding: "10px 16px" }}>
                      <a
                        href={run.url}
                        target="_blank"
                        rel="noreferrer"
                        style={{ color: "#378ADD", fontFamily: "monospace" }}
                      >
                        {run.commit}
                      </a>
                    </td>
                    <td
                      style={{
                        padding: "10px 16px",
                        maxWidth: 220,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {run.name}
                    </td>
                    <td style={{ padding: "10px 16px", color: "#5f5e5a" }}>
                      {run.branch}
                    </td>
                    <td style={{ padding: "10px 16px" }}>
                      <Badge
                        text={run.status}
                        color={STATUS_COLOR[run.status] || "#888"}
                      />
                    </td>
                    <td style={{ padding: "10px 16px" }}>
                      {run.status === "failure" ? (
                        <Badge
                          text={run.category}
                          color={CATEGORY_COLOR[run.category] || "#888"}
                        />
                      ) : (
                        <span style={{ color: "#b4b2a9" }}>—</span>
                      )}
                    </td>
                    <td style={{ padding: "10px 16px", color: "#5f5e5a" }}>
                      {run.confidence > 0 ? `${run.confidence}%` : "—"}
                    </td>
                    <td
                      style={{
                        padding: "10px 16px",
                        color: "#888",
                        fontSize: 12,
                      }}
                    >
                      {new Date(run.updated_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
