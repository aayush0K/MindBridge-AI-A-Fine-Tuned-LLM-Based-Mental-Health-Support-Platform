"use client";

import { useEffect, useRef } from "react";
import { Sparkles } from "lucide-react";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import { ChatInput } from "./ChatInput";
import { QuickReplies } from "./QuickReplies";
import { CrisisAlert } from "./CrisisAlert";
import { useChatStore } from "@/store/chatStore";
import { chatApi } from "@/lib/api";

const STARTERS = [
  { text: "I'm feeling anxious about my exams or work", tag: "Stress & Anxiety" },
  { text: "I've been feeling lonely and disconnected lately", tag: "Connection" },
  { text: "I'm having trouble sleeping with racing thoughts", tag: "Sleep & Calm" },
  { text: "I just need a safe space to vent and be heard", tag: "Emotional Release" },
];

const QUICK_REPLIES = [
  "Tell me more",
  "That helps, thank you",
  "I need coping strategies",
];

export function ChatWindow() {
  const {
    messages,
    activeSessionId,
    isTyping,
    showCrisis,
    addMessage,
    setMessages,
    setActiveSession,
    setSessions,
    setTyping,
    setShowCrisis,
  } = useChatStore();
  const bottomRef = useRef<HTMLDivElement>(null);
  const hasLoadedRef = useRef(false);

  // ── Load most recent session on mount ─────────────────────────────────
  useEffect(() => {
    if (hasLoadedRef.current) return;
    hasLoadedRef.current = true;

    const loadLastSession = async () => {
      try {
        const { data: sessions } = await chatApi.getSessions();
        setSessions(sessions);
        if (sessions.length > 0 && !activeSessionId) {
          const lastSession = sessions[0]; // most recent (ordered by started_at desc)
          setActiveSession(lastSession.id);
          const { data: msgs } = await chatApi.getMessages(lastSession.id);
          setMessages(
            msgs.map((m: any) => ({
              role: m.role,
              content: m.content,
              relevance_score: m.relevance_score,
              is_crisis: m.is_crisis,
            }))
          );
        }
      } catch {
        // silently ignore — user may not have any sessions yet
      }
    };

    loadLastSession();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Auto-scroll to bottom ─────────────────────────────────────────────
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const sendMessage = async (text: string) => {
    addMessage({ role: "user", content: text });
    setTyping(true);
    try {
      const { data } = await chatApi.sendMessage(text, activeSessionId || undefined);
      if (!activeSessionId) {
        setActiveSession(data.session_id);
        // Refresh sidebar sessions list
        chatApi.getSessions().then((r) => setSessions(r.data)).catch(() => {});
      }
      addMessage({
        role: "assistant",
        content: data.response,
        relevance_score: data.relevance_score,
        is_crisis: data.is_crisis,
      });
      if (data.is_crisis) setShowCrisis(true);
    } catch {
      addMessage({
        role: "assistant",
        content: "I'm having trouble connecting right now. Please try again in a moment.",
      });
    } finally {
      setTyping(false);
    }
  };

  return (
    <div className="relative flex flex-col h-full bg-parchment">
      <div className="mb-ambient-bg" />
      <div className="flex flex-col h-full relative z-10 flex-1">
        {showCrisis && <CrisisAlert onAcknowledge={() => setShowCrisis(false)} />}

        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="max-w-xl mx-auto text-center pt-8 md:pt-14 space-y-5">
              <div className="inline-flex p-3 rounded-2xl bg-sage/15 text-sage ring-8 ring-sage/5 shadow-xs">
                <Sparkles className="h-6 w-6" />
              </div>
              <div>
                <h2 className="font-display text-2xl md:text-3xl text-ink font-semibold tracking-tight">
                  How are you feeling today?
                </h2>
                <p className="font-sans text-xs md:text-sm text-ink/60 mt-1.5 max-w-md mx-auto">
                  I'm here to listen without judgment. Choose a topic below or share what's on your mind.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 text-left pt-2">
                {STARTERS.map((s) => (
                  <button
                    key={s.text}
                    type="button"
                    onClick={() => sendMessage(s.text)}
                    className="group rounded-2xl border border-ink/8 bg-white/95 p-4 text-left shadow-xs hover:border-sage/40 hover:shadow-md hover:-translate-y-0.5 active:scale-[0.99] transition-all"
                  >
                    <span className="inline-block text-[10px] font-semibold uppercase tracking-wider text-sage bg-sage/10 px-2 py-0.5 rounded-full mb-2">
                      {s.tag}
                    </span>
                    <p className="text-sm text-ink font-medium leading-snug group-hover:text-sage transition-colors">
                      {s.text}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto w-full space-y-4">
              {messages.map((m, i) => (
                <MessageBubble key={i} message={m} />
              ))}
              {isTyping && <TypingIndicator />}
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {messages.length > 0 && messages[messages.length - 1]?.role === "assistant" && !isTyping && (
          <div className="max-w-3xl mx-auto w-full">
            <QuickReplies suggestions={QUICK_REPLIES} onSelect={sendMessage} />
          </div>
        )}
        <ChatInput onSend={sendMessage} disabled={isTyping} />
      </div>
    </div>
  );
}
