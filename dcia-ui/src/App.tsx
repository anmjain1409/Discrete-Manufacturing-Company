import { useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const API = "http://localhost:8000/api";

const SEVERITY_COLORS: Record<string, string> = {
  HIGH: "#E24B4A", MEDIUM: "#EF9F27", LOW: "#1D9E75"
};

type ImpactResult = {
  intent: any; impacts: any[]; class_rules: any[];
  historical: any[]; cost_estimate: any; report: string;
};

export default function App() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImpactResult | null>(null);
  const [error, setError] = useState("");

  const submit = async () => {
    if (!message.trim()) return;
    setLoading(true); setError(""); setResult(null);
    try {
      const res = await axios.post(`${API}/chat`, { message });
      setResult(res.data);
    } catch (e: any) {
      setError("API error: " + (e.message || "unknown"));
    } finally { setLoading(false); }
  };

  const costData = result ? [
    { name: "P10 (optimistic)", value: result.cost_estimate.total_p10_usd },
    { name: "P50 (likely)",     value: result.cost_estimate.total_p50_usd },
    { name: "P90 (pessimistic)",value: result.cost_estimate.total_p90_usd },
  ] : [];

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "2rem", fontFamily: "sans-serif" }}>
      <h1 style={{ fontSize: 22, fontWeight: 500 }}>DCIA — Design Change Intelligence Assistant</h1>
      <p style={{ color: "#666", fontSize: 14 }}>PoC · MDL Shipbuilding · Source: PS-1 &amp; PS-2</p>

      {/* Input */}
      <div style={{ display: "flex", gap: 8, marginTop: 24 }}>
        <input
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={e => e.key === "Enter" && submit()}
          placeholder='Try: "Increase main engine power by 15%. What systems are affected and what will it cost?"'
          style={{ flex: 1, padding: "10px 14px", borderRadius: 8,
                   border: "1px solid #ddd", fontSize: 15 }}
        />
        <button onClick={submit} disabled={loading}
          style={{ padding: "10px 20px", borderRadius: 8, background: "#185FA5",
                   color: "#fff", border: "none", cursor: "pointer", fontWeight: 500 }}>
          {loading ? "Analysing…" : "Analyse"}
        </button>
      </div>

      {/* Sample prompts */}
      <div style={{ marginTop: 10, display: "flex", gap: 8, flexWrap: "wrap" }}>
        {[
          "Increase main engine power by 15% for improved speed",
          "Replace the shaft generator with a new 3MW unit",
          "Add structural stiffening at frames 40–48 to support a new weapons mount",
          "Increase fuel tank capacity by 20% for extended petrol range"
        ].map(p => (
          <button key={p} onClick={() => setMessage(p)}
            style={{ padding: "4px 12px", borderRadius: 20, border: "1px solid #ccc",
                     background: "#f8f8f8", cursor: "pointer", fontSize: 13 }}>
            {p}
          </button>
        ))}
      </div>

      {error && <p style={{ color: "#E24B4A", marginTop: 16 }}>{error}</p>}

      {result && (
        <div style={{ marginTop: 32 }}>

          {/* AI report */}
          <section style={{ background: "#f0f4f8", borderRadius: 10, padding: 20, marginBottom: 24 }}>
            <h2 style={{ fontSize: 16, fontWeight: 500, marginTop: 0 }}>Impact assessment</h2>
            <p style={{ lineHeight: 1.7, fontSize: 15, whiteSpace: "pre-wrap" }}>{result.report}</p>
            <p style={{ fontSize: 12, color: "#888", marginBottom: 0 }}>
              Source: Neo4j graph traversal + LLM synthesis · Confidence: {result.cost_estimate.confidence}
            </p>
          </section>

          {/* Affected systems */}
          <section style={{ marginBottom: 24 }}>
            <h2 style={{ fontSize: 16, fontWeight: 500 }}>Affected systems ({result.impacts.length})</h2>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
              <thead>
                <tr style={{ background: "#f0f0f0" }}>
                  {["System", "Discipline", "Hops from origin", "Severity", "Reason"].map(h => (
                    <th key={h} style={{ padding: "8px 12px", textAlign: "left", fontWeight: 500 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.impacts.map((imp, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #eee" }}>
                    <td style={{ padding: "8px 12px" }}>{imp.name}</td>
                    <td style={{ padding: "8px 12px", textTransform: "capitalize" }}>{imp.discipline}</td>
                    <td style={{ padding: "8px 12px" }}>{imp.hops}</td>
                    <td style={{ padding: "8px 12px" }}>
                      <span style={{ padding: "2px 10px", borderRadius: 12,
                                     background: SEVERITY_COLORS[imp.severity] + "22",
                                     color: SEVERITY_COLORS[imp.severity],
                                     fontWeight: 500, fontSize: 12 }}>
                        {imp.severity}
                      </span>
                    </td>
                    <td style={{ padding: "8px 12px", color: "#555" }}>
                      {imp.cascade_reasons?.[imp.cascade_reasons.length - 1] || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          {/* Cost estimate */}
          <section style={{ marginBottom: 24 }}>
            <h2 style={{ fontSize: 16, fontWeight: 500 }}>Cost estimate (USD)</h2>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={costData} layout="vertical">
                <XAxis type="number" tickFormatter={v => `$${(v/1e6).toFixed(1)}M`} fontSize={12}/>
                <YAxis type="category" dataKey="name" width={140} fontSize={12}/>
                <Tooltip formatter={(v: any) => `$${Number(v).toLocaleString()}`}/>
                <Bar dataKey="value" radius={[0,4,4,0]}>
                  {costData.map((_, i) => (
                    <Cell key={i} fill={["#1D9E75","#185FA5","#E24B4A"][i]}/>
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <p style={{ fontSize: 12, color: "#888" }}>{result.cost_estimate.note}</p>
          </section>

          {/* Class rules */}
          <section style={{ marginBottom: 24 }}>
            <h2 style={{ fontSize: 16, fontWeight: 500 }}>
              Class rule flags ({result.class_rules.length})
            </h2>
            {result.class_rules.map((cr, i) => (
              <div key={i} style={{ padding: "10px 14px", borderLeft: "3px solid #EF9F27",
                                    background: "#fffbf0", borderRadius: 6, marginBottom: 8 }}>
                <strong style={{ fontSize: 13 }}>{cr.society} — {cr.clause}</strong>
                <p style={{ margin: "4px 0 0", fontSize: 13, color: "#555" }}>{cr.description}</p>
                <p style={{ margin: "4px 0 0", fontSize: 12, color: "#888" }}>
                  Triggered by: {cr.system}
                </p>
              </div>
            ))}
          </section>

          {/* Historical analogues */}
          {result.historical.length > 0 && (
            <section>
              <h2 style={{ fontSize: 16, fontWeight: 500 }}>Historical analogues</h2>
              {result.historical.map((h, i) => (
                <div key={i} style={{ padding: "10px 14px", border: "1px solid #e0e0e0",
                                      borderRadius: 8, marginBottom: 8 }}>
                  <strong style={{ fontSize: 13 }}>{h.id}</strong> — {h.description}
                  <p style={{ margin: "4px 0", fontSize: 13, color: "#555" }}>{h.summary}</p>
                  <p style={{ margin: "4px 0 0", fontSize: 12, color: "#185FA5" }}>
                    Actual cost: ${h.cost_actual_usd?.toLocaleString()} ·
                    Schedule delay: {h.delay_days} days
                  </p>
                </div>
              ))}
            </section>
          )}
        </div>
      )}
    </div>
  );
}