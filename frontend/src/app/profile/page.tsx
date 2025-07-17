"use client"

import { useState, useEffect } from "react"
import { AppSidebar } from "@/components/app-sidebar"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AlertTriangle, Save, Eye, EyeOff, Shield, Bot, Wallet, Key, User, Mail, CheckCircle, XCircle, Trophy, Vote, Flame, Download } from "lucide-react"
import { kairosLitService } from "@/lib/kairos-lit-service"
import { AuthGuard, useAuth } from "@/hooks/useAuth"

// Avatar options for users to choose from
const avatarOptions = [
  "https://api.dicebear.com/7.x/avataaars/svg?seed=Felix",
  "https://api.dicebear.com/7.x/avataaars/svg?seed=Aneka",
  "https://api.dicebear.com/7.x/avataaars/svg?seed=Kiki",
  "https://api.dicebear.com/7.x/avataaars/svg?seed=Milo",
  "https://api.dicebear.com/7.x/avataaars/svg?seed=Zara",
  "https://api.dicebear.com/7.x/avataaars/svg?seed=Nova",
  "https://api.dicebear.com/7.x/avataaars/svg?seed=Echo",
  "https://api.dicebear.com/7.x/avataaars/svg?seed=Orion",
  "https://api.dicebear.com/7.x/avataaars/svg?seed=Luna",
  "https://api.dicebear.com/7.x/avataaars/svg?seed=Phoenix",
  "https://api.dicebear.com/7.x/avataaars/svg?seed=Sage",
  "https://api.dicebear.com/7.x/avataaars/svg?seed=Atlas"
]

interface UserProfile {
  id: string
  username: string
  email: string
  avatar_url: string
  wallet_address: string
  recall_api_key: string
  coinpanic_api_key: string
  consent_terms: boolean
  consent_risks: boolean
  consent_data: boolean
  created_at: string
  updated_at: string
}

export default function ProfilePage() {
  return (
    <AuthGuard>
      <ProfilePageContent />
    </AuthGuard>
  )
}

function ProfilePageContent() {
  const { userAddress: authUserAddress, authMethod: authAuthMethod, logout } = useAuth()
  const [profile, setProfile] = useState<UserProfile>({
    id: '',
    username: '',
    email: '',
    avatar_url: avatarOptions[0],
    wallet_address: '',
    recall_api_key: '',
    coinpanic_api_key: '',
    consent_terms: false,
    consent_risks: false,
    consent_data: false,
    created_at: '',
    updated_at: ''
  })

  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [showApiKeys, setShowApiKeys] = useState(false)
  const [showAvatarSelector, setShowAvatarSelector] = useState(false)
  const [saveMessage, setSaveMessage] = useState('')
  
  // Lit Protocol state - use auth context values
  const [isLitConnected, setIsLitConnected] = useState(true) // Already connected via auth
  const [nftPortfolio, setNftPortfolio] = useState<any>(null)
  const [premiumAccess, setPremiumAccess] = useState(false)
  
  // Use auth context values
  const userAddress = authUserAddress || ''
  const authMethod = authAuthMethod

  // Load profile when user address changes
  useEffect(() => {
    if (userAddress) {
      updateProfile('wallet_address', userAddress)
      updateProfile('id', userAddress)
      loadDecentralizedProfile()
      loadNFTPortfolio()
      checkPremiumAccess()
    }
  }, [userAddress])

  const checkPremiumAccess = async () => {
    if (userAddress) {
      const accessCheck = await kairosLitService.checkAccessNFT(userAddress, 'kairos_premium')
      setPremiumAccess(accessCheck.hasAccess)
    }
  }

  // Remove the authenticateWithWallet function since it's handled by login page

  // 📁 LOAD DECENTRALIZED PROFILE
  const loadDecentralizedProfile = async () => {
    if (!userAddress) return
    
    setIsLoading(true)
    try {
      const result = await kairosLitService.loadDecentralizedProfile(userAddress)
      if (result.profile) {
        setProfile(result.profile)
        setSaveMessage(result.message)
      } else {
        // New user - set defaults
        setProfile(prev => ({
          ...prev,
          id: userAddress,
          wallet_address: userAddress,
          created_at: new Date().toISOString()
        }))
        setSaveMessage('👋 Welcome! Creating new decentralized profile...')
      }
    } catch (error) {
      console.error('Error loading profile:', error)
      setSaveMessage('❌ Error loading profile from decentralized storage')
    }
    setIsLoading(false)
  }

  // 💾 SAVE DECENTRALIZED PROFILE
  const saveDecentralizedProfile = async () => {
    if (!userAddress || !authMethod) {
      setSaveMessage('❌ Please connect wallet first')
      return
    }

    setIsSaving(true)
    setSaveMessage('')
    
    try {
      const result = await kairosLitService.saveDecentralizedProfile(profile, userAddress)
      setSaveMessage(result.message)
      
      if (result.success) {
        setProfile(prev => ({
          ...prev,
          updated_at: new Date().toISOString()
        }))
        
        // Mint achievement for profile completion
        if (isProfileComplete) {
          await kairosLitService.mintAchievementNFT('profile_complete', userAddress, { timestamp: new Date().toISOString() })
        }
      }
    } catch (error) {
      console.error('Error saving profile:', error)
      setSaveMessage('❌ Error saving profile to decentralized storage')
    }
    
    setIsSaving(false)
    setTimeout(() => setSaveMessage(''), 5000)
  }

  // 🗝️ ENCRYPT AND SAVE API KEYS
  const saveEncryptedAPIKeys = async () => {
    if (!userAddress || !authMethod) {
      setSaveMessage('❌ Please connect wallet first')
      return
    }

    try {
      const apiKeys = {
        recall_api_key: profile.recall_api_key,
        coinpanic_api_key: profile.coinpanic_api_key
      }

      const result = await kairosLitService.encryptAndStoreAPIKeys(apiKeys, userAddress)
      setSaveMessage(result.message)
      
      if (result.success) {
        // Mint achievement for API key setup
        await kairosLitService.mintAchievementNFT('api_setup', userAddress, { timestamp: new Date().toISOString() })
      }
    } catch (error) {
      console.error('Error encrypting API keys:', error)
      setSaveMessage('❌ Failed to encrypt API keys')
    }
  }

  // 🎯 LOAD API KEYS
  const loadDecryptedAPIKeys = async () => {
    if (!userAddress) return

    try {
      const result = await kairosLitService.decryptAPIKeys(userAddress)
      if (result.success) {
        updateProfile('recall_api_key', result.apiKeys.recall_api_key)
        updateProfile('coinpanic_api_key', result.apiKeys.coinpanic_api_key)
        setSaveMessage(result.message)
      }
    } catch (error) {
      console.error('Error decrypting API keys:', error)
      setSaveMessage('❌ Failed to decrypt API keys')
    }
  }

  // 🏆 LOAD NFT PORTFOLIO
  const loadNFTPortfolio = async () => {
    if (!userAddress) return

    try {
      const result = await kairosLitService.getUserNFTPortfolio(userAddress)
      if (result.success) {
        setNftPortfolio(result.portfolio)
      }
    } catch (error) {
      console.error('Error loading NFT portfolio:', error)
    }
  }

  // 🎫 MINT DEMO NFTS
  const mintDemoNFTs = async () => {
    if (!userAddress) return

    try {
      // Mint various demo NFTs
      await kairosLitService.mintConsumableNFT('ai_boost', userAddress)
      await kairosLitService.mintGovernanceNFT(userAddress, 'early_supporter')
      
      // Reload portfolio
      await loadNFTPortfolio()
      setSaveMessage('🎁 Demo NFTs minted successfully!')
    } catch (error) {
      console.error('Error minting demo NFTs:', error)
      setSaveMessage('❌ Failed to mint demo NFTs')
    }
  }

  // 🚀 CREATE TRADING SESSION
  const createAutonomousTradingSession = async () => {
    if (!userAddress || !authMethod) {
      setSaveMessage('❌ Please connect wallet first')
      return
    }

    try {
      const sessionData = {
        authMethod,
        duration: 3600, // 1 hour
        maxTradeAmount: 1000,
        allowedTokens: ['ETH', 'USDC', 'WBTC']
      }

      const result = await kairosLitService.createAuthorizedTradingSession(sessionData, userAddress)
      setSaveMessage(result.message)
      
      if (result.success && result.pkp) {
        // Mint achievement for first trading session
        await kairosLitService.mintAchievementNFT('first_session', userAddress, { 
          sessionId: result.pkp.publicKey,
          timestamp: new Date().toISOString() 
        })
      }
    } catch (error) {
      console.error('Error creating trading session:', error)
      setSaveMessage('❌ Failed to create trading session')
    }
  }

  const updateProfile = (field: keyof UserProfile, value: any) => {
    setProfile(prev => ({ ...prev, [field]: value }))
  }

  const isProfileComplete = profile.username && profile.email && profile.recall_api_key && profile.coinpanic_api_key && profile.consent_terms && profile.consent_risks

  return (
    <SidebarProvider>
      <AppSidebar activePage="profile" />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 data-[orientation=vertical]:h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem>
                  <BreadcrumbLink href="/dashboard">Kairos</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>Profile</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>

        <div className="flex flex-1 flex-col gap-6 p-6 pt-0">
          {/* Lit Protocol Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                🔐 Decentralized Profile
                {isLitConnected && userAddress ? (
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
                {premiumAccess && (
                  <Badge className="bg-purple-500 text-white">
                    <Trophy className="h-3 w-3 mr-1" />
                    Premium
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Your profile is secured with Lit Protocol encryption and stored on IPFS. No database required!
              </p>
              {userAddress && (
                <p className="text-xs text-muted-foreground mt-2">
                  Connected: {userAddress.substring(0, 10)}...{userAddress.substring(userAddress.length - 8)}
                </p>
              )}
            </CardContent>
          </Card>

          <Tabs defaultValue="authentication" className="space-y-6">
            <TabsList className="grid w-full grid-cols-6">
              <TabsTrigger value="authentication">Connect</TabsTrigger>
              <TabsTrigger value="personal">Personal</TabsTrigger>
              <TabsTrigger value="api-keys">API Keys</TabsTrigger>
              <TabsTrigger value="nfts">NFTs</TabsTrigger>
              <TabsTrigger value="trading">Trading</TabsTrigger>
              <TabsTrigger value="consent">Consent</TabsTrigger>
            </TabsList>

            {/* Authentication Tab */}
            <TabsContent value="authentication" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>🔐 Wallet Authentication</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-4">
                    <div className="p-4 bg-green-50 dark:bg-green-950 rounded-lg">
                      <p className="text-sm text-green-700 dark:text-green-300">
                        ✅ Wallet connected and authenticated with Lit Protocol!
                      </p>
                      <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                        Address: {userAddress.substring(0, 10)}...{userAddress.substring(userAddress.length - 8)}
                      </p>
                      <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                        Your data is now encrypted and decentralized.
                      </p>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <Button onClick={loadDecryptedAPIKeys} variant="outline">
                        <Key className="h-4 w-4 mr-2" />
                        Load Encrypted Keys
                      </Button>
                      <Button onClick={mintDemoNFTs} variant="outline">
                        <Trophy className="h-4 w-4 mr-2" />
                        Mint Demo NFTs
                      </Button>
                      <Button onClick={logout} variant="destructive">
                        <XCircle className="h-4 w-4 mr-2" />
                        Logout
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Personal Tab */}
            <TabsContent value="personal" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>👤 Personal Information</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Stored on IPFS, encrypted with Lit Protocol
                  </p>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <Label>Profile Avatar</Label>
                    <div className="flex items-center gap-4">
                      <Avatar className="h-20 w-20">
                        <AvatarImage src={profile.avatar_url} />
                        <AvatarFallback>{profile.username.slice(0, 2).toUpperCase()}</AvatarFallback>
                      </Avatar>
                      <Button 
                        variant="outline" 
                        onClick={() => setShowAvatarSelector(!showAvatarSelector)}
                      >
                        Choose Avatar
                      </Button>
                    </div>
                    
                    {showAvatarSelector && (
                      <div className="grid grid-cols-6 gap-3 p-4 border rounded-lg">
                        {avatarOptions.map((avatar, index) => (
                          <Avatar 
                            key={index} 
                            className="h-12 w-12 cursor-pointer hover:ring-2 hover:ring-primary transition-all"
                            onClick={() => {
                              updateProfile('avatar_url', avatar)
                              setShowAvatarSelector(false)
                            }}
                          >
                            <AvatarImage src={avatar} />
                          </Avatar>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      value={profile.username}
                      onChange={(e) => updateProfile('username', e.target.value)}
                      placeholder="Enter your username"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      value={profile.email}
                      onChange={(e) => updateProfile('email', e.target.value)}
                      placeholder="Enter your email"
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* API Keys Tab */}
            <TabsContent value="api-keys" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Key className="h-5 w-5" />
                    🔒 Encrypted API Configuration
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    API keys are encrypted with Lit Protocol and stored on IPFS. Only you can decrypt them.
                  </p>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="recall-api">Recall API Key</Label>
                    <Input
                      id="recall-api"
                      type={showApiKeys ? "text" : "password"}
                      value={profile.recall_api_key}
                      onChange={(e) => updateProfile('recall_api_key', e.target.value)}
                      placeholder="Enter your Recall API key"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="coinpanic-api">CoinPanic API Key</Label>
                    <Input
                      id="coinpanic-api"
                      type={showApiKeys ? "text" : "password"}
                      value={profile.coinpanic_api_key}
                      onChange={(e) => updateProfile('coinpanic_api_key', e.target.value)}
                      placeholder="Enter your CoinPanic API key"
                    />
                  </div>

                  <div className="flex gap-2">
                    <Button 
                      onClick={() => setShowApiKeys(!showApiKeys)}
                      variant="outline"
                    >
                      {showApiKeys ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
                      {showApiKeys ? 'Hide' : 'Show'} Keys
                    </Button>
                    <Button 
                      onClick={saveEncryptedAPIKeys}
                      disabled={!userAddress}
                    >
                      <Shield className="h-4 w-4 mr-2" />
                      Encrypt & Store
                    </Button>
                  </div>

                  <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                    <div className="flex items-start gap-3">
                      <Shield className="h-5 w-5 text-blue-600 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-blue-900 dark:text-blue-100">No Database Storage</h4>
                        <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                          Your API keys are never stored in any database. They're encrypted with your wallet signature and stored on IPFS.
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* NFTs Tab */}
            <TabsContent value="nfts" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Trophy className="h-5 w-5" />
                    🏆 Your NFT Portfolio
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {nftPortfolio ? (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center p-4 border rounded-lg">
                          <h4 className="font-semibold">Strategies</h4>
                          <p className="text-2xl font-bold text-blue-600">{nftPortfolio.strategies?.length || 0}</p>
                        </div>
                        <div className="text-center p-4 border rounded-lg">
                          <h4 className="font-semibold">Achievements</h4>
                          <p className="text-2xl font-bold text-green-600">{nftPortfolio.achievements?.length || 0}</p>
                        </div>
                        <div className="text-center p-4 border rounded-lg">
                          <h4 className="font-semibold">Governance</h4>
                          <p className="text-2xl font-bold text-purple-600">{nftPortfolio.governance?.length || 0}</p>
                        </div>
                        <div className="text-center p-4 border rounded-lg">
                          <h4 className="font-semibold">Consumables</h4>
                          <p className="text-2xl font-bold text-orange-600">{nftPortfolio.consumables?.length || 0}</p>
                        </div>
                      </div>

                      {nftPortfolio.achievements && nftPortfolio.achievements.length > 0 && (
                        <div>
                          <h4 className="font-semibold mb-2">🎖️ Recent Achievements</h4>
                          <div className="space-y-2">
                            {nftPortfolio.achievements.slice(-3).map((achievement: any, index: number) => (
                              <div key={index} className="p-3 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800">
                                <p className="font-medium">{achievement.name}</p>
                                <p className="text-sm text-muted-foreground">{achievement.metadata.description}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Trophy className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                      <p className="text-muted-foreground">Connect your wallet to view your NFT portfolio</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Trading Tab */}
            <TabsContent value="trading" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="h-5 w-5" />
                    🚀 Autonomous Trading
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      Create secure, time-limited autonomous trading sessions using Lit Protocol PKPs.
                    </p>
                    
                    <Button 
                      onClick={createAutonomousTradingSession}
                      disabled={!userAddress}
                      className="w-full"
                    >
                      <Bot className="h-4 w-4 mr-2" />
                      Create Authorized Trading Session
                    </Button>

                    <div className="bg-yellow-50 dark:bg-yellow-950 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
                      <div className="flex items-start gap-3">
                        <Download className="h-5 w-5 text-yellow-600 mt-0.5" />
                        <div>
                          <h4 className="font-medium text-yellow-900 dark:text-yellow-100">Trading Reports Download</h4>
                          <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                            After trading sessions end, reports will be automatically downloaded to your browser. No email required!
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Consent Tab */}
            <TabsContent value="consent" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>📋 Consent & Risk Acknowledgment</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div className="flex items-start space-x-3">
                      <input
                        type="checkbox"
                        id="consent-terms"
                        checked={profile.consent_terms}
                        onChange={(e) => updateProfile('consent_terms', e.target.checked)}
                        className="mt-1"
                      />
                      <Label htmlFor="consent-terms" className="text-sm">
                        I agree to the Terms of Service and understand that this is experimental technology
                      </Label>
                    </div>

                    <div className="flex items-start space-x-3">
                      <input
                        type="checkbox"
                        id="consent-risks"
                        checked={profile.consent_risks}
                        onChange={(e) => updateProfile('consent_risks', e.target.checked)}
                        className="mt-1"
                      />
                      <Label htmlFor="consent-risks" className="text-sm">
                        I understand the risks of cryptocurrency trading and autonomous AI decision making
                      </Label>
                    </div>

                    <div className="flex items-start space-x-3">
                      <input
                        type="checkbox"
                        id="consent-data"
                        checked={profile.consent_data}
                        onChange={(e) => updateProfile('consent_data', e.target.checked)}
                        className="mt-1"
                      />
                      <Label htmlFor="consent-data" className="text-sm">
                        I consent to decentralized data storage on IPFS with Lit Protocol encryption
                      </Label>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Save Button */}
          <div className="flex items-center justify-between">
            <div className="text-sm">
              {saveMessage && (
                <span className={saveMessage.includes('✅') || saveMessage.includes('🔗') || saveMessage.includes('🏆') ? 'text-green-600' : 'text-red-600'}>
                  {saveMessage}
                </span>
              )}
            </div>
            <Button 
              onClick={saveDecentralizedProfile} 
              disabled={isSaving || !userAddress} 
              className="flex items-center gap-2"
            >
              {isSaving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Saving to IPFS...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  Save to Decentralized Storage
                </>
              )}
            </Button>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}