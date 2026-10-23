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
    <div className="h-full flex flex-col bg-slate-50">
      <header className="border-b border-slate-200 bg-white px-4 md:px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2.5">
          <Link
            href="/dashboard"
            className="flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-full transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Dashboard</span>
            <span className="sm:hidden">Back</span>
          </Link>
          <div>
            <h1 className="text-sm md:text-base font-semibold text-slate-900 leading-tight">MindBridge Chat</h1>
            <p className="text-[10px] md:text-[11px] text-slate-500 hidden sm:block">Not a substitute for professional care</p>
          </div>
        </div>

        {/* New Chat Button directly inside Chat Section */}
        <button
          type="button"
          onClick={handleNewChat}
          className="flex items-center gap-1.5 text-xs font-medium bg-gold text-gold-dark hover:bg-gold/90 px-3.5 py-1.5 rounded-full shadow-sm transition-colors"
        >
          <Plus className="h-3.5 w-3.5" />
          <span>New Chat</span>
        </button>
      </header>
      <div className="flex-1 overflow-hidden">
        <ChatWindow />
      </div>
    </div>
  );
}
