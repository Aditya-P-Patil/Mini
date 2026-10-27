"use client";

import { ArrowDownRight, ArrowUpRight, BarChart3, Search } from "lucide-react";
import {
  Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { useState } from "react";
import { api } from "../../lib/api";

const money = (value) => value == null
  ? "—"
  : new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 2 }).format(value);

export default function Analysis() {
  const [ticker, setTicker] = useState("AAPL");
  const [start, setStart] = useState("2020-09-26");
  const [end, setEnd] = useState("2021-06-26");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function run(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      setData(await api.compare(ticker, start, end));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  const chartData = data
    ? Object.entries(data.metrics).map(([name, metric]) => ({
        name: name.replaceAll("_", " "),
        start: metric.start_value || 0,
        end: metric.end_value || 0,
      }))
    : [];

  return (
    <div className="page">
      <div className="page-heading"><div><div className="stat-label">Structured financial data</div><h1>Financial <span className="accent-text">analysis</span></h1><p className="subtitle">Deterministic comparisons from the repository&apos;s financial dataset.</p></div></div>
      <section className="card" style={{ marginBottom: 20 }}>
        <form className="form-row" onSubmit={run}>
          <input value={ticker} onChange={(event) => setTicker(event.target.value)} aria-label="Ticker" placeholder="Ticker" style={{ maxWidth: 120, textTransform: "uppercase" }} />
          <input type="date" value={start} onChange={(event) => setStart(event.target.value)} aria-label="Start date" />
          <input type="date" value={end} onChange={(event) => setEnd(event.target.value)} aria-label="End date" />
          <button className="button primary" disabled={busy}><Search size={14} />{busy ? "Loading…" : "Compare periods"}</button>
        </form>
      </section>
      {error && <div className="error">{error}</div>}
      {!data ? <div className="empty"><BarChart3 size={25} /><p>Choose a ticker and two reporting dates to compare financial metrics.</p></div> : <>
        <div className="section-head"><div><h2>{data.company} <span className="badge neutral">{data.ticker}</span></h2><p className="subtitle">{data.start_date} → {data.end_date}</p></div></div>
        <div className="grid metric-grid">{Object.entries(data.metrics).map(([name, metric]) => <div className="card" key={name}><div className="metric-name">{name.replaceAll("_", " ")}</div><div className="metric-number">{money(metric.end_value)}</div><div className={metric.percentage_change >= 0 ? "positive" : "negative"} style={{ fontSize: 12, marginTop: 8 }}>{metric.percentage_change == null ? "Change unavailable" : <>{metric.percentage_change >= 0 ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />} {metric.percentage_change}% period change</>}</div><div className="stat-note" style={{ marginTop: 8 }}>From {money(metric.start_value)} · absolute {money(metric.absolute_change)}</div></div>)}</div>
        <section className="card" style={{ marginTop: 16 }}><div className="section-head"><h2>Period comparison</h2><span className="stat-note">Reported values · source dataset units</span></div><ResponsiveContainer width="100%" height={280}><BarChart data={chartData} margin={{ top: 8, right: 15, left: 15, bottom: 35 }}><CartesianGrid strokeDasharray="3 3" stroke="#e8edf1" /><XAxis dataKey="name" angle={-18} textAnchor="end" height={55} tick={{ fontSize: 10 }} /><YAxis tick={{ fontSize: 10 }} tickFormatter={money} /><Tooltip formatter={money} /><Bar dataKey="start" fill="#9db8ef" name={start} /><Bar dataKey="end" fill="#2463eb" name={end} /></BarChart></ResponsiveContainer></section>
      </>}
    </div>
  );
}
