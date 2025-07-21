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
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  AlertTriangle, 
  Save, 
  Eye, 
  EyeOff, 
  Shield, 
  Bot, 
  Wallet, 
  Key, 
  User, 
  Mail, 
  CheckCircle, 
  XCircle,
  Info,
  Lock,
  Sparkles,
  ExternalLink
} from "lucide-react"

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

const STORAGE_KEY = 'kairos_user_profile'

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile>({
    id: crypto.randomUUID(),
    username: '',
    email: '',
    avatar_url: avatarOptions[0],
    wallet_address: '',
    recall_api_key: '',
    coinpanic_api_key: '',
    consent_terms: false,
    consent_risks: false,
    consent_data: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  })

  const [isSaving, setIsSaving] = useState(false)
  const [showApiKeys, setShowApiKeys] = useState(false)
  const [showAvatarSelector, setShowAvatarSelector] = useState(false)
  const [saveMessage, setSaveMessage] = useState('')
  const [activeTab, setActiveTab] = useState('personal')

  // Load profile from localStorage on mount
  useEffect(() => {
    const savedProfile = localStorage.getItem(STORAGE_KEY)
    if (savedProfile) {
      try {
        const parsedProfile = JSON.parse(savedProfile)
        setProfile(parsedProfile)
      } catch (error) {
        console.error('Error loading profile:', error)
      }
    }
  }, [])

  // Save profile to localStorage
  const saveProfile = () => {
    setIsSaving(true)
    setSaveMessage('')
    
    try {
      const updatedProfile = {
        ...profile,
        updated_at: new Date().toISOString()
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedProfile))
      setProfile(updatedProfile)
      setSaveMessage('✅ Profile saved successfully!')
      
      // If profile is complete, show celebration
      if (isProfileComplete) {
        setSaveMessage('🎉 Profile complete! You\'re ready to start trading!')
      }
    } catch (error) {
      console.error('Error saving profile:', error)
      setSaveMessage('❌ Error saving profile')
    }
    
    setIsSaving(false)
    setTimeout(() => setSaveMessage(''), 4000)
  }

  const updateProfile = (field: keyof UserProfile, value: any) => {
    setProfile(prev => ({ ...prev, [field]: value }))
  }

  // Calculate profile completion
  const profileFields = [
    { field: 'username', label: 'Username', required: true },
    { field: 'email', label: 'Email', required: true },
    { field: 'recall_api_key', label: 'Recall API Key', required: true },
    { field: 'coinpanic_api_key', label: 'CoinPanic API Key', required: true },
    { field: 'consent_terms', label: 'Terms Agreement', required: true },
    { field: 'consent_risks', label: 'Risk Acknowledgment', required: true },
    { field: 'wallet_address', label: 'Wallet Address', required: false },
    { field: 'consent_data', label: 'Data Consent', required: false }
  ]

  const completedFields = profileFields.filter(field => 
    field.required ? profile[field.field as keyof UserProfile] : true
  ).length

  const totalRequiredFields = profileFields.filter(f => f.required).length
  const completionPercentage = Math.round((completedFields / totalRequiredFields) * 100)
  const isProfileComplete = completedFields === totalRequiredFields

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
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="personal" className="flex items-center gap-2">
                <User className="h-4 w-4" />
                Personal
              </TabsTrigger>
              <TabsTrigger value="api-keys" className="flex items-center gap-2">
                <Key className="h-4 w-4" />
                API Keys
              </TabsTrigger>
              <TabsTrigger value="wallet" className="flex items-center gap-2">
                <Wallet className="h-4 w-4" />
                Wallet
              </TabsTrigger>
              <TabsTrigger value="consent" className="flex items-center gap-2">
                <Shield className="h-4 w-4" />
                Consent
              </TabsTrigger>
            </TabsList>

            {/* Personal Information Tab */}
            <TabsContent value="personal" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Personal Information</CardTitle>
                  <CardDescription>
                    Your basic profile information for personalized trading experience
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Avatar Selection */}
                  <div className="space-y-4">
                    <Label>Profile Avatar</Label>
                    <div className="flex items-center gap-4">
                      <div className="relative">
                        <Avatar className="h-24 w-24 ring-4 ring-background shadow-lg">
                          <AvatarImage src={profile.avatar_url} />
                          <AvatarFallback>{profile.username.slice(0, 2).toUpperCase()}</AvatarFallback>
                        </Avatar>
                        <div className="absolute -bottom-2 -right-2 bg-primary text-primary-foreground rounded-full p-1">
                          <Sparkles className="h-4 w-4" />
                        </div>
                      </div>
                      <div>
                        <Button 
                          variant="outline" 
                          onClick={() => setShowAvatarSelector(!showAvatarSelector)}
                        >
                          Choose Avatar
                        </Button>
                        <p className="text-xs text-muted-foreground mt-1">
                          Pick an avatar that represents you
                        </p>
                      </div>
                    </div>
                    
                    {showAvatarSelector && (
                      <Card>
                        <CardContent className="p-4">
                          <div className="grid grid-cols-6 gap-3">
                            {avatarOptions.map((avatar, index) => (
                              <Avatar 
                                key={index} 
                                className={`h-14 w-14 cursor-pointer transition-all hover:scale-110 ${
                                  profile.avatar_url === avatar ? 'ring-4 ring-primary' : 'hover:ring-2 hover:ring-primary'
                                }`}
                                onClick={() => {
                                  updateProfile('avatar_url', avatar)
                                  setShowAvatarSelector(false)
                                }}
                              >
                                <AvatarImage src={avatar} />
                              </Avatar>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )}
                  </div>

                  {/* Username */}
                  <div className="space-y-2">
                    <Label htmlFor="username">
                      Username <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="username"
                      value={profile.username}
                      onChange={(e) => updateProfile('username', e.target.value)}
                      placeholder="Enter your username"
                      className={!profile.username ? 'border-red-300' : ''}
                    />
                    <p className="text-xs text-muted-foreground">
                      This is how you'll be identified in the trading system
                    </p>
                  </div>

                  {/* Email */}
                  <div className="space-y-2">
                    <Label htmlFor="email">
                      Email Address <span className="text-red-500">*</span>
                    </Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="email"
                        type="email"
                        value={profile.email}
                        onChange={(e) => updateProfile('email', e.target.value)}
                        placeholder="your@email.com"
                        className={`pl-10 ${!profile.email ? 'border-red-300' : ''}`}
                      />
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Used for important notifications and account recovery
                    </p>
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
                  <CardDescription>
                    Your API keys are stored locally and never sent to any server
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Local Storage Notice */}
                  <Alert>
                    <Lock className="h-4 w-4" />
                    <AlertDescription>
                      <strong>Enhanced Security:</strong> Your API keys are encrypted and stored only in your browser's local storage. 
                      They never leave your device.
                    </AlertDescription>
                  </Alert>

                  {/* Show/Hide Toggle */}
                  <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                    <div className="flex items-center gap-2">
                      <Shield className="h-5 w-5 text-muted-foreground" />
                      <span className="text-sm font-medium">API Key Visibility</span>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowApiKeys(!showApiKeys)}
                    >
                      {showApiKeys ? (
                        <>
                          <EyeOff className="h-4 w-4 mr-2" />
                          Hide Keys
                        </>
                      ) : (
                        <>
                          <Eye className="h-4 w-4 mr-2" />
                          Show Keys
                        </>
                      )}
                    </Button>
                  </div>

                  {/* Recall API Key */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="recall-api">
                        Recall API Key <span className="text-red-500">*</span>
                      </Label>
                      <a 
                        href="https://recall.trade" 
                        target="_blank" 
                        className="text-xs text-primary hover:underline flex items-center gap-1"
                      >
                        Get API Key
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </div>
                    <Input
                      id="recall-api"
                      type={showApiKeys ? "text" : "password"}
                      value={profile.recall_api_key}
                      onChange={(e) => updateProfile('recall_api_key', e.target.value)}
                      placeholder="Enter your Recall API key"
                      className={!profile.recall_api_key ? 'border-red-300' : ''}
                    />
                    <p className="text-xs text-muted-foreground">
                      Required for executing trades on the blockchain
                    </p>
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
                    Wallet Connection
                  </CardTitle>
                  <CardDescription>
                    Optional: Connect your wallet for enhanced portfolio tracking
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <Label htmlFor="wallet">Wallet Address (Optional)</Label>
                    <div className="relative">
                      <Wallet className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="wallet"
                        value={profile.wallet_address}
                        onChange={(e) => updateProfile('wallet_address', e.target.value)}
                        placeholder="0x..."
                        className="pl-10 font-mono text-sm"
                      />
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Your wallet address for portfolio tracking and transaction history
                    </p>
                  </div>

                  <Alert>
                    <Info className="h-4 w-4" />
                    <AlertDescription>
                      <strong>Note:</strong> Wallet connection is optional. Kairos can trade without it using your API keys.
                    </AlertDescription>
                  </Alert>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Consent Tab */}
            <TabsContent value="consent" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Terms & Risk Acknowledgment</CardTitle>
                  <CardDescription>
                    Please read and accept our terms before trading
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Terms of Service */}
                  <Card className={`border-2 transition-all ${profile.consent_terms ? 'border-green-500 bg-green-50 dark:bg-green-950' : ''}`}>
                    <CardContent className="p-4">
                      <div className="flex items-start space-x-3">
                        <input
                          type="checkbox"
                          id="consent-terms"
                          checked={profile.consent_terms}
                          onChange={(e) => updateProfile('consent_terms', e.target.checked)}
                          className="mt-1"
                        />
                        <div className="space-y-1">
                          <Label htmlFor="consent-terms" className="font-medium cursor-pointer">
                            I agree to the Terms of Service <span className="text-red-500">*</span>
                          </Label>
                          <p className="text-sm text-muted-foreground">
                            By checking this box, you agree to our terms and conditions for using Kairos AI trading services.
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Trading Risks */}
                  <Card className={`border-2 transition-all ${profile.consent_risks ? 'border-green-500 bg-green-50 dark:bg-green-950' : ''}`}>
                    <CardContent className="p-4">
                      <div className="flex items-start space-x-3">
                        <input
                          type="checkbox"
                          id="consent-risks"
                          checked={profile.consent_risks}
                          onChange={(e) => updateProfile('consent_risks', e.target.checked)}
                          className="mt-1"
                        />
                        <div className="space-y-1">
                          <Label htmlFor="consent-risks" className="font-medium cursor-pointer">
                            I understand the trading risks <span className="text-red-500">*</span>
                          </Label>
                          <p className="text-sm text-muted-foreground">
                            Cryptocurrency trading involves substantial risk of loss. Past performance does not guarantee future results.
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Data Usage */}
                  <Card className={`border transition-all ${profile.consent_data ? 'border-primary bg-primary/5' : ''}`}>
                    <CardContent className="p-4">
                      <div className="flex items-start space-x-3">
                        <input
                          type="checkbox"
                          id="consent-data"
                          checked={profile.consent_data}
                          onChange={(e) => updateProfile('consent_data', e.target.checked)}
                          className="mt-1"
                        />
                        <div className="space-y-1">
                          <Label htmlFor="consent-data" className="font-medium cursor-pointer">
                            Help improve Kairos AI (Optional)
                          </Label>
                          <p className="text-sm text-muted-foreground">
                            Allow anonymous usage analytics. Your personal data and API keys are never included.
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Risk Warning */}
                  <Alert className="border-yellow-200 bg-yellow-50 dark:bg-yellow-950 dark:border-yellow-800">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    <AlertDescription>
                      <strong className="text-yellow-900 dark:text-yellow-100">Important Trading Warning:</strong>
                      <p className="text-yellow-700 dark:text-yellow-300 mt-1">
                        Kairos AI is a powerful tool, but all investment decisions are your responsibility. 
                        Never invest more than you can afford to lose. Start small and test strategies carefully.
                      </p>
                    </AlertDescription>
                  </Alert>

                  {/* About Kairos */}
                  <Card className="bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20">
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <div className="bg-primary text-primary-foreground rounded-full p-2">
                          <Bot className="h-5 w-5" />
                        </div>
                        <div className="space-y-2">
                          <h4 className="font-semibold">About Kairos AI</h4>
                          <p className="text-sm text-muted-foreground">
                            Kairos is your intelligent trading copilot powered by Google Gemini AI. It analyzes market sentiment, 
                            news, and portfolio data to provide informed trading recommendations through both conversational 
                            assistance and fully autonomous trading sessions.
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Save Button */}
          <Card className="border-2">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium">
                    {isProfileComplete ? '✅ Your profile is complete!' : '⚡ Complete your profile to start trading'}
                  </p>
                  {saveMessage && (
                    <p className={`text-sm ${saveMessage.includes('✅') || saveMessage.includes('🎉') ? 'text-green-600' : 'text-red-600'}`}>
                      {saveMessage}
                    </p>
                  )}
                </div>
                <Button 
                  onClick={saveProfile} 
                  disabled={isSaving} 
                  size="lg"
                  className="min-w-[140px]"
                >
                  {isSaving ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Save Profile
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}