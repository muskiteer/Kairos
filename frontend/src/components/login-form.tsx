"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Bot, Wallet, CheckCircle, AlertTriangle, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useAuth } from "@/hooks/use-auth"

declare global {
  interface Window {
    ethereum?: any
  }
}

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { login, isAuthenticated, isLoading } = useAuth()
  
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState("")
  const [isMetaMaskInstalled, setIsMetaMaskInstalled] = useState(false)
  const [hasRedirected, setHasRedirected] = useState(false)

  // Get redirect destination
  const redirectTo = searchParams.get('from') || '/dashboard'

  // Check if MetaMask is installed
  useEffect(() => {
    const checkMetaMask = () => {
      if (typeof window !== "undefined" && window.ethereum) {
        setIsMetaMaskInstalled(true)
      }
    }

    checkMetaMask()
  }, [])

  // Handle redirect only once when authenticated
  useEffect(() => {
    if (!isLoading && isAuthenticated && !hasRedirected) {
      setHasRedirected(true)
      
      // Use replace to prevent back button issues
      router.replace(redirectTo)
    }
  }, [isAuthenticated, isLoading, router, redirectTo, hasRedirected])

  const connectWallet = async () => {
    if (!isMetaMaskInstalled) {
      setError("MetaMask is not installed. Please install MetaMask to continue.")
      return
    }

    setIsConnecting(true)
    setError("")

    try {
      // Request account access
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      })

      if (accounts.length > 0) {
        const chainId = await window.ethereum.request({ method: 'eth_chainId' })
        
        const walletInfo = {
          address: accounts[0],
          chainId,
          isConnected: true
        }

        // Use the auth hook to login
        login(walletInfo)
        
        // Don't manually redirect here - let the useEffect handle it
        console.log('Wallet connected successfully')
      }
    } catch (error: any) {
      console.error('Error connecting wallet:', error)
      
      if (error.code === 4001) {
        setError("Connection rejected. Please accept the connection request to continue.")
      } else {
        setError(`Failed to connect wallet: ${error.message || 'Unknown error'}`)
      }
    } finally {
      setIsConnecting(false)
    }
  }

  // Show loading spinner while checking authentication or redirecting
  if (isLoading) {
    return (
      <div className="flex flex-col items-center gap-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    )
  }

  // Show redirecting state when authenticated
  if (isAuthenticated || hasRedirected) {
    return (
      <div className="flex flex-col items-center gap-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">Redirecting to dashboard...</p>
      </div>
    )
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col items-center gap-2">
          {/* <div className="flex size-12 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <Bot className="size-8" />
          </div> */}
          <h1 className="text-2xl font-bold">Welcome to Kairos AI</h1>
          <p className="text-center text-sm text-muted-foreground">
            Connect your wallet to access autonomous crypto trading powered by AI
          </p>
          {redirectTo !== '/dashboard' && (
            <p className="text-center text-xs text-muted-foreground">
              You'll be redirected to: {redirectTo}
            </p>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <Alert className="border-red-200 bg-red-50 dark:bg-red-950">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-700 dark:text-red-300">
              {error}
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-4">
          {/* MetaMask Connection */}
          <Button 
            onClick={connectWallet}
            disabled={isConnecting || !isMetaMaskInstalled}
            className="w-full"
            size="lg"
          >
            {isConnecting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Connecting...
              </>
            ) : (
              <>
                <Wallet className="mr-2 h-4 w-4" />
                Connect with MetaMask
              </>
            )}
          </Button>

          {/* Install MetaMask Button */}
          {!isMetaMaskInstalled && (
            <Button 
              variant="outline"
              onClick={() => window.open('https://metamask.io/download/', '_blank')}
              className="w-full"
            >
              <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Install MetaMask
            </Button>
          )}

          {/* Supported Wallets Info */}
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-2">Supported Wallets</p>
            <div className="flex justify-center space-x-4">
              <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                <Wallet className="h-3 w-3" />
                <span>MetaMask</span>
              </div>
            </div>
          </div>
        </div>

        {/* Features Preview */}
        <div className="space-y-3 p-4 bg-muted rounded-lg">
          <h3 className="font-medium text-sm">What you get with Kairos AI:</h3>
          <div className="space-y-2 text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-3 w-3 text-green-600" />
              <span>Autonomous AI trading powered by Gemini</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-3 w-3 text-green-600" />
              <span>Multi-chain portfolio management</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-3 w-3 text-green-600" />
              <span>Real-time market analysis and insights</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-3 w-3 text-green-600" />
              <span>Professional trading reports</span>
            </div>
          </div>
        </div>
      </div>

      <div className="text-muted-foreground text-center text-xs text-balance">
        By connecting your wallet, you agree to our{" "}
        <a href="#" className="underline underline-offset-4 hover:text-primary">
          Terms of Service
        </a>{" "}
        and{" "}
        <a href="#" className="underline underline-offset-4 hover:text-primary">
          Privacy Policy
        </a>
        .
      </div>
    </div>
  )
}