"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { Menu, Plus, ArrowLeft } from "lucide-react";
import { Sidebar } from "@/components/layout/Sidebar";
import { getAccessToken } from "@/lib/api";
import { useChatStore } from "@/store/chatStore";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isAuthed, setIsAuthed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const { reset } = useChatStore();

  useEffect(() => {
    if (!getAccessToken()) {
      router.replace("/login");
    } else {
      setIsAuthed(true);
    }
  }, [router]);

  if (!isAuthed) {
    return (
      <div className="flex h-screen items-center justify-center bg-parchment">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-sage border-t-transparent" />
      </div>
    );
  }

  const handleMobileNewChat = () => {
    reset();
    router.push("/dashboard/chat");
  };

  // Determine page title for mobile top bar
  const getPageTitle = () => {
    if (pathname === "/dashboard") return "Dashboard";
    if (pathname.includes("/chat")) return "AI Chat";
    if (pathname.includes("/mood")) return "Mood Tracker";
    if (pathname.includes("/journal")) return "Journal";
    if (pathname.includes("/resources")) return "Crisis Resources";
    if (pathname.includes("/settings")) return "Settings";
    return "MindBridge";
  };

  return (
    <div className="flex h-screen bg-parchment overflow-hidden">
      {/* Responsive Sidebar */}
      <Sidebar
        mobileOpen={mobileSidebarOpen}
        onMobileClose={() => setMobileSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        {/* Mobile Top Header (always visible on small screens) */}
        <header className="md:hidden flex items-center justify-between px-4 py-3 bg-ink border-b border-white/10 text-parchment flex-shrink-0 z-30">
          <div className="flex items-center gap-2.5">
            <button
              type="button"
              onClick={() => setMobileSidebarOpen(true)}
              className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-parchment/80 hover:text-parchment transition-colors"
              aria-label="Open menu"
            >
              <Menu className="h-5 w-5" />
            </button>
            {pathname !== "/dashboard" && (
              <Link
                href="/dashboard"
                className="flex items-center gap-1 text-xs text-parchment/70 hover:text-parchment bg-white/5 hover:bg-white/10 px-2 py-1 rounded"
              >
                <ArrowLeft className="h-3 w-3" />
                <span>Back</span>
              </Link>
            )}
            <span className="font-display text-sm tracking-wide text-parchment font-medium truncate">
              {getPageTitle()}
            </span>
          </div>

          {/* Quick Action: New Chat (Always available on mobile!) */}
          <button
            type="button"
            onClick={handleMobileNewChat}
            className="flex items-center gap-1.5 text-xs font-medium bg-gold text-gold-dark hover:bg-gold/90 px-3 py-1.5 rounded-full shadow-sm transition-colors"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>New Chat</span>
          </button>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-hidden">{children}</main>
      </div>
    </div>
  );
}
