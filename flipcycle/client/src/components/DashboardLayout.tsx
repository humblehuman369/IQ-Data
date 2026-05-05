import { useAuth } from "@/_core/hooks/useAuth";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader, SidebarInset, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarProvider, SidebarTrigger, useSidebar } from "@/components/ui/sidebar";
import { getLoginUrl } from "@/const";
import { useIsMobile } from "@/hooks/useMobile";
import { BarChart3, BriefcaseBusiness, Calculator, FileText, KanbanSquare, LogOut, PanelLeft, ReceiptText, Users } from "lucide-react";
import { CSSProperties, useEffect, useRef, useState } from "react";
import { useLocation } from "wouter";
import { DashboardLayoutSkeleton } from "./DashboardLayoutSkeleton";
import { Button } from "./ui/button";

const menuItems = [
  { icon: BarChart3, label: "Overview", path: "/dashboard" },
  { icon: Calculator, label: "Deal Analyzer", path: "/dashboard/analyzer" },
  { icon: KanbanSquare, label: "Pipeline", path: "/dashboard/pipeline" },
  { icon: ReceiptText, label: "Budgets", path: "/dashboard/budgets" },
  { icon: FileText, label: "Documents", path: "/dashboard/documents" },
  { icon: Users, label: "Team", path: "/dashboard/team" },
];

const SIDEBAR_WIDTH_KEY = "flipcycle-sidebar-width";
const DEFAULT_WIDTH = 292;
const MIN_WIDTH = 220;
const MAX_WIDTH = 440;

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [sidebarWidth, setSidebarWidth] = useState(() => {
    const saved = localStorage.getItem(SIDEBAR_WIDTH_KEY);
    return saved ? parseInt(saved, 10) : DEFAULT_WIDTH;
  });
  const { loading, user } = useAuth();

  useEffect(() => {
    localStorage.setItem(SIDEBAR_WIDTH_KEY, sidebarWidth.toString());
  }, [sidebarWidth]);

  if (loading) return <DashboardLayoutSkeleton />;

  if (!user) {
    return (
      <div className="grid-fade flex min-h-screen items-center justify-center px-4">
        <div className="soft-panel flex w-full max-w-md flex-col items-center gap-7 rounded-[2rem] p-8 text-center">
          <div className="brand-gradient flex h-14 w-14 items-center justify-center rounded-2xl text-white shadow-lg shadow-sky-300/30">
            <BriefcaseBusiness className="h-7 w-7" aria-hidden="true" />
          </div>
          <div className="space-y-3">
            <h1 className="text-3xl font-semibold tracking-tight">Sign in to FlipCycle</h1>
            <p className="text-sm leading-6 text-muted-foreground">Your portfolio dashboard, deal analyzer, budgets, documents, and team tools are protected with Manus OAuth.</p>
          </div>
          <Button onClick={() => { window.location.href = getLoginUrl(); }} size="lg" className="brand-gradient w-full border-0 text-white shadow-lg shadow-sky-300/30 hover:opacity-95">
            Continue with Manus OAuth
          </Button>
          <a href="/" className="text-sm font-medium text-primary hover:underline">Return to public site</a>
        </div>
      </div>
    );
  }

  return (
    <SidebarProvider style={{ "--sidebar-width": `${sidebarWidth}px` } as CSSProperties}>
      <DashboardLayoutContent setSidebarWidth={setSidebarWidth}>{children}</DashboardLayoutContent>
    </SidebarProvider>
  );
}

type DashboardLayoutContentProps = { children: React.ReactNode; setSidebarWidth: (width: number) => void };

function DashboardLayoutContent({ children, setSidebarWidth }: DashboardLayoutContentProps) {
  const { user, logout } = useAuth();
  const [location, setLocation] = useLocation();
  const { state, toggleSidebar } = useSidebar();
  const isCollapsed = state === "collapsed";
  const [isResizing, setIsResizing] = useState(false);
  const sidebarRef = useRef<HTMLDivElement>(null);
  const activeMenuItem = menuItems.find(item => item.path === location) ?? menuItems.find(item => location.startsWith(item.path) && item.path !== "/dashboard") ?? menuItems[0];
  const isMobile = useIsMobile();

  useEffect(() => { if (isCollapsed) setIsResizing(false); }, [isCollapsed]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      const sidebarLeft = sidebarRef.current?.getBoundingClientRect().left ?? 0;
      const newWidth = e.clientX - sidebarLeft;
      if (newWidth >= MIN_WIDTH && newWidth <= MAX_WIDTH) setSidebarWidth(newWidth);
    };
    const handleMouseUp = () => setIsResizing(false);
    if (isResizing) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
    }
    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
  }, [isResizing, setSidebarWidth]);

  return (
    <>
      <div className="relative" ref={sidebarRef}>
        <Sidebar collapsible="icon" className="border-r-0 bg-sidebar text-sidebar-foreground" disableTransition={isResizing}>
          <SidebarHeader className="h-20 justify-center border-b border-white/10">
            <div className="flex w-full items-center gap-3 px-2 transition-all">
              <button onClick={toggleSidebar} className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-sidebar-foreground/75 transition-colors hover:bg-white/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring" aria-label="Toggle navigation">
                <PanelLeft className="h-4 w-4" />
              </button>
              {!isCollapsed ? (
                <button onClick={() => setLocation("/dashboard")} className="flex min-w-0 items-center gap-3 text-left">
                  <span className="brand-gradient flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl text-white shadow-lg shadow-sky-950/30"><BriefcaseBusiness className="h-5 w-5" /></span>
                  <span className="min-w-0"><span className="block truncate text-base font-semibold tracking-tight text-white">FlipCycle</span><span className="block truncate text-xs text-sky-100/70">Flip operations</span></span>
                </button>
              ) : null}
            </div>
          </SidebarHeader>
          <SidebarContent className="gap-0 py-3">
            <SidebarMenu className="px-2 py-1">
              {menuItems.map(item => {
                const isActive = item.path === "/dashboard" ? location === item.path : location.startsWith(item.path);
                return (
                  <SidebarMenuItem key={item.path}>
                    <SidebarMenuButton isActive={isActive} onClick={() => setLocation(item.path)} tooltip={item.label} className="h-11 rounded-xl font-medium text-sidebar-foreground/78 transition-all hover:bg-white/10 data-[active=true]:bg-white data-[active=true]:text-slate-950">
                      <item.icon className={`h-4 w-4 ${isActive ? "text-primary" : "text-sky-100/70"}`} />
                      <span>{item.label}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarContent>
          <SidebarFooter className="border-t border-white/10 p-3">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex w-full items-center gap-3 rounded-xl px-2 py-2 text-left transition-colors hover:bg-white/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring group-data-[collapsible=icon]:justify-center">
                  <Avatar className="h-10 w-10 shrink-0 border border-white/20"><AvatarFallback className="brand-gradient text-xs font-semibold text-white">{user?.name?.charAt(0).toUpperCase() || "W"}</AvatarFallback></Avatar>
                  <div className="min-w-0 flex-1 group-data-[collapsible=icon]:hidden"><p className="truncate text-sm font-medium leading-none text-white">{user?.name || "FlipCycle User"}</p><p className="mt-1.5 truncate text-xs text-sky-100/70">{user?.email || "Signed in"}</p></div>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48"><DropdownMenuItem onClick={logout} className="cursor-pointer text-destructive focus:text-destructive"><LogOut className="mr-2 h-4 w-4" /><span>Sign out</span></DropdownMenuItem></DropdownMenuContent>
            </DropdownMenu>
          </SidebarFooter>
        </Sidebar>
        <div className={`absolute right-0 top-0 h-full w-1 cursor-col-resize transition-colors hover:bg-primary/20 ${isCollapsed ? "hidden" : ""}`} onMouseDown={() => { if (!isCollapsed) setIsResizing(true); }} style={{ zIndex: 50 }} />
      </div>
      <SidebarInset>
        {isMobile && (
          <div className="sticky top-0 z-40 flex h-14 items-center justify-between border-b bg-background/95 px-2 backdrop-blur supports-[backdrop-filter]:backdrop-blur">
            <div className="flex items-center gap-2"><SidebarTrigger className="h-9 w-9 rounded-lg bg-background" /><span className="font-medium tracking-tight text-foreground">{activeMenuItem?.label ?? "Menu"}</span></div>
          </div>
        )}
        <main className="grid-fade min-h-screen flex-1 p-4 sm:p-6 lg:p-8">{children}</main>
      </SidebarInset>
    </>
  );
}
