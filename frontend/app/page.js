"use client";

import Link from "next/link";
import { ArrowUpRight, FileText, MessageSquare, RefreshCw, Search, ShieldCheck, UploadCloud } from "lucide-react";
import { useEffect, useState } from "react";
import AnimatedContent from "../components/AnimatedContent";
import FadeContent from "../components/FadeContent";
import { api } from "../lib/api";

export default function Dashboard() {
  const [documents, setDocuments] = useState([]);
  const [health, setHealth] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [error, setError] = useState("");
  useEffect(() => {
    api.documents().then(setDocuments).catch((e) => setError(e.message));
    api.health().then(setHealth).catch((e) => setError(e.message));
    api.conversations().then(setConversations).catch(() => {});
  }, []);
  const chunks = documents.reduce((sum, doc) => sum + (doc.chunk_count || 0), 0);
  return <div className="page">
    <AnimatedContent className="dashboard-hero-motion" trigger="mount" distance={22} duration={0.65}>
    <section className="dashboard-hero">
      <div className="page-heading"><div><div className="eyebrow-label"><span className="pulse-dot" /> Research command center</div><h1>Good morning, <span className="accent-text">researcher.</span></h1><p className="subtitle">Turn your reports into clear, evidence-backed answers.</p></div><div className="heading-actions"><Link href="/documents" className="button secondary"><UploadCloud size={15}/> Add report</Link><Link href="/research" className="button primary"><MessageSquare size={15}/> Ask a question</Link></div></div>
      <div className="dashboard-actions">
        <Link href="/research" className="dashboard-action primary-action"><span className="action-icon"><MessageSquare size={16} /></span><span><strong>Start new research</strong><small>Ask questions and get cited answers</small></span><ArrowUpRight size={15} /></Link>
        <Link href="/documents" className="dashboard-action"><span className="action-icon"><UploadCloud size={16} /></span><span><strong>Upload a document</strong><small>Add financial reports to your library</small></span><ArrowUpRight size={15} /></Link>
      </div>
      <Link href="/research" className="dashboard-search"><span className="search-icon"><Search size={17} /></span><span>Ask about a company, market, or your documents...</span><span className="search-key">Ask FolioAI <ArrowUpRight size={14} /></span></Link>
      <div className="suggestion-row dashboard-suggestions"><span className="suggestion-label">Try asking:</span>{["What are the key risks?", "Summarize this document", "Compare reported periods"].map((suggestion) => <Link href="/research" className="suggestion" key={suggestion}>{suggestion}</Link>)}</div>
    </section>
    </AnimatedContent>
    {error && <div className="error">{error} <button className="button secondary" onClick={() => location.reload()}><RefreshCw size={13}/> Retry</button></div>}
    <FadeContent className="dashboard-motion" stagger={0.08} threshold={0.16} duration={0.55}>
    <div className="grid stats-grid">
      <div className="card"><div className="stat-label">Documents</div><div className="stat-value">{documents.length}</div><div className="stat-note">Uploaded reports</div></div>
      <div className="card"><div className="stat-label">Pages indexed</div><div className="stat-value">{documents.reduce((s,d)=>s+(d.page_count||0),0)}</div><div className="stat-note">Extracted text pages</div></div>
      <div className="card"><div className="stat-label">Chunks</div><div className="stat-value">{chunks || "—"}</div><div className="stat-note">{chunks ? "Available for retrieval" : "Chunk documents to begin"}</div></div>
      <div className="card"><div className="stat-label">System status</div><div className="stat-value" style={{fontSize:20}}>{health?.status === "healthy" ? "Operational" : "Checking"}</div><div className="stat-note"><span className="status-dot" style={{display:"inline-block",marginRight:5}}/>{health?.database || "Connecting"}</div></div>
    </div>
    </FadeContent>
    <FadeContent className="dashboard-motion" threshold={0.12} duration={0.55}>
    <div className="grid two-col">
      <section className="card"><div className="section-head"><h2>Document library</h2><Link className="link" href="/documents">View all <ArrowUpRight size={13}/></Link></div>
        {documents.length ? <div className="table-wrap"><table><thead><tr><th>Report</th><th>Pages</th><th>Added</th></tr></thead><tbody>{documents.slice(0,5).map(d=><tr key={d.id}><td><FileText size={14} style={{verticalAlign:"middle",marginRight:7,color:"#5686e2"}}/>{d.filename}</td><td>{d.page_count}</td><td>{d.uploaded_at ? new Date(d.uploaded_at).toLocaleDateString() : "—"}</td></tr>)}</tbody></table></div> : <div className="empty"><FileText size={24}/><p>No documents uploaded yet.</p><Link href="/documents" className="button secondary">Upload your first report</Link></div>}
      </section>
      <section className="card"><div className="section-head"><h2>Research readiness</h2><ShieldCheck size={18} color="#159570"/></div><p className="subtitle">Build a reliable retrieval set before asking questions.</p><div style={{marginTop:22}}><div className="section-head"><span className="stat-label">Ingestion workflow</span><span className="badge badge-success">Live</span></div>{["Upload a PDF report","Create searchable chunks","Generate embeddings for every chunk"].map((item,i)=><div key={item} style={{display:"flex",gap:12,alignItems:"center",padding:"12px 0",borderBottom:"1px solid #eef1f4",fontSize:13}}><span className="badge neutral">{i+1}</span>{item}</div>)}</div></section>
    </div>
    </FadeContent>
    <FadeContent className="dashboard-motion" threshold={0.12} duration={0.55}>
    <section className="card activity-card"><div className="section-head"><div><div className="stat-label">Persisted activity</div><h2>Recent research</h2></div><Link href="/history" className="link">View history <ArrowUpRight size={13}/></Link></div>{conversations.length ? conversations.slice(0, 4).map((item) => <Link className="activity-row" href="/research" key={item.id}><MessageSquare size={15}/><span><strong>{item.title}</strong><small>{item.created_at ? new Date(item.created_at).toLocaleString() : "Saved research"}</small></span><ArrowUpRight size={14}/></Link>) : <div className="empty compact"><MessageSquare size={22}/><p>Your saved research questions will appear here.</p></div>}</section>
    </FadeContent>
  </div>;
}
