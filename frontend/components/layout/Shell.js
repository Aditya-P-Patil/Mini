"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3, BookOpen, ChevronLeft, ChevronRight, Clock3, FileText,
  LayoutDashboard, MessageSquare, Settings2, Wifi,
} from "lucide-react";
import { useState } from "react";

const links = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/research", label: "Research chat", icon: MessageSquare },
  { href: "/analysis", label: "Financial analysis", icon: BarChart3 },
  { href: "/history", label: "Conversation history", icon: Clock3 },
];

export default function Shell({ children }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  return (
    <div className={`app-shell ${collapsed ? "sidebar-collapsed" : ""}`}>
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">F</div><span>Folio<span className="accent">AI</span></span></div>
        <div className="workspace-label">WORKSPACE</div>
        <nav aria-label="Primary navigation">
          {links.map(({ href, label, icon: Icon }) => (
            <Link key={href} href={href} prefetch className={`nav-link ${pathname === href || (href !== "/" && pathname.startsWith(`${href}/`)) ? "active" : ""}`} title={label}>
              <Icon size={18} /><span>{label}</span>
            </Link>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="connection"><span className="status-dot" /> <span>API connected</span></div>
          <Link href="/settings" className="nav-link"><Settings2 size={18} /><span>Settings</span></Link>
          <button className="collapse-button" onClick={() => setCollapsed(!collapsed)} aria-label="Collapse sidebar">
            {collapsed ? <ChevronRight size={17} /> : <ChevronLeft size={17} />}<span>Collapse menu</span>
          </button>
        </div>
      </aside>
      <main className="main-content"><header className="topbar"><div className="eyebrow"><BookOpen size={15} /> Financial research workspace</div><div className="topbar-status"><Wifi size={15} /> Live data</div></header>{children}</main>
    </div>
  );
}
