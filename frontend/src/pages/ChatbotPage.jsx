import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import DashboardLayout from "../components/layout/DashboardLayout";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import { chatbotApi } from "../api/client";
import { getApiErrorMessage } from "../utils/apiError";

function MessageBubble({ role, content, createdAt }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-md border px-3 py-2 ${
          isUser
            ? "bg-mint-active text-onMint border-mint-active"
            : "bg-card text-content border-borderLight"
        }`}
      >
        <p className="text-sm m-0 whitespace-pre-wrap break-words">{content}</p>
        {createdAt ? (
          <p className={`text-[11px] mt-1 mb-0 ${isUser ? "text-white/90" : "text-contentMuted"}`}>
            {new Date(createdAt).toLocaleString()}
          </p>
        ) : null}
      </div>
    </div>
  );
}

export default function ChatbotPage() {
  const [sessionId, setSessionId] = useState(localStorage.getItem("chatbot_session_id") || "");
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const listRef = useRef(null);

  const canSend = useMemo(() => inputValue.trim().length > 0 && !sending, [inputValue, sending]);

  const scrollToBottom = useCallback(() => {
    const el = listRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, []);

  const loadSuggestions = useCallback(async () => {
    setLoadingSuggestions(true);
    try {
      const { data } = await chatbotApi.getSuggestions();
      setSuggestions(Array.isArray(data?.suggestions) ? data.suggestions : []);
    } catch (err) {
      // Suggestions are optional UI enhancement.
      setSuggestions([]);
      setError((prev) => prev || getApiErrorMessage(err, "Failed to load suggestions"));
    } finally {
      setLoadingSuggestions(false);
    }
  }, []);

  const loadHistory = useCallback(async (sid) => {
    if (!sid) return;
    setLoadingHistory(true);
    setError("");
    try {
      const { data } = await chatbotApi.getHistory(sid, 60);
      const rows = Array.isArray(data?.messages) ? data.messages : [];
      setMessages(
        rows.map((m) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          created_at: m.created_at,
        })),
      );
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load chat history"));
    } finally {
      setLoadingHistory(false);
    }
  }, []);

  useEffect(() => {
    loadSuggestions();
  }, [loadSuggestions]);

  useEffect(() => {
    if (sessionId) {
      loadHistory(sessionId);
    }
  }, [sessionId, loadHistory]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, sending, scrollToBottom]);

  const sendMessage = useCallback(
    async (text) => {
      const msg = (text || "").trim();
      if (!msg || sending) return;
      setError("");

      const optimisticId = `local-${Date.now()}`;
      const optimisticUser = { id: optimisticId, role: "user", content: msg, created_at: new Date().toISOString() };
      setMessages((prev) => [...prev, optimisticUser]);
      setInputValue("");
      setSending(true);

      try {
        const body = sessionId ? { session_id: sessionId, message: msg } : { message: msg };
        const { data } = await chatbotApi.sendMessage(body);
        if (data?.session_id && data.session_id !== sessionId) {
          setSessionId(data.session_id);
          localStorage.setItem("chatbot_session_id", data.session_id);
        }
        const assistantMsg = {
          id: data?.message_id || `assistant-${Date.now()}`,
          role: "assistant",
          content: data?.reply || "I could not generate a response right now.",
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMsg]);
        if (Array.isArray(data?.suggestions) && data.suggestions.length > 0) {
          setSuggestions(data.suggestions);
        }
      } catch (err) {
        setError(getApiErrorMessage(err, "Failed to send message"));
        // rollback optimistic user message on failure
        setMessages((prev) => prev.filter((m) => m.id !== optimisticId));
      } finally {
        setSending(false);
      }
    },
    [sending, sessionId],
  );

  const onSubmit = async (e) => {
    e.preventDefault();
    await sendMessage(inputValue);
  };

  const handleNewChat = () => {
    if (sending) return;
    setMessages([]);
    setInputValue("");
    setError("");
    setSessionId("");
    localStorage.removeItem("chatbot_session_id");
  };

  return (
    <DashboardLayout
      title="Career Guidance Chatbot"
      subtitle="Ask about freelancing, proposals, portfolio improvements, and learning paths."
      showSearch={false}
    >
      <Card className="p-3">
        <div className="flex flex-wrap items-center gap-2">
          <Button type="button" variant="secondary" onClick={loadSuggestions} disabled={loadingSuggestions || sending}>
            {loadingSuggestions ? "Loading prompts…" : "Refresh prompts"}
          </Button>
          {sessionId ? (
            <Button
              type="button"
              variant="secondary"
              onClick={() => loadHistory(sessionId)}
              disabled={loadingHistory || sending}
            >
              {loadingHistory ? "Loading history…" : "Reload history"}
            </Button>
          ) : null}
          {sessionId ? <p className="text-xs text-contentMuted m-0">Session: {sessionId.slice(0, 8)}…</p> : null}
          <div className="ml-auto">
            <Button type="button" variant="secondary" onClick={handleNewChat} disabled={sending}>
              New Chat
            </Button>
          </div>
        </div>
      </Card>

      {error ? (
        <Card>
          <p className="text-sm text-error m-0">{error}</p>
        </Card>
      ) : null}

      <Card className="p-0 overflow-hidden">
        <div
          ref={listRef}
          className="h-[420px] overflow-y-auto px-3 py-3 bg-main border-b border-borderLight flex flex-col gap-3"
        >
          {messages.length === 0 && !loadingHistory ? (
            <div className="text-center py-6">
              <p className="text-sm text-contentSecondary m-0 mb-2">
                Start by asking a question about freelancing, portfolio, proposals, or tasks.
              </p>
              <p className="text-xs text-contentMuted m-0">
                Example: "How can I improve my portfolio for clients?"
              </p>
            </div>
          ) : null}

          {messages.map((m) => (
            <MessageBubble key={m.id} role={m.role} content={m.content} createdAt={m.created_at} />
          ))}

          {sending ? (
            <div className="flex justify-start">
              <div className="rounded-md border border-borderLight bg-card px-3 py-2">
                <p className="text-sm text-contentSecondary m-0">Assistant is typing…</p>
              </div>
            </div>
          ) : null}
        </div>

        <form onSubmit={onSubmit} className="p-3 bg-card flex gap-2 items-start">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask your question..."
            className="flex-1"
            disabled={sending}
            maxLength={2000}
          />
          <Button type="submit" disabled={!canSend}>
            {sending ? "Sending…" : "Send"}
          </Button>
        </form>
      </Card>

      <Card>
        <h3 className="text-sm font-semibold text-content m-0 mb-2">Suggested prompts</h3>
        {loadingSuggestions ? (
          <p className="text-sm text-contentSecondary m-0">Loading suggestions…</p>
        ) : suggestions.length === 0 ? (
          <p className="text-sm text-contentSecondary m-0">No suggestions available right now.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {suggestions.map((s, idx) => (
              <button
                key={`${s}-${idx}`}
                type="button"
                className="text-sm py-2 px-3 rounded-md bg-primary border border-borderInput text-content cursor-pointer hover:border-mint-active"
                onClick={() => sendMessage(s)}
                disabled={sending}
              >
                {s}
              </button>
            ))}
          </div>
        )}
      </Card>
    </DashboardLayout>
  );
}

