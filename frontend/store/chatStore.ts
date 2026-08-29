import { create } from "zustand";
import type { ChatMessage, ChatSession } from "@/types/chat.types";

interface ChatState {
  sessions: ChatSession[];
  activeSessionId: string | null;
  messages: ChatMessage[];
  isTyping: boolean;
  showCrisis: boolean;
  setSessions: (sessions: ChatSession[]) => void;
  setActiveSession: (id: string | null) => void;
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (msg: ChatMessage) => void;
  setTyping: (v: boolean) => void;
  setShowCrisis: (v: boolean) => void;
  reset: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  sessions: [],
  activeSessionId: null,
  messages: [],
  isTyping: false,
  showCrisis: false,
  setSessions: (sessions) => set({ sessions }),
  setActiveSession: (id) => set({ activeSessionId: id }),
  setMessages: (messages) => set({ messages }),
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  setTyping: (isTyping) => set({ isTyping }),
  setShowCrisis: (showCrisis) => set({ showCrisis }),
  reset: () =>
    set({
      sessions: [],
      activeSessionId: null,
      messages: [],
      isTyping: false,
      showCrisis: false,
    }),
}));
