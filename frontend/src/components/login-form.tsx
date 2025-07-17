"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Wallet, Shield, CheckCircle, XCircle, Loader2 } from "lucide-react"
import { kairosLitService } from "@/lib/kairos-lit-service"
import { useAuth } from "@/hooks/useAuth"

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { login } = useAuth()
  const [isConnecting, setIsConnecting] = useState(false)
  const [isLitConnected, setIsLitConnected] = useState(false)
  const [message, setMessage] = useState('')
  const [userAddress, setUserAddress] = useState('')

  const handleWalletLogin = async () => {
    setIsConnecting(true)
    setMessage('')
    
    try {
      console.log('🚀 Starting wallet login process...')
      
      // Initialize Lit Protocol if not already connected
      if (!isLitConnected) {
        console.log('🔗 Connecting to Lit Protocol...')
        const connectResult = await kairosLitService.connect()
        if (connectResult.success) {
          setIsLitConnected(true)
          setMessage('🔗 Lit Protocol connected!')
          console.log('✅ Lit Protocol connected successfully')
        } else {
          console.error('❌ Lit Protocol connection failed:', connectResult.message)
          setMessage(connectResult.message)
          setIsConnecting(false)
          return
        }
      }

      // Authenticate with wallet
      console.log('🔐 Authenticating with wallet...')
      const result = await kairosLitService.authenticateWithWallet()
      console.log('🔐 Wallet authentication result:', result)
      
      if (result.success && result.address) {
        setUserAddress(result.address)
        setMessage(`✅ Welcome! Redirecting...`)
        console.log('✅ Authentication successful, address:', result.address)
        
        // Use auth context to set authentication
        console.log('🔄 Setting authentication in context...')
        login({
          address: result.address,
          authMethod: result.authMethod
        })
        
        // Mint achievement NFT for first wallet connection
        console.log('🏆 Minting achievement NFT...')
        await kairosLitService.mintAchievementNFT('first_connection', result.address, { timestamp: new Date().toISOString() })
        
        // Redirect to intended page or dashboard
        const redirectTo = searchParams.get('redirect') || '/dashboard'
        console.log('🚀 Redirecting to:', redirectTo)
        setTimeout(() => {
          console.log('🔄 Executing redirect...')
          router.push(redirectTo)
        }, 1500)
      } else {
        console.error('❌ Authentication failed:', result.message)
        setMessage(result.message)
      }
    } catch (error) {
      console.error('❌ Login failed with error:', error)
      setMessage('❌ Login failed. Please try again.')
    }
    
    setIsConnecting(false)
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card className="w-full max-w-md mx-auto">
        <CardHeader className="text-center">
          <CardTitle className="flex items-center justify-center gap-2 text-2xl font-bold">
            <Shield className="h-6 w-6" />
            Kairos Login
          </CardTitle>
          <CardDescription>
            Connect your wallet to access Kairos trading platform
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Lit Protocol Status */}
          <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
            <span className="text-sm font-medium">Lit Protocol</span>
            {isLitConnected ? (
              <Badge className="bg-green-500 text-white">
                <CheckCircle className="h-3 w-3 mr-1" />
                Connected
              </Badge>
            ) : (
              <Badge variant="destructive">
                <XCircle className="h-3 w-3 mr-1" />
                Not Connected
              </Badge>
            )}
          </div>

          {/* Wallet Connection */}
          {!userAddress ? (
            <Button 
              onClick={handleWalletLogin} 
              disabled={isConnecting}
              className="w-full h-12 text-lg"
            >
              {isConnecting ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Connecting...
                </>
              ) : (
                <>
                  <Wallet className="h-5 w-5 mr-2" />
                  Connect Wallet & Login
                </>
              )}
            </Button>
          ) : (
            <div className="p-4 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="font-medium text-green-800 dark:text-green-200">
                  Wallet Connected!
                </span>
              </div>
              <p className="text-sm text-green-700 dark:text-green-300">
                {userAddress.substring(0, 10)}...{userAddress.substring(userAddress.length - 8)}
              </p>
            </div>
          )}

          {/* Status Message */}
          {message && (
            <div className="text-center p-3 rounded-lg bg-muted">
              <p className={`text-sm ${message.includes('✅') || message.includes('🔗') ? 'text-green-600' : 'text-red-600'}`}>
                {message}
              </p>
            </div>
          )}

          {/* Benefits */}
          <div className="space-y-3">
            <h4 className="font-medium text-sm text-muted-foreground">With Kairos you get:</h4>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-blue-500" />
                <span>Decentralized profile & encrypted API keys</span>
              </div>
              <div className="flex items-center gap-2">
                <Wallet className="h-4 w-4 text-purple-500" />
                <span>No database - everything on IPFS</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span>Autonomous trading with Lit Protocol PKPs</span>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center text-xs text-muted-foreground">
            <p>Secure, decentralized, and fully on-chain</p>
            <p className="mt-1">No email, no passwords, no databases</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
