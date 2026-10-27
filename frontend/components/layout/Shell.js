"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3, Bell, BookOpen, ChevronLeft, ChevronRight, Clock3, FileText,
  LayoutDashboard, Menu, MessageSquare, Search, Settings2, Wifi, X,
} from "lucide-react";
import { useState } from "react";

const groups = [
  {
    label: "Workspace",
    links: [
      { href: "/", label: "Overview", icon: LayoutDashboard },
      { href: "/documents", label: "Documents", icon: FileText },
    ],
  },
  {
    label: "Research",
    links: [
      { href: "/research", label: "Research chat", icon: MessageSquare },
      { href: "/analysis", label: "Financial analysis", icon: BarChart3 },
      { href: "/history", label: "Conversation history", icon: Clock3 },
    ],
  },
];

export default function Shell({ children }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  return (
    <div className={`app-shell ${collapsed ? "sidebar-collapsed" : ""} ${mobileOpen ? "mobile-nav-open" : ""}`}>
      <a className="skip-link" href="#main-content">Skip to content</a>
      <button className="mobile-menu-button" onClick={() => setMobileOpen(true)} aria-label="Open navigation menu"><Menu size={19} /></button>
      {mobileOpen && <button className="sidebar-backdrop" onClick={() => setMobileOpen(false)} aria-label="Close navigation menu" />}
      <aside className="sidebar">
        <button className="mobile-close-button" onClick={() => setMobileOpen(false)} aria-label="Close navigation menu"><X size={18} /></button>
        <div className="brand"><div className="brand-mark">F</div><span><strong>Folio<span className="accent">AI</span></strong><small>AI Financial Research</small></span></div>
        <nav aria-label="Primary navigation">
          {groups.map((group) => <div className="nav-group" key={group.label}>
            <div className="workspace-label">{group.label}</div>
            {group.links.map(({ href, label, icon: Icon }) => (
              <Link key={href} href={href} prefetch onClick={() => setMobileOpen(false)} className={`nav-link ${pathname === href || (href !== "/" && pathname.startsWith(`${href}/`)) ? "active" : ""}`} title={label}>
                <Icon size={18} /><span>{label}</span>
              </Link>
            ))}
          </div>)}
        </nav>
        <div className="sidebar-bottom">
          <div className="connection"><span className="status-dot" /> <span>API connected</span></div>
          <Link href="/settings" onClick={() => setMobileOpen(false)} className="nav-link"><Settings2 size={18} /><span>Settings</span></Link>
          <button className="collapse-button" onClick={() => setCollapsed(!collapsed)} aria-label="Collapse sidebar">
            {collapsed ? <ChevronRight size={17} /> : <ChevronLeft size={17} />}<span>Collapse menu</span>
          </button>
        </div>
      </aside>
      <main className="main-content" id="main-content"><header className="topbar"><div className="breadcrumb"><span>Workspace</span><b>/</b><strong>{pathname === "/" ? "Overview" : pathname.slice(1).replace("-", " ")}</strong></div><div className="topbar-actions"><Link href="/research" className="topbar-search"><Search size={14} /><span>Search documents, companies, or past research...</span><kbd>⌘ K</kbd></Link><button className="icon-button" aria-label="Notifications"><Bell size={16} /><span className="notification-dot" /></button><div className="profile-chip"><span className="profile-avatar">A</span><span className="profile-name">Aarav</span><ChevronRight size={13} className="profile-chevron" /></div></div></header>{children}</main>
    </div>
  );
}
