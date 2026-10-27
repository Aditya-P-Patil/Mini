"use client";

import Link from "next/link";
import { ArrowUpRight, FileText, MessageSquare, RefreshCw, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Dashboard() {
  const [documents, setDocuments] = useState([]);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    api.documents().then(setDocuments).catch((e) => setError(e.message));
    api.health().then(setHealth).catch((e) => setError(e.message));
  }, []);
  const chunks = documents.reduce((sum, doc) => sum + (doc.chunk_count || 0), 0);
  return <div className="page">
    <div className="page-heading"><div><div className="stat-label">Research command center</div><h1>Good morning, <span className="accent-text">researcher.</span></h1><p className="subtitle">Your evidence-backed financial workspace, in one view.</p></div><Link href="/research" className="button primary"><MessageSquare size={15}/> Ask a question</Link></div>
    {error && <div className="error">{error} <button className="button secondary" onClick={() => location.reload()}><RefreshCw size={13}/> Retry</button></div>}
    <div className="grid stats-grid">
      <div className="card"><div className="stat-label">Documents</div><div className="stat-value">{documents.length}</div><div className="stat-note">Uploaded reports</div></div>
      <div className="card"><div className="stat-label">Pages indexed</div><div className="stat-value">{documents.reduce((s,d)=>s+(d.page_count||0),0)}</div><div className="stat-note">Extracted text pages</div></div>
      <div className="card"><div className="stat-label">Chunks</div><div className="stat-value">{chunks || "—"}</div><div className="stat-note">{chunks ? "Available for retrieval" : "Chunk documents to begin"}</div></div>
      <div className="card"><div className="stat-label">System status</div><div className="stat-value" style={{fontSize:20}}>{health?.status === "healthy" ? "Operational" : "Checking"}</div><div className="stat-note"><span className="status-dot" style={{display:"inline-block",marginRight:5}}/>{health?.database || "Connecting"}</div></div>
    </div>
    <div className="grid two-col">
      <section className="card"><div className="section-head"><h2>Document library</h2><Link className="link" href="/documents">View all <ArrowUpRight size={13}/></Link></div>
        {documents.length ? <div className="table-wrap"><table><thead><tr><th>Report</th><th>Pages</th><th>Added</th></tr></thead><tbody>{documents.slice(0,5).map(d=><tr key={d.id}><td><FileText size={14} style={{verticalAlign:"middle",marginRight:7,color:"#5686e2"}}/>{d.filename}</td><td>{d.page_count}</td><td>{d.uploaded_at ? new Date(d.uploaded_at).toLocaleDateString() : "—"}</td></tr>)}</tbody></table></div> : <div className="empty"><FileText size={24}/><p>No documents uploaded yet.</p><Link href="/documents" className="button secondary">Upload your first report</Link></div>}
      </section>
      <section className="card"><div className="section-head"><h2>Research readiness</h2><ShieldCheck size={18} color="#159570"/></div><p className="subtitle">Build a reliable retrieval set before asking questions.</p><div style={{marginTop:22}}><div className="section-head"><span className="stat-label">Ingestion workflow</span><span className="badge">Live</span></div>{["Upload a PDF report","Create searchable chunks","Generate embeddings"].map((item,i)=><div key={item} style={{display:"flex",gap:12,alignItems:"center",padding:"12px 0",borderBottom:"1px solid #eef1f4",fontSize:13}}><span className="badge neutral">{i+1}</span>{item}</div>)}</div></section>
    </div>
  </div>;
}
