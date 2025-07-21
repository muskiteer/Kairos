"use client"

import { ReactNode } from 'react'
import { AuthProvider } from '@/hooks/use-auth'
import { ThemeProvider } from '@/components/theme-provider'

interface AppProviderProps {
  children: ReactNode
}

export function AppProvider({ children }: AppProviderProps) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <AuthProvider>
        {children}
      </AuthProvider>
    </ThemeProvider>
  )
}