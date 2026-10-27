"use client";

import { CheckCircle2, ChevronRight, FileText, Loader2, Search, UploadCloud, XCircle } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import EmptyState from "../../components/ui/EmptyState";
import StatusBadge from "../../components/ui/StatusBadge";
import { api } from "../../lib/api";

const stages = ["Uploaded", "Text extracted", "Chunks created", "Embeddings stored", "Ready for research"];

function ProcessingStages({ document, busy }) {
  const completed = document ? [
    true,
    document.page_count > 0,
    document.chunk_count > 0,
    document.embedded_chunk_count === document.chunk_count && document.chunk_count > 0,
    document.ready === true,
  ] : [];
  return (
    <div className="processing-card">
      <div className="section-head"><div><div className="stat-label">Processing pipeline</div><h2>{busy ? "Preparing your report" : "Document readiness"}</h2></div><StatusBadge tone={completed[4] ? "success" : "neutral"}>{completed[4] ? "Searchable" : "In progress"}</StatusBadge></div>
      <div className="stage-list">
        {stages.map((stage, index) => <div className={`stage ${completed[index] ? "complete" : ""}`} key={stage}><span className="stage-icon">{completed[index] ? <CheckCircle2 size={15} /> : <span>{index + 1}</span>}</span><span>{stage}</span>{index < stages.length - 1 && <ChevronRight className="stage-arrow" size={14} />}</div>)}
      </div>
      {!completed[4] && !busy && <p className="inline-help">Run processing again from the upload flow if a stage did not complete. Existing chunking replaces the document&apos;s previous chunks safely.</p>}
    </div>
  );
}

export default function Documents() {
  const inputRef = useRef();
  const [documents, setDocuments] = useState([]);
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const load = () => api.documents().then(setDocuments).catch((requestError) => setError(requestError.message));
  useEffect(() => { load(); }, []);
  const filteredDocuments = documents.filter((document) => {
    const matchesQuery = document.filename.toLowerCase().includes(query.toLowerCase());
    const ready = document.ready === true;
    return matchesQuery && (filter === "all" || (filter === "ready" ? ready : !ready));
  });

  async function upload(file) {
    setError(""); setMessage("");
    if (!file || file.type !== "application/pdf" || !file.name.toLowerCase().endsWith(".pdf")) return setError("Choose a PDF file.");
    if (file.size > 25 * 1024 * 1024) return setError("PDF must be 25 MB or smaller.");
    setBusy(true);
    try {
      const result = await api.upload(file);
      setMessage(`${result.filename} uploaded. Extracted ${result.page_count} pages.`);
      await api.chunk(result.document_id);
      setMessage("Text extracted and chunks created. Generating embeddings…");
      await api.embed(result.document_id);
      setMessage("Document is ready for semantic research.");
      await load();
    } catch (requestError) {
      setError(`${requestError.message} You can retry this document without re-uploading if it was already stored.`);
    } finally { setBusy(false); }
  }

  return <div className="page">
    <div className="page-heading"><div><div className="stat-label">Knowledge base</div><h1>Documents</h1><p className="subtitle">Build a searchable evidence library from your financial reports.</p></div><button className="button primary" onClick={() => inputRef.current?.click()} disabled={busy}><UploadCloud size={15} /> Add report</button></div>
    <div className={`upload-zone ${dragging ? "dragging" : ""}`} onDragOver={(event) => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={(event) => { event.preventDefault(); setDragging(false); upload(event.dataTransfer.files[0]); }}>
      <div className="upload-icon">{busy ? <Loader2 className="spin" aria-hidden="true" /> : <UploadCloud size={21} aria-hidden="true" />}</div>
      <p className="upload-title">{busy ? "Processing report…" : "Drop a PDF here"}</p>
      <p className="subtitle">or <button className="file-label" onClick={() => inputRef.current?.click()}>browse from your computer</button></p>
      <input ref={inputRef} type="file" accept="application/pdf,.pdf" onChange={(event) => upload(event.target.files[0])} />
      <div className="stat-note">Maximum file size: 25 MB · Text-based PDFs only · Files are validated by the backend</div>
    </div>
    {message && <div className="success" role="status"><CheckCircle2 size={14} /> {message}</div>}
    {error && <div className="error" role="alert"><XCircle size={14} /> {error}</div>}
    {busy && <div className="progress-track" aria-label="Document processing in progress"><span /></div>}
    {selected && <ProcessingStages document={selected} busy={busy} />}
    <section className="card library-card"><div className="section-head"><div><div className="stat-label">Evidence library</div><h2>Reports <StatusBadge>{documents.length}</StatusBadge></h2></div><span className="stat-note">Click a row to inspect chunks</span></div>
      <div className="library-toolbar"><div className="library-tabs">{[["all", `All documents (${documents.length})`], ["ready", "Ready"], ["processing", "Needs processing"]].map(([value, label]) => <button key={value} className={`library-tab ${filter === value ? "active" : ""}`} onClick={() => setFilter(value)}>{label}</button>)}</div><div className="library-search"><Search size={14} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search documents..." aria-label="Search documents" /></div></div>
      {filteredDocuments.length ? <div className="table-wrap"><table><thead><tr><th>Report</th><th>Pages</th><th>Chunks</th><th>Embeddings</th><th>Added</th><th>Status</th></tr></thead><tbody>{filteredDocuments.map((document) => { const ready = document.ready === true; return <tr key={document.id} onClick={() => setSelected(document)} tabIndex={0} onKeyDown={(event) => event.key === "Enter" && setSelected(document)}><td><FileText size={14} className="table-icon" /> <strong>{document.filename}</strong></td><td>{document.page_count}</td><td>{document.chunk_count || "—"}</td><td>{document.embedded_chunk_count || "—"}</td><td>{document.uploaded_at ? new Date(document.uploaded_at).toLocaleDateString() : "—"}</td><td><StatusBadge tone={ready ? "success" : "warning"}>{ready ? "Ready" : "Needs processing"}</StatusBadge></td></tr>; })}</tbody></table></div> : <EmptyState icon={FileText} title={documents.length ? "No matching reports" : "Your library is empty"} description={documents.length ? "Try a different search or status filter." : "Upload a text-based PDF to start building your research set."} action={<button className="button secondary" onClick={() => inputRef.current?.click()}>Upload first report</button>} />}
    </section>
    {selected && <DocumentDetails document={selected} onClose={() => setSelected(null)} />}
  </div>;
}

function DocumentDetails({ document, onClose }) {
  const [chunks, setChunks] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { api.chunks(document.id).then(setChunks).catch((requestError) => setError(requestError.message)); }, [document.id]);
  return <section className="card detail-card"><div className="section-head"><div><div className="stat-label">Document detail</div><h2>{document.filename}</h2><p className="subtitle">{document.page_count} pages · ID {document.id}</p></div><button className="button secondary" onClick={onClose}>Close</button></div>{error && <div className="error">{error}</div>}{chunks ? <><div className="stat-note">{chunks.length} chunks available for inspection</div>{chunks.slice(0, 8).map((chunk) => <details className="source" key={chunk.chunk_id}><summary>Page {chunk.page_number} · Chunk {chunk.chunk_index + 1}</summary><div className="source-text">{chunk.text}</div></details>)}</> : <div className="loading">Loading extracted chunks…</div>}</section>;
}
