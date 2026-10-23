"use client";

import Link from "next/link";
import { ArrowLeft, Plus } from "lucide-react";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { useChatStore } from "@/store/chatStore";

export default function ChatPage() {
  const { reset } = useChatStore();

  const handleNewChat = () => {
    reset();
  };

  return (
    <div className="h-full flex flex-col bg-parchment">
      {/* Desktop Header only - On mobile, the unified top header in DashboardLayout handles title, Back, and New Chat */}
      <header className="hidden md:flex border-b border-ink/8 bg-white/80 backdrop-blur-sm px-6 py-3.5 items-center justify-between flex-shrink-0 shadow-xs">
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="flex items-center gap-1.5 text-xs font-medium text-ink/70 hover:text-ink bg-parchment hover:bg-parchment-dim border border-ink/10 px-3.5 py-1.5 rounded-full transition-all"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Dashboard</span>
          </Link>
          <div>
            <h1 className="text-base font-semibold text-ink leading-tight">MindBridge AI Companion</h1>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[11px] text-ink/50">Confidential · Empathetic AI Support</span>
            </div>
          </div>
        </div>

        {/* New Chat Button directly inside Chat Section */}
        <button
          type="button"
          onClick={handleNewChat}
          className="flex items-center gap-1.5 text-xs font-semibold bg-gold text-gold-dark hover:bg-gold/90 px-4 py-2 rounded-full shadow-sm hover:shadow transition-all active:scale-95"
        >
          <Plus className="h-3.5 w-3.5 stroke-[2.5]" />
          <span>New Chat</span>
        </button>
      </header>

      <div className="flex-1 overflow-hidden">
        <ChatWindow />
      </div>
    </div>
  );
}
