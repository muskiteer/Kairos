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
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AlertTriangle, Save, Eye, EyeOff, Shield, Bot, Wallet, Key, User, Mail, CheckCircle, XCircle } from "lucide-react"

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

  // Load profile data on component mount
  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/profile', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        const data = await response.json()
        setProfile(data.profile || profile)
      }
    } catch (error) {
      console.error('Error loading profile:', error)
    }
    setIsLoading(false)
  }

  const saveProfile = async () => {
    setIsSaving(true)
    setSaveMessage('')
    
    try {
      const response = await fetch('http://localhost:8000/api/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile })
      })
      
      if (response.ok) {
        const data = await response.json()
        setSaveMessage('✅ Profile saved successfully!')
        setProfile(data.profile)
      } else {
        setSaveMessage('❌ Failed to save profile')
      }
    } catch (error) {
      console.error('Error saving profile:', error)
      setSaveMessage('❌ Error saving profile')
    }
    
    setIsSaving(false)
    setTimeout(() => setSaveMessage(''), 3000)
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
          {/* Profile Completion Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Profile Setup
                {isProfileComplete ? (
                  <Badge className="bg-green-500 text-white">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Complete
                  </Badge>
                ) : (
                  <Badge variant="destructive">
                    <XCircle className="h-3 w-3 mr-1" />
                    Incomplete
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Complete your profile to start trading with Kairos AI. Your API keys are securely stored and never shared.
              </p>
            </CardContent>
          </Card>

          <Tabs defaultValue="personal" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="personal">Personal</TabsTrigger>
              <TabsTrigger value="api-keys">API Keys</TabsTrigger>
              <TabsTrigger value="wallet">Wallet</TabsTrigger>
              <TabsTrigger value="consent">Consent</TabsTrigger>
            </TabsList>

            {/* Personal Information Tab */}
            <TabsContent value="personal" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Personal Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Avatar Selection */}
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

                  {/* Username */}
                  <div className="space-y-2">
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      value={profile.username}
                      onChange={(e) => updateProfile('username', e.target.value)}
                      placeholder="Enter your username"
                    />
                  </div>

                  {/* Email */}
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
                    API Configuration
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Your API keys are encrypted and stored securely. They're used dynamically by the backend without hardcoding.
                  </p>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Show/Hide API Keys Toggle */}
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowApiKeys(!showApiKeys)}
                    >
                      {showApiKeys ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      {showApiKeys ? 'Hide' : 'Show'} API Keys
                    </Button>
                  </div>

                  {/* Recall API Key */}
                  <div className="space-y-2">
                    <Label htmlFor="recall-api">Recall API Key</Label>
                    <Input
                      id="recall-api"
                      type={showApiKeys ? "text" : "password"}
                      value={profile.recall_api_key}
                      onChange={(e) => updateProfile('recall_api_key', e.target.value)}
                      placeholder="Enter your Recall API key"
                    />
                    <p className="text-xs text-muted-foreground">
                      Required for trade execution. Get yours at{" "}
                      <a href="https://recall.trade" target="_blank" className="text-primary hover:underline">
                        recall.trade
                      </a>
                    </p>
                  </div>

                  {/* CoinPanic API Key */}
                  <div className="space-y-2">
                    <Label htmlFor="coinpanic-api">CoinPanic API Key</Label>
                    <Input
                      id="coinpanic-api"
                      type={showApiKeys ? "text" : "password"}
                      value={profile.coinpanic_api_key}
                      onChange={(e) => updateProfile('coinpanic_api_key', e.target.value)}
                      placeholder="Enter your CoinPanic API key"
                    />
                    <p className="text-xs text-muted-foreground">
                      Required for market news analysis. Get yours at{" "}
                      <a href="https://cryptopanic.com/developers/api/" target="_blank" className="text-primary hover:underline">
                        cryptopanic.com
                      </a>
                    </p>
                  </div>

                  {/* API Security Notice */}
                  <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                    <div className="flex items-start gap-3">
                      <Shield className="h-5 w-5 text-blue-600 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-blue-900 dark:text-blue-100">Secure API Storage</h4>
                        <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                          Your API keys are encrypted in our database and only accessible to your trading sessions. 
                          We never log or share your keys with third parties.
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Wallet Tab */}
            <TabsContent value="wallet" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Wallet className="h-5 w-5" />
                    Connected Wallet
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="wallet">Wallet Address</Label>
                    <Input
                      id="wallet"
                      value={profile.wallet_address}
                      onChange={(e) => updateProfile('wallet_address', e.target.value)}
                      placeholder="0x... (Optional - for portfolio tracking)"
                    />
                    <p className="text-xs text-muted-foreground">
                      Connect your wallet for enhanced portfolio tracking and transaction history.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Consent Tab */}
            <TabsContent value="consent" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Terms & Consent</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Terms of Service */}
                  <div className="flex items-start space-x-3">
                    <input
                      type="checkbox"
                      id="consent-terms"
                      checked={profile.consent_terms}
                      onChange={(e) => updateProfile('consent_terms', e.target.checked)}
                      className="mt-1"
                    />
                    <div>
                      <Label htmlFor="consent-terms" className="font-medium">
                        I agree to the Terms of Service
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        By checking this box, you agree to our terms and conditions for using Kairos AI trading services.
                      </p>
                    </div>
                  </div>

                  {/* Trading Risks */}
                  <div className="flex items-start space-x-3">
                    <input
                      type="checkbox"
                      id="consent-risks"
                      checked={profile.consent_risks}
                      onChange={(e) => updateProfile('consent_risks', e.target.checked)}
                      className="mt-1"
                    />
                    <div>
                      <Label htmlFor="consent-risks" className="font-medium">
                        I understand the trading risks
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        Cryptocurrency trading involves substantial risk of loss. Past performance does not guarantee future results.
                      </p>
                    </div>
                  </div>

                  {/* Data Usage */}
                  <div className="flex items-start space-x-3">
                    <input
                      type="checkbox"
                      id="consent-data"
                      checked={profile.consent_data}
                      onChange={(e) => updateProfile('consent_data', e.target.checked)}
                      className="mt-1"
                    />
                    <div>
                      <Label htmlFor="consent-data" className="font-medium">
                        Data usage consent (Optional)
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        Allow anonymous usage analytics to improve Kairos AI. Your API keys and personal data are never included.
                      </p>
                    </div>
                  </div>

                  {/* Trading Warning */}
                  <div className="bg-yellow-50 dark:bg-yellow-950 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-yellow-900 dark:text-yellow-100">Important Trading Warning</h4>
                        <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                          Kairos AI is a powerful trading tool, but all investment decisions are ultimately your responsibility. 
                          Never invest more than you can afford to lose. Start with small amounts and test strategies carefully.
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* About Kairos AI */}
                  <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                    <div className="flex items-start gap-3">
                      <Bot className="h-5 w-5 text-primary mt-0.5" />
                      <div>
                        <h4 className="font-medium">About Kairos AI</h4>
                        <p className="text-sm text-muted-foreground mt-1">
                          Kairos is an intelligent trading copilot powered by Google Gemini AI. It analyzes market sentiment, 
                          news, and portfolio data to provide informed trading recommendations. The system supports both 
                          conversational trading assistance and fully autonomous trading sessions with customizable parameters.
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Save Button */}
          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              {saveMessage && (
                <span className={saveMessage.includes('✅') ? 'text-green-600' : 'text-red-600'}>
                  {saveMessage}
                </span>
              )}
            </div>
            <Button onClick={saveProfile} disabled={isSaving} className="flex items-center gap-2">
              {isSaving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  Save Profile
                </>
              )}
            </Button>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}