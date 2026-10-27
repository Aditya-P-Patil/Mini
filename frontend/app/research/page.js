"use client";

import ReactMarkdown from "react-markdown";
import { Clock3, FileText, Lightbulb, MessageSquare, Send, SlidersHorizontal, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../../lib/api";

export default function Research() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.conversations().then(setHistory).catch(() => {});
  }, []);

  async function ask(event) {
    event.preventDefault();
    if (!question.trim() || busy) return;
    setBusy(true);
    setError("");
    try {
      const next = await api.ask(question.trim());
      setResult(next);
      setHistory((items) => [
        {
          ...next,
          id: next.conversation_id,
          title: next.question,
        },
        ...items.filter((item) => item.id !== next.conversation_id),
      ]);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <div className="stat-label">Evidence-backed answers</div>
          <h1>Research <span className="accent-text">chat</span></h1>
          <p className="subtitle">Ask questions about your indexed financial reports. Every answer is grounded in retrieved passages.</p>
        </div>
      </div>
      <div className="research-layout">
        <aside className="card chat-history">
          <div className="section-head"><h2>Recent chats</h2><Clock3 size={16} /></div>
          {history.length ? history.slice(0, 8).map((item) => (
            <button className={`history-item ${result?.conversation_id === item.id ? "selected" : ""}`} key={item.id} onClick={() => { setResult(item); setQuestion(item.question); }}>
              <strong>{item.title}</strong>
              <span>{item.created_at ? new Date(item.created_at).toLocaleDateString() : "Just now"}</span>
            </button>
          )) : <p className="stat-note">Your saved questions will appear here.</p>}
        </aside>
        <div className="chat">
          <div className="research-toolbar"><span className="research-back">← Research</span><span className="badge badge-success">Citations enabled</span></div>
          <div className="card composer-panel" style={{ marginBottom: 16 }}>
            <form onSubmit={ask}>
              <div className="composer">
                <textarea value={question} onChange={(event) => setQuestion(event.target.value)} rows={3} placeholder="e.g. How did operating income change between the reported periods?" aria-label="Research question" />
                <div className="composer-footer"><div className="composer-tools"><span className="composer-chip"><FileText size={13} /> Indexed reports</span><span className="composer-chip"><SlidersHorizontal size={13} /> Top 5 sources</span></div><button className="button primary" disabled={busy || !question.trim()}>{busy ? <><Sparkles size={15} />Thinking…</> : <><Send size={15} />Ask research</>}</button></div>
              </div>
              <div className="stat-note" style={{ marginTop: 10 }}>Answers use the top 5 retrieved document chunks. Do not treat generated text as financial advice.</div>
            </form>
          </div>
          {error && <div className="error">{error}</div>}
          {!result && !busy && <div className="empty research-empty"><MessageSquare size={26} /><strong>Your research desk is ready</strong><p>Ask a question about a report, metric, or filing detail to see cited evidence here.</p></div>}
          {busy && <div className="card loading"><Sparkles size={15} /> Retrieving evidence and drafting an answer…</div>}
          {!result && !busy && <div className="suggestion-row"><span className="suggestion-label"><Lightbulb size={14} /> Suggested questions</span>{["What are the key proposals?", "Summarize the report’s main risks", "What changed between periods?"].map((suggestion) => <button className="suggestion" key={suggestion} onClick={() => setQuestion(suggestion)}>{suggestion}</button>)}</div>}
          {result && (
            <>
              <div className="chat-message user"><div className="message-label">Your question</div>{result.question}</div>
              <div className="chat-message">
                <div className="message-label">FolioAI answer</div>
                <div className="markdown"><ReactMarkdown>{result.answer}</ReactMarkdown></div>
                {result.sources?.length > 0 && (
                  <div className="source">
                    <strong>Sources · {result.sources.length}</strong>
                    {result.sources.map((source) => (
                      <details key={source.source_id} style={{ marginTop: 10 }}>
                        <summary>{source.source_id} · {source.filename} · page {source.page_number}{source.similarity_score != null ? ` · similarity ${source.similarity_score}` : ""}</summary>
                        <div className="source-text">{source.text}</div>
                      </details>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
