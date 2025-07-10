"use client"

import * as React from "react"
import {
  AudioWaveform,
  Book,
  BookOpen,
  Bot,
  Command,
  Frame,
  GalleryVerticalEnd,
  History,
  LogOut,
  Map,
  PieChart,
  Settings2,
  SquareTerminal,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavProjects } from "@/components/nav-projects"
import { NavUser } from "@/components/nav-user"
import { TeamSwitcher } from "@/components/team-switcher"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar"

// This is sample data.
const data = {
  user: {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  },
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: SquareTerminal,
      isActive: true,
    },
    {
      title: "Manual Trading",
      url: "/manual-trade",
      icon: PieChart, // Added graph icon here
    },
    {
      title: "AI Agent",
      url: "/ai-agent",
      icon: Bot,
    },
    {
      title: "Vincent Police",
      url: "/vincent",
      icon: Book,
    },
    {
      title: "Trade History",
      url: "/trade-history",
      icon: History,
    },
    {
      title: "Logout",
      url: "/logout",
      icon: LogOut,
    },
  ],
}

export function AppSidebar({ 
  activePage,
  ...props 
}: React.ComponentProps<typeof Sidebar> & { activePage?: string }) {
  // Update the data based on active page
  const data = {
    user: {
      name: "shadcn",
      email: "m@example.com",
      avatar: "/avatars/shadcn.jpg",
    },
    navMain: [
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
        title: "AI Agent",
        url: "/ai-agent",
        icon: Bot,
        isActive: activePage === "ai-agent",
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
        title: "Logout",
        url: "/logout",
        icon: LogOut,
        isActive: activePage === "logout",
      },
    ],
  }

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <TeamSwitcher />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
