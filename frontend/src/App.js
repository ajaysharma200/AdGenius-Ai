import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer
} from "recharts";

const API = "http://127.0.0.1:8000";
const COLORS = ["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"];

export default function App() {
  const [analytics, setAnalytics] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [form, setForm] = useState({
    platform: "Google Ads", campaign_type: "Search",
    industry: "SaaS", country: "India",
    impressions: 50000, clicks: 1500, CTR: 3.0,
    CPC: 2.5, ad_spend: 5000, conversions: 120, CPA: 41.67
  });

  useEffect(() => {
    axios.get(`${API}/analytics`)
      .then(res => { setAnalytics(res.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const handlePredict = async () => {
    const res = await axios.post(`${API}/predict`, form);
    setPrediction(res.data);
  };

  if (loading) return (
    <div style={styles.loader}>
      <h2 style={{ color: "#6366f1" }}>Loading AdGenius AI...</h2>
    </div>
  );

  return (
    <div style={styles.app}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.logo}>⚡ AdGenius AI</h1>
        <p style={styles.subtitle}>AI-Powered Marketing Campaign Optimization</p>
        <div style={styles.tabs}>
          {["dashboard", "analytics", "predict"].map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              style={activeTab === tab ? styles.activeTab : styles.tab}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div style={styles.content}>
        {/* DASHBOARD TAB */}
        {activeTab === "dashboard" && analytics && (
          <div>
            {/* KPI Cards */}
            <div style={styles.cards}>
              <KPICard title="Total Campaigns" value={analytics.total_campaigns} color="#6366f1" icon="📊" />
              <KPICard title="Total Spend" value={`$${(analytics.total_spend/1000000).toFixed(2)}M`} color="#ef4444" icon="💰" />
              <KPICard title="Total Revenue" value={`$${(analytics.total_revenue/1000000).toFixed(2)}M`} color="#10b981" icon="📈" />
              <KPICard title="Avg ROI" value={`${analytics.avg_roi}%`} color="#f59e0b" icon="🎯" />
            </div>

            {/* Platform Performance */}
            <div style={styles.chartBox}>
              <h3 style={styles.chartTitle}>Platform Performance - ROI Comparison</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analytics.platform_performance}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="platform" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={styles.tooltip} />
                  <Legend />
                  <Bar dataKey="avg_roi" fill="#6366f1" name="Avg ROI %" radius={[4,4,0,0]} />
                  <Bar dataKey="campaigns" fill="#06b6d4" name="Campaigns" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Monthly Trends */}
            <div style={styles.chartBox}>
              <h3 style={styles.chartTitle}>Monthly ROI Trend</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analytics.monthly_trends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="month" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={styles.tooltip} />
                  <Legend />
                  <Line type="monotone" dataKey="avg_roi" stroke="#6366f1" strokeWidth={2} dot={{ fill: "#6366f1" }} name="Avg ROI %" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* ANALYTICS TAB */}
        {activeTab === "analytics" && analytics && (
          <div>
            <div style={styles.grid2}>
              {/* Industry Performance */}
              <div style={styles.chartBox}>
                <h3 style={styles.chartTitle}>Industry ROI Analysis</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analytics.industry_performance} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis type="number" stroke="#94a3b8" />
                    <YAxis dataKey="industry" type="category" stroke="#94a3b8" width={80} />
                    <Tooltip contentStyle={styles.tooltip} />
                    <Bar dataKey="avg_roi" fill="#10b981" name="Avg ROI %" radius={[0,4,4,0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Platform Pie */}
              <div style={styles.chartBox}>
                <h3 style={styles.chartTitle}>Campaign Distribution by Platform</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={analytics.platform_performance} dataKey="campaigns"
                      nameKey="platform" cx="50%" cy="50%" outerRadius={100} label>
                      {analytics.platform_performance.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={styles.tooltip} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Platform Table */}
            <div style={styles.chartBox}>
              <h3 style={styles.chartTitle}>Platform Performance Summary</h3>
              <table style={styles.table}>
                <thead>
                  <tr>
                    {["Platform", "Campaigns", "Avg ROI %", "Total Spend", "Total Revenue"].map(h => (
                      <th key={h} style={styles.th}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {analytics.platform_performance.map((p, i) => (
                    <tr key={i} style={i % 2 === 0 ? styles.trEven : styles.trOdd}>
                      <td style={styles.td}>{p.platform}</td>
                      <td style={styles.td}>{p.campaigns}</td>
                      <td style={{ ...styles.td, color: "#10b981", fontWeight: "bold" }}>{p.avg_roi}%</td>
                      <td style={styles.td}>${p.total_spend?.toLocaleString()}</td>
                      <td style={styles.td}>${p.total_revenue?.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* PREDICT TAB */}
        {activeTab === "predict" && (
          <div style={styles.chartBox}>
            <h3 style={styles.chartTitle}>🤖 ROI Prediction Engine</h3>
            <div style={styles.grid2}>
              <div>
                {[
                  ["platform", "Platform", ["Google Ads", "Meta Ads", "TikTok Ads"]],
                  ["campaign_type", "Campaign Type", ["Search", "Video", "Shopping", "Display"]],
                  ["industry", "Industry", ["SaaS", "EdTech", "Fintech", "E-commerce", "Healthcare"]],
                  ["country", "Country", ["India", "USA", "UK", "Canada", "UAE", "Germany", "Australia"]],
                ].map(([key, label, options]) => (
                  <div key={key} style={styles.formGroup}>
                    <label style={styles.label}>{label}</label>
                    <select style={styles.input} value={form[key]}
                      onChange={e => setForm({ ...form, [key]: e.target.value })}>
                      {options.map(o => <option key={o}>{o}</option>)}
                    </select>
                  </div>
                ))}
              </div>
              <div>
                {[
                  ["impressions", "Impressions"],
                  ["clicks", "Clicks"],
                  ["CTR", "CTR (%)"],
                  ["CPC", "CPC ($)"],
                  ["ad_spend", "Ad Spend ($)"],
                  ["conversions", "Conversions"],
                  ["CPA", "CPA ($)"],
                ].map(([key, label]) => (
                  <div key={key} style={styles.formGroup}>
                    <label style={styles.label}>{label}</label>
                    <input type="number" style={styles.input} value={form[key]}
                      onChange={e => setForm({ ...form, [key]: parseFloat(e.target.value) })} />
                  </div>
                ))}
              </div>
            </div>

            <button onClick={handlePredict} style={styles.btn}>
              🚀 Predict ROI
            </button>

            {prediction && (
              <div style={styles.resultBox}>
                <h3 style={{ color: "#10b981", marginBottom: 16 }}>Prediction Results</h3>
                <div style={styles.cards}>
                  <KPICard title="Predicted ROI" value={`${prediction.predicted_roi}%`} color="#6366f1" icon="📈" />
                  <KPICard title="Campaign Success" value={prediction.campaign_success ? "✅ Yes" : "❌ No"} color="#10b981" icon="🎯" />
                  <KPICard title="Recommended Platform" value={prediction.recommended_platform} color="#f59e0b" icon="⚡" />
                  <KPICard title="Confidence" value={prediction.confidence} color="#06b6d4" icon="🔮" />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function KPICard({ title, value, color, icon }) {
  return (
    <div style={{ ...styles.card, borderTop: `3px solid ${color}` }}>
      <div style={styles.cardIcon}>{icon}</div>
      <div style={{ ...styles.cardValue, color }}>{value}</div>
      <div style={styles.cardTitle}>{title}</div>
    </div>
  );
}

const styles = {
  app: { minHeight: "100vh", background: "#0f172a", color: "#e2e8f0", fontFamily: "Inter, sans-serif" },
  loader: { display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", background: "#0f172a" },
  header: { background: "#1e293b", padding: "24px 32px", borderBottom: "1px solid #334155" },
  logo: { margin: 0, fontSize: 28, color: "#6366f1", fontWeight: 800 },
  subtitle: { margin: "4px 0 16px", color: "#94a3b8", fontSize: 14 },
  tabs: { display: "flex", gap: 8 },
  tab: { padding: "8px 20px", border: "1px solid #334155", borderRadius: 8, background: "transparent", color: "#94a3b8", cursor: "pointer", fontSize: 14 },
  activeTab: { padding: "8px 20px", border: "none", borderRadius: 8, background: "#6366f1", color: "white", cursor: "pointer", fontSize: 14, fontWeight: 600 },
  content: { padding: 32, maxWidth: 1200, margin: "0 auto" },
  cards: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginBottom: 24 },
  card: { background: "#1e293b", borderRadius: 12, padding: 20, textAlign: "center" },
  cardIcon: { fontSize: 28, marginBottom: 8 },
  cardValue: { fontSize: 24, fontWeight: 800, marginBottom: 4 },
  cardTitle: { color: "#94a3b8", fontSize: 13 },
  chartBox: { background: "#1e293b", borderRadius: 12, padding: 24, marginBottom: 24 },
  chartTitle: { margin: "0 0 16px", color: "#e2e8f0", fontSize: 16, fontWeight: 600 },
  tooltip: { background: "#1e293b", border: "1px solid #334155", borderRadius: 8 },
  grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 },
  table: { width: "100%", borderCollapse: "collapse" },
  th: { padding: "12px 16px", background: "#0f172a", color: "#94a3b8", textAlign: "left", fontSize: 13 },
  td: { padding: "12px 16px", fontSize: 14, color: "#e2e8f0" },
  trEven: { background: "#1e293b" },
  trOdd: { background: "#162032" },
  formGroup: { marginBottom: 16 },
  label: { display: "block", color: "#94a3b8", fontSize: 13, marginBottom: 6 },
  input: { width: "100%", padding: "10px 12px", background: "#0f172a", border: "1px solid #334155", borderRadius: 8, color: "#e2e8f0", fontSize: 14, boxSizing: "border-box" },
  btn: { width: "100%", padding: "14px", background: "#6366f1", color: "white", border: "none", borderRadius: 8, fontSize: 16, fontWeight: 700, cursor: "pointer", marginTop: 8 },
  resultBox: { marginTop: 24, padding: 24, background: "#0f172a", borderRadius: 12, border: "1px solid #10b981" },
};