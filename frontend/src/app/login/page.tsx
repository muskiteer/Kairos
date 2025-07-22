"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { LoginForm } from "@/components/login-form"
import { Logo } from "@/components/navbar/logo"
import { Loader2 } from "lucide-react"

export default function LoginPage() {
  const router = useRouter()
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)
  const [shouldRedirect, setShouldRedirect] = useState(false)

  useEffect(() => {
    // Check if user is already authenticated
    const checkAuthStatus = () => {
      try {
        const savedWallet = localStorage.getItem('kairos_wallet')
        if (savedWallet) {
          const walletInfo = JSON.parse(savedWallet)
          if (walletInfo?.isConnected && walletInfo?.address) {
            // User is already authenticated, set redirect flag
            setShouldRedirect(true)
            return
          }
        }
      } catch (error) {
        console.error('Error checking auth status:', error)
        // Clear corrupted data
        localStorage.removeItem('kairos_wallet')
      }
      
      setIsCheckingAuth(false)
    }

    // Small delay to prevent flash
    const timer = setTimeout(checkAuthStatus, 100)
    return () => clearTimeout(timer)
  }, [])

  // Handle redirect in a separate effect to avoid loops
  useEffect(() => {
    if (shouldRedirect) {
      router.replace('/dashboard')
    }
  }, [shouldRedirect, router])

  // Show loading spinner while checking authentication
  if (isCheckingAuth || shouldRedirect) {
    return (
      <div className="bg-background flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
        <div className="flex flex-col items-center gap-4">
          <Logo />
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">
            {shouldRedirect ? 'Redirecting to dashboard...' : 'Checking authentication...'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-background flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center gap-6 mb-6">
          <Logo />
        </div>
        <LoginForm />
      </div>
    </div>
  )
}