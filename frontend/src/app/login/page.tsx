"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { LoginForm } from "@/components/login-form"
import { Loader2 } from "lucide-react"

export default function LoginPage() {
  const router = useRouter()
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)

  useEffect(() => {
    // Check if user is already authenticated
    const checkAuthStatus = () => {
      try {
        const savedWallet = localStorage.getItem('kairos_wallet')
        if (savedWallet) {
          const walletInfo = JSON.parse(savedWallet)
          if (walletInfo.isConnected && walletInfo.address) {
            // User is already authenticated, redirect to dashboard
            router.push('/dashboard')
            return
          }
        }
      } catch (error) {
        console.error('Error checking auth status:', error)
      }
      
      setIsCheckingAuth(false)
    }

    // Small delay to prevent flash
    const timer = setTimeout(checkAuthStatus, 100)
    return () => clearTimeout(timer)
  }, [router])

  // Show loading spinner while checking authentication
  if (isCheckingAuth) {
    return (
      <div className="bg-background flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Checking authentication...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-background flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="w-full max-w-sm">
        <LoginForm />
      </div>
    </div>
  )
}