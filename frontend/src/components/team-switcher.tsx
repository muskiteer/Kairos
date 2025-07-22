"use client"

import * as React from "react"
import { Logo } from "@/components/navbar/logo"
// import { ModeToggle } from "@/components/mode-toggle"
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"

export function TeamSwitcher() {
  const { state } = useSidebar()
  const isCollapsed = state === "collapsed"

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <SidebarMenuButton size="lg" className="cursor-default">
          {/* Show only the K logo when collapsed, full logo when expanded */}
          {isCollapsed ? (
            <div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">
              <svg
                width="16"
                height="16"
                viewBox="0 0 32 32"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="text-sidebar-primary-foreground"
              >
                {/* Vertical bar */}
                <rect x="10" y="8" width="2.5" height="16" rx="1" className="fill-current" />
                {/* Upper diagonal */}
                <path
                  d="M13 16 L21.5 9.5 C22 9 23 9.5 23.5 10 L24.5 11 C25 11.5 24 12.5 23.5 13 L16 17 Z"
                  className="fill-current"
                />
                {/* Lower diagonal */}
                <path
                  d="M13 16 L21.5 22.5 C22 23 23 22.5 23.5 22 L24.5 21 C25 20.5 24 19.5 23.5 19 L16 15 Z"
                  className="fill-current"
                />
              </svg>
            </div>
          ) : (
            <Logo />
          )}
          
          {!isCollapsed && (
            <div className="grid flex-1 text-left text-sm leading-tight ml-2">
              <span className="truncate text-xs opacity-70">Trading Assistant</span>
            </div>
          )}
          
          {/* Only show ModeToggle when sidebar is expanded */}
          {/* <div className={`transition-opacity duration-200 ${isCollapsed ? 'opacity-0 w-0 overflow-hidden' : 'opacity-100'}`}>
            <ModeToggle />
          </div> */}
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}