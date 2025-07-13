"use client"

import * as React from "react"
import { Bot } from "lucide-react"
import { ModeToggle } from "@/components/mode-toggle";
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

export function TeamSwitcher() {
  return (
    <SidebarMenu>
       <SidebarMenuItem>
        <SidebarMenuButton size="lg" className="cursor-default">
          <div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">
            <Bot className="size-4" />
          </div>
          <div className="grid flex-1 text-left text-sm leading-tight">
            <span className="truncate font-medium">Kairos</span>
            <span className="truncate text-xs">Trading Assistant</span>
          </div>
          <div>
            <ModeToggle />
          </div>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}