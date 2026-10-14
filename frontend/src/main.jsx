import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BookOpen,
  Check,
  FilePlus,
  Loader2,
  MessageSquarePlus,
  PanelRightOpen,
  Plus,
  RefreshCw,
  Send,
  Trash2,
  Upload,
  X
} from "lucide-react";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

function App() {
  const [notebooks, setNotebooks] = useState([]);
  const [activeNotebookId, setActiveNotebookId] = useState(null);
  const [sources, setSources] = useState([]);
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [newNotebookName, setNewNotebookName] = useState("Project I Notebook");
  const [renameName, setRenameName] = useState("");
  const [pasteTitle, setPasteTitle] = useState("Pasted source");
  const [pasteText, setPasteText] = useState("");
  const [selectedSource, setSelectedSource] = useState(null);
  const [selectedChunk, setSelectedChunk] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const fileInput = useRef(null);

  async function loadNotebooks() {
    const data = await api("/notebooks");
    setNotebooks(data);
    if (!activeNotebookId && data[0]) {
      setActiveNotebookId(data[0].id);
    }
  }

  async function loadNotebookData(notebookId = activeNotebookId) {
    if (!notebookId) return;
    const [sourceData, messageData] = await Promise.all([
      api(`/notebooks/${notebookId}/sources`),
      api(`/notebooks/${notebookId}/messages`)
    ]);
    setSources(sourceData);
    setMessages(messageData);
    if (selectedSource) {
      setSelectedSource(sourceData.find((source) => source.id === selectedSource.id) || null);
    }
  }

  useEffect(() => {
    loadNotebooks().catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    loadNotebookData().catch((err) => setError(err.message));
    const notebook = notebooks.find((item) => item.id === activeNotebookId);
    setRenameName(notebook?.name || "");
  }, [activeNotebookId]);

  useEffect(() => {
    const pending = sources.some((source) => source.status === "pending" || source.status === "processing");
    if (!pending || !activeNotebookId) return;
    const timer = setInterval(() => loadNotebookData().catch(() => {}), 1800);
    return () => clearInterval(timer);
  }, [sources, activeNotebookId]);

  async function createNotebook() {
    setError("");
    const notebook = await api("/notebooks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newNotebookName })
    });
    setNotebooks([notebook, ...notebooks]);
    setActiveNotebookId(notebook.id);
  }

  async function deleteNotebook(id) {
    await api(`/notebooks/${id}`, { method: "DELETE" });
    const next = notebooks.filter((notebook) => notebook.id !== id);
    setNotebooks(next);
    setActiveNotebookId(next[0]?.id || null);
    setSources([]);
    setMessages([]);
  }

  async function renameNotebook() {
    if (!activeNotebookId || !renameName.trim()) return;
    const updated = await api(`/notebooks/${activeNotebookId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: renameName.trim() })
    });
    setNotebooks(notebooks.map((notebook) => (notebook.id === updated.id ? updated : notebook)));
  }

  async function uploadFile(event) {
    const file = event.target.files?.[0];
    if (!file || !activeNotebookId) return;
    const form = new FormData();
    form.append("file", file);
    form.append("title", file.name);
    await api(`/notebooks/${activeNotebookId}/sources`, { method: "POST", body: form });
    event.target.value = "";
    await loadNotebookData();
  }

  async function addTextSource() {
    if (!pasteText.trim() || !activeNotebookId) return;
    await api(`/notebooks/${activeNotebookId}/sources/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: pasteTitle, text: pasteText })
    });
    setPasteText("");
    await loadNotebookData();
  }

  async function toggleSource(source) {
    const updated = await api(`/sources/${source.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: !source.enabled })
    });
    setSources(sources.map((item) => (item.id === updated.id ? updated : item)));
    if (selectedSource?.id === updated.id) setSelectedSource(updated);
  }

  async function deleteSource(source) {
    await api(`/sources/${source.id}`, { method: "DELETE" });
    setSources(sources.filter((item) => item.id !== source.id));
    if (selectedSource?.id === source.id) setSelectedSource(null);
  }

  async function sendQuestion(event) {
    event.preventDefault();
    if (!question.trim() || !activeNotebookId || busy) return;
    setBusy(true);
    setError("");
    const asked = question;
    setQuestion("");
    setMessages((items) => [...items, { role: "user", content: asked, id: `local-${Date.now()}` }]);
    try {
      const answer = await api(`/notebooks/${activeNotebookId}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: asked })
      });
      setMessages((items) => [
        ...items,
        {
          role: "assistant",
          content: answer.answer,
          citations_json: answer.citations,
          id: `answer-${Date.now()}`
        }
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
      loadNotebookData().catch(() => {});
    }
  }

  async function openCitation(citation) {
    const chunk = await api(`/chunks/${citation.chunk_id}`);
    setSelectedChunk(chunk);
  }

  return (
    <div className="app-shell">
      <aside className="source-pane">
        <div className="brand-row">
          <BookOpen size={22} />
          <div>
            <h1>Mini NotebookLM</h1>
            <p>Project I</p>
          </div>
        </div>

        <div className="notebook-create">
          <input value={newNotebookName} onChange={(event) => setNewNotebookName(event.target.value)} />
          <button onClick={createNotebook} title="Create notebook" aria-label="Create notebook">
            <Plus size={18} />
          </button>
        </div>

        <div className="notebook-list">
          {notebooks.map((notebook) => (
            <button
              key={notebook.id}
              className={notebook.id === activeNotebookId ? "notebook active" : "notebook"}
              onClick={() => setActiveNotebookId(notebook.id)}
            >
              <span>{notebook.name}</span>
              <Trash2
                size={16}
                onClick={(event) => {
                  event.stopPropagation();
                  deleteNotebook(notebook.id).catch((err) => setError(err.message));
                }}
              />
            </button>
          ))}
        </div>

        <div className="section-head">
          <h2>Sources</h2>
          <div className="icon-row">
            <button onClick={() => fileInput.current?.click()} title="Upload source" aria-label="Upload source">
              <Upload size={17} />
            </button>
            <button onClick={() => loadNotebookData()} title="Refresh sources" aria-label="Refresh sources">
              <RefreshCw size={17} />
            </button>
          </div>
          <input ref={fileInput} type="file" accept=".pdf,.txt,.md" onChange={uploadFile} hidden />
        </div>

        <div className="paste-box">
          <input value={pasteTitle} onChange={(event) => setPasteTitle(event.target.value)} />
          <textarea value={pasteText} onChange={(event) => setPasteText(event.target.value)} />
          <button className="wide-action" onClick={addTextSource}>
            <FilePlus size={17} />
            Add pasted text
          </button>
        </div>

        <div className="source-list">
          {sources.map((source) => (
            <div className="source-item" key={source.id}>
              <button className="source-main" onClick={() => setSelectedSource(source)}>
                <span>{source.title}</span>
                <small>
                  {source.status}
                  {source.status === "failed" && source.error ? `: ${source.error}` : ""}
                </small>
              </button>
              <button
                className={source.enabled ? "toggle enabled" : "toggle"}
                onClick={() => toggleSource(source).catch((err) => setError(err.message))}
                title={source.enabled ? "Disable source" : "Enable source"}
                aria-label={source.enabled ? "Disable source" : "Enable source"}
              >
                {source.enabled ? <Check size={15} /> : <X size={15} />}
              </button>
              <button
                onClick={() => deleteSource(source).catch((err) => setError(err.message))}
                title="Delete source"
                aria-label="Delete source"
              >
                <Trash2 size={15} />
              </button>
            </div>
          ))}
        </div>
      </aside>

      <main className="chat-pane">
        <header className="chat-header">
          <div>
            <div className="rename-row">
              <input value={renameName} onChange={(event) => setRenameName(event.target.value)} />
              <button onClick={() => renameNotebook().catch((err) => setError(err.message))} title="Rename notebook" aria-label="Rename notebook">
                <Check size={17} />
              </button>
            </div>
            <p>{sources.filter((source) => source.enabled).length} enabled sources</p>
          </div>
          <button onClick={() => setSelectedChunk(null)} title="Open source panel" aria-label="Open source panel">
            <PanelRightOpen size={18} />
          </button>
        </header>

        {error && <div className="error-bar">{error}</div>}

        <div className="messages">
          {messages.map((message) => (
            <article key={message.id} className={`message ${message.role}`}>
              <p>{message.content}</p>
              {message.citations_json?.length > 0 && (
                <div className="citations">
                  {message.citations_json.map((citation) => (
                    <button key={citation.chunk_id} onClick={() => openCitation(citation)}>
                      {citation.source_title}
                      {citation.page ? ` p.${citation.page}` : ""}
                    </button>
                  ))}
                </div>
              )}
            </article>
          ))}
        </div>

        <form className="composer" onSubmit={sendQuestion}>
          <MessageSquarePlus size={20} />
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask from enabled sources"
          />
          <button disabled={busy || !question.trim()} title="Send" aria-label="Send">
            {busy ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
          </button>
        </form>
      </main>

      <aside className="detail-pane">
        <h2>Evidence</h2>
        {selectedChunk ? (
          <div className="detail-content">
            <h3>{selectedChunk.source_title}</h3>
            <small>{selectedChunk.page ? `Page ${selectedChunk.page}` : "Text source"}</small>
            <p>{selectedChunk.text}</p>
          </div>
        ) : selectedSource ? (
          <div className="detail-content">
            <h3>{selectedSource.title}</h3>
            <small>{selectedSource.status}</small>
            <p>{selectedSource.summary || "Summary will appear after processing."}</p>
            {selectedSource.suggested_questions_json?.length > 0 && (
              <div className="suggestions">
                {selectedSource.suggested_questions_json.map((item) => (
                  <button key={item} onClick={() => setQuestion(item)}>
                    {item}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="empty-state">Select a source or citation.</div>
        )}
      </aside>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
