import React, { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, formatGBP } from "../api";
import { useCart } from "../contexts";
import { Send, Sparkles, ShoppingBag } from "lucide-react";

const SUGGESTIONS = [
  "What do I need to cook jollof rice for 5 people?",
  "Help me make pepper soup.",
  "What can I use for moi moi?",
  "I want breakfast staples for the week.",
  "I need banga soup essentials for 4.",
  "Build me a family efo riro basket.",
];

export default function AIAssistant() {
  const [params] = useSearchParams();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [sending, setSending] = useState(false);
  const [lastBasket, setLastBasket] = useState(null);
  const { bulkAdd } = useCart();
  const bottomRef = useRef();

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, sending]);

  useEffect(() => {
    const q = params.get("q");
    if (q && messages.length === 0) send(q);
    // eslint-disable-next-line
  }, []);

  const send = async (text) => {
    const msg = (text || input).trim();
    if (!msg) return;
    setMessages(m => [...m, { role: "user", content: msg }]);
    setInput(""); setSending(true);
    try {
      const { data } = await api.post("/ai/chat", { message: msg, session_id: sessionId });
      setSessionId(data.session_id);
      setMessages(m => [...m, { role: "assistant", content: data.reply, basket: data.basket }]);
      if (data.basket?.hydrated_items?.length) setLastBasket(data.basket);
    } catch (e) {
      setMessages(m => [...m, { role: "assistant", content: "Sorry, I couldn't reach the AI just now. Please try again." }]);
    } finally {
      setSending(false);
    }
  };

  const addBasket = async () => {
    if (!lastBasket?.hydrated_items) return;
    const items = lastBasket.hydrated_items.map(i => ({ product_id: i.product_id, quantity: i.quantity }));
    await bulkAdd(items);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8" data-testid="ai-page">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-full bg-afro-primary text-white flex items-center justify-center"><Sparkles /></div>
        <div>
          <h1 className="font-display text-3xl md:text-4xl">Afrobean AI</h1>
          <p className="text-sm text-afro-ink-soft">Tell me what you want to cook. I'll build your basket.</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white border border-afro-border rounded-2xl flex flex-col h-[70vh]" data-testid="ai-chat">
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 && (
              <div className="text-center py-10">
                <p className="text-afro-ink-soft mb-4">Try one of these to get started:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {SUGGESTIONS.map((s, i) => (
                    <button key={i} onClick={() => send(s)} className="bg-afro-surface-alt hover:bg-afro-border text-sm px-3 py-1.5 rounded-full transition" data-testid={`ai-sug-${i}`}>{s}</button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${m.role === "user" ? "bg-afro-primary text-white" : "bg-afro-surface-alt text-afro-ink"}`}>
                  <pre className="whitespace-pre-wrap font-sans">{m.content}</pre>
                  {m.basket?.hydrated_items?.length > 0 && (
                    <div className="mt-3 bg-white rounded-xl p-3 border border-afro-border">
                      <div className="text-xs text-afro-ink-soft mb-2">Suggested basket:</div>
                      <div className="space-y-1 text-xs">
                        {m.basket.hydrated_items.map(it => (
                          <div key={it.product_id} className="flex justify-between">
                            <span>{it.name} × {it.quantity}</span>
                            <span className="font-semibold">{formatGBP(it.price * it.quantity)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {sending && (
              <div className="flex justify-start">
                <div className="bg-afro-surface-alt rounded-2xl px-4 py-3 flex gap-1 text-afro-ink-soft">
                  <span className="animate-bounce">●</span><span className="animate-bounce" style={{ animationDelay: ".15s" }}>●</span><span className="animate-bounce" style={{ animationDelay: ".3s" }}>●</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          <form onSubmit={e => { e.preventDefault(); send(); }} className="border-t border-afro-border p-4 flex gap-2" data-testid="ai-form">
            <input
              value={input} onChange={e => setInput(e.target.value)}
              placeholder="Tell Afrobean AI what you want to cook..."
              className="afr-input flex-1"
              data-testid="ai-input"
            />
            <button type="submit" disabled={sending || !input.trim()} className="afr-btn-primary px-5 disabled:opacity-60" data-testid="ai-send"><Send size={16} /></button>
          </form>
        </div>

        <aside className="bg-afro-surface-alt rounded-2xl p-6 border border-afro-border h-fit lg:sticky lg:top-28" data-testid="ai-basket">
          <h3 className="font-display text-2xl">Your AI basket</h3>
          {!lastBasket ? (
            <p className="text-sm text-afro-ink-soft mt-3">Your suggested basket will appear here after chatting with Afrobean AI.</p>
          ) : (
            <>
              <div className="mt-4 space-y-2">
                {lastBasket.hydrated_items.map(it => (
                  <div key={it.product_id} className="flex gap-3 items-center bg-white p-2 rounded-md border border-afro-border">
                    {it.image && <img src={it.image} alt="" className="w-12 h-12 object-cover rounded" />}
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-medium truncate">{it.name}</div>
                      <div className="text-[10px] text-afro-ink-soft">× {it.quantity} · {formatGBP(it.price)}</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 pt-4 border-t border-afro-border flex justify-between font-semibold">
                <span>Total</span>
                <span>{formatGBP(lastBasket.hydrated_items.reduce((a, b) => a + b.price * b.quantity, 0))}</span>
              </div>
              <button onClick={addBasket} className="afr-btn-primary w-full mt-4 inline-flex items-center justify-center gap-2" data-testid="ai-add-basket"><ShoppingBag size={16} /> Add all to basket</button>
              {lastBasket.notes && <p className="text-xs text-afro-ink-soft mt-3">{lastBasket.notes}</p>}
            </>
          )}
        </aside>
      </div>
    </div>
  );
}
