"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  MessageCircle,
  Heart,
  BookOpen,
  LifeBuoy,
  Settings,
  LogOut,
  Plus,
  ArrowLeft,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { clearTokens } from "@/lib/api";
import { useChatStore } from "@/store/chatStore";
import { chatApi } from "@/lib/api";
import { useEffect } from "react";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/chat", label: "Chat", icon: MessageCircle },
  { href: "/dashboard/mood", label: "Mood Tracker", icon: Heart },
  { href: "/dashboard/journal", label: "Journal", icon: BookOpen },
  { href: "/dashboard/resources", label: "Resources", icon: LifeBuoy },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

interface SidebarProps {
  mobileOpen?: boolean;
  onMobileClose?: () => void;
}

export function Sidebar({ mobileOpen = false, onMobileClose }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { sessions, activeSessionId, setSessions, setActiveSession, setMessages, reset } = useChatStore();

  useEffect(() => {
    chatApi.getSessions().then((r) => setSessions(r.data)).catch(() => {});
  }, [setSessions]);

  const handleNavClick = () => {
    if (onMobileClose) onMobileClose();
  };

  const newChat = () => {
    reset();
    router.push("/dashboard/chat");
    if (onMobileClose) onMobileClose();
  };

  const openSession = async (id: string) => {
    setActiveSession(id);
    const { data } = await chatApi.getMessages(id);
    setMessages(data);
    router.push("/dashboard/chat");
    if (onMobileClose) onMobileClose();
  };

  const logout = () => {
    clearTokens();
    reset();
    router.push("/login");
    if (onMobileClose) onMobileClose();
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          onClick={onMobileClose}
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden transition-opacity"
        />
      )}

      {/* Sidebar Container: hidden on mobile unless mobileOpen=true */}
      <aside
        className={cn(
          "w-64 flex-col border-r border-white/5 bg-ink h-full transition-transform duration-300 z-50",
          "fixed inset-y-0 left-0 md:static md:flex",
          mobileOpen ? "flex translate-x-0" : "-translate-x-full md:translate-x-0"
        )}
      >
        <div className="p-4 border-b border-white/5 flex items-center justify-between">
          <Link
            href="/dashboard"
            onClick={handleNavClick}
            className="flex items-center gap-2 font-display text-lg text-parchment hover:text-gold transition-colors"
          >
            MindBridge
          </Link>
          <div className="flex items-center gap-2">
            {/* Back to landing page */}
            <Link
              href="/"
              title="Back to Landing Page"
              className="flex items-center gap-1 text-xs text-parchment/60 hover:text-parchment bg-white/5 hover:bg-white/10 px-2 py-1 rounded transition-colors"
            >
              <ArrowLeft className="h-3 w-3" />
              <span>Home</span>
            </Link>

            {/* Mobile close button */}
            <button
              type="button"
              onClick={onMobileClose}
              className="p-1 rounded text-parchment/60 hover:text-parchment hover:bg-white/10 md:hidden"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {nav.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              onClick={handleNavClick}
              className={cn(
                "flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors duration-300 ease-mb-ease",
                pathname === href
                  ? "bg-sage/15 text-gold font-medium"
                  : "text-parchment/50 hover:bg-white/5 hover:text-parchment"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}

          {/* New Chat & Recent Chats Section */}
          <div className="pt-3">
            <button
              type="button"
              onClick={newChat}
              className="flex w-full items-center justify-center gap-2 rounded-full bg-gold px-3 py-2.5 text-sm font-medium text-gold-dark hover:bg-gold/90 shadow-sm transition-colors duration-300 ease-mb-ease"
            >
              <Plus className="h-4 w-4" />
              New Chat
            </button>

            {sessions.length > 0 && (
              <p className="text-[10px] text-parchment/30 uppercase tracking-wider mt-4 mb-1.5 px-2">
                Recent Chats
              </p>
            )}
            <div className="max-h-52 overflow-y-auto space-y-1">
              {sessions.slice(0, 10).map((s) => (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => openSession(s.id)}
                  className={cn(
                    "w-full truncate rounded px-2.5 py-1.5 text-left text-xs transition-colors duration-200",
                    activeSessionId === s.id
                      ? "bg-sage/15 text-gold font-medium"
                      : "text-parchment/40 hover:bg-white/5 hover:text-parchment/80"
                  )}
                >
                  {s.title}
                </button>
              ))}
            </div>
          </div>
        </nav>

        <div className="p-3 border-t border-white/5">
          <button
            type="button"
            onClick={logout}
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-parchment/50 hover:bg-white/5 hover:text-parchment transition-colors duration-300 ease-mb-ease"
          >
            <LogOut className="h-4 w-4" />
            Log out
          </button>
        </div>
      </aside>
    </>
  );
}
