import { useRef, useState, type FormEvent } from "react";

type Message = { role: "assistant" | "user"; content: string };

const welcomeMessage: Message = {
  role: "assistant",
  content:
    "Corpus đã sẵn sàng. Bạn có thể hỏi về sinh lý học, chấn thương hoặc tác động tâm lý – xã hội của Brazilian Jiu-Jitsu.",
};

const examples = [
  "What are the most common injuries?",
  "BJJ đòi hỏi thể lực như thế nào?",
  "How does BJJ affect psychological resilience?",
];

function ArchiveMark() {
  return (
    <span className="archive-symbol" aria-hidden="true">
      <span />
    </span>
  );
}

function SendMark() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-5 w-5" fill="none">
      <path d="M4 12h15M13 5l7 7-7 7" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}

function App() {
  const [messages, setMessages] = useState<Message[]>([welcomeMessage]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const conversationEnd = useRef<HTMLDivElement>(null);

  async function ask(value: string) {
    const prompt = value.trim();
    if (!prompt || loading) return;

    setQuestion("");
    setError("");
    setMessages((current) => [...current, { role: "user", content: prompt }]);
    setLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: prompt }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Không thể gửi câu hỏi.");
      setMessages((current) => [...current, { role: "assistant", content: result.answer }]);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Không thể kết nối. Hãy thử lại.");
    } finally {
      setLoading(false);
      requestAnimationFrame(() => conversationEnd.current?.scrollIntoView({ behavior: "smooth", block: "end" }));
    }
  }

  function submitQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void ask(question);
  }

  function clearConversation() {
    setMessages([welcomeMessage]);
    setError("");
    setQuestion("");
  }

  return (
    <div className="min-h-dvh bg-ink-950 text-film">
      <div className="mx-auto flex min-h-dvh max-w-[1600px]">
        <aside className="hidden w-[292px] shrink-0 flex-col border-r border-mint/20 bg-ink-900 px-6 py-7 md:flex">
          <div className="archive-mark-row">
            <ArchiveMark />
            <div>
              <div className="font-display text-xl uppercase tracking-wide text-film-bright">BJJ RAG</div>
              <div className="rail-caption">Evidence archive</div>
            </div>
          </div>

          <div className="rail-title">Corpus readout</div>
          <div className="grid grid-cols-3 border-y border-mint/25 py-3">
            <div className="readout-cell"><strong>02</strong><span>PDF</span></div>
            <div className="readout-cell border-l border-white/10 pl-3"><strong>08</strong><span>Pages</span></div>
            <div className="readout-cell border-l border-white/10 pl-3"><strong>EN / VI</strong><span>Query</span></div>
          </div>

          <div className="mt-7 rail-title">In this archive</div>
          <ul className="space-y-3 text-sm leading-5 text-film-dim">
            <li className="archive-entry">Physiological demands, biomechanics &amp; injury epidemiology</li>
            <li className="archive-entry">Neurobiological resilience, flow states &amp; psychosocial adaptation</li>
          </ul>

          <div className="mt-auto space-y-2 border-t border-white/10 pt-5 text-xs text-film-dim">
            <div className="status-line">Embedding · text-embedding-3-small</div>
            <div className="status-line">Chat · gpt-4o-mini</div>
            <div className="status-line">Cosine · top 5 · threshold 0.2</div>
            <div className="status-line">Independent retrieval per question</div>
            <button className="clear-button mt-5 w-full" onClick={clearConversation} type="button">
              Clear conversation
            </button>
          </div>
        </aside>

        <main className="flex min-h-dvh min-w-0 flex-1 flex-col px-4 pb-4 pt-5 sm:px-8 sm:pt-8 lg:px-14">
          <header className="masthead">
            <div className="flex items-center gap-3 md:block">
              <div className="md:hidden"><ArchiveMark /></div>
              <h1 className="font-display text-[clamp(2.8rem,7vw,5.8rem)] leading-[0.82] tracking-[-0.035em] text-film-bright">
                BJJ <span className="text-mint">Research</span><br className="hidden sm:block" /> Assistant
              </h1>
            </div>
            <p className="max-w-xl pb-1 text-sm leading-6 text-film-dim sm:text-base">
              Đặt câu hỏi bằng tiếng Việt hoặc English. Câu trả lời chỉ dựa trên corpus nghiên cứu và trích dẫn theo trang.
            </p>
          </header>

          <div className="mb-2 flex items-center justify-between gap-3 font-display text-xs uppercase tracking-[0.12em] text-film-dim">
            <span>Conversation plate</span>
            <div className="flex items-center gap-3">
              <span className="text-mint">Source-locked output</span>
              <button className="clear-button mobile-clear-button md:hidden" onClick={clearConversation} type="button">
                Clear
              </button>
            </div>
          </div>

          <section aria-label="Conversation" className="conversation min-h-[250px] flex-1 overflow-y-auto pb-5" aria-live="polite">
            {messages.map((message, index) => (
              <article className={`message-plate ${message.role === "user" ? "message-user" : "message-assistant"}`} key={`${index}-${message.role}`}>
                <div className={`message-mark ${message.role === "user" ? "message-mark-user" : ""}`} aria-hidden="true">
                  <span />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="message-role">{message.role === "user" ? "You" : "Research assistant"}</div>
                  <p className="message-copy">{message.content}</p>
                </div>
              </article>
            ))}

            {messages.length === 1 && !loading && (
              <div className="starter-prompts" aria-label="Example questions">
                <p className="mb-2 text-xs text-film-dim">Try asking</p>
                {examples.map((example) => (
                  <button className="starter-button" key={example} onClick={() => void ask(example)} type="button">
                    {example}
                  </button>
                ))}
              </div>
            )}

            {loading && (
              <article className="message-plate message-assistant" role="status">
                <div className="message-mark" aria-hidden="true"><span /></div>
                <div>
                  <div className="message-role">Research assistant</div>
                  <p className="message-copy text-film-dim">Đang đối chiếu các trang liên quan…</p>
                  <div className="scan-track" aria-hidden="true"><span /></div>
                </div>
              </article>
            )}
            {error && <p className="error-note" role="alert">{error}</p>}
            <div ref={conversationEnd} />
          </section>

          <form className="query-form" onSubmit={submitQuestion}>
            <label className="sr-only" htmlFor="question">Your question</label>
            <textarea
              id="question"
              name="question"
              maxLength={2000}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  void ask(question);
                }
              }}
              placeholder="Nhập câu hỏi để quét corpus nghiên cứu…"
              rows={2}
              value={question}
            />
            <button className="send-button" disabled={loading || !question.trim()} type="submit" aria-label="Send question">
              <SendMark />
            </button>
            <div className="query-hint">Enter để gửi · Shift + Enter để xuống dòng</div>
          </form>
        </main>
      </div>
    </div>
  );
}

export default App;
