"use client"

import * as React from "react"
import {
  Book,
  Bot,
  History,
  PieChart,
  SquareTerminal,
  User
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavUser } from "@/components/nav-user"
import { TeamSwitcher } from "@/components/team-switcher"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar"

interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {
  activePage?: string
}

export function AppSidebar({ activePage, ...props }: AppSidebarProps) {
  // Navigation items with proper active state handling
  const navItems = [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: SquareTerminal,
      isActive: activePage === "dashboard",
    },
    {
      title: "Manual Trading",
      url: "/manual-trade",
      icon: PieChart,
      isActive: activePage === "manual-trade",
    },
    {
      title: "Kairos AI",
      url: "/kairos-ai",
      icon: Bot,
      isActive: activePage === "kairos-ai",
    },
    {
      title: "Vincent Police",
      url: "/vincent",
      icon: Book,
      isActive: activePage === "vincent",
    },
    {
      title: "Trade History",
      url: "/trade-history",
      icon: History,
      isActive: activePage === "trade-history",
    },
    {
      title: "Profile",
      url: "/profile",
      icon: User,
      isActive: activePage === "profile",
    },
  ]

  return (
    <Sidebar 
      collapsible="icon" 
      className="border-r border-sidebar-border"
      {...props}
    >
      <SidebarHeader>
        <TeamSwitcher />
      </SidebarHeader>
      
      <SidebarContent>
        <NavMain items={navItems} />
      </SidebarContent>
      
      <SidebarFooter>
        <NavUser />
      </SidebarFooter>
      
      <SidebarRail />
    </Sidebar>
  )
}