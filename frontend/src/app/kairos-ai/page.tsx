"use client"

import { useState, useRef, useEffect } from "react"
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
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { 
  Bot, 
  User, 
  Send, 
  TrendingUp, 
  Wallet, 
  DollarSign, 
  Activity, 
  Loader2,
  Play,
  Pause,
  Download,
  Clock,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  MessageSquare,
  Settings,
  RefreshCw
} from "lucide-react"

interface Message {
  id: string
  type: 'user' | 'ai' | 'system' | 'trading-update' | 'session-end'
  content: string
  timestamp: Date
  intent?: string
  confidence?: number
  isStreaming?: boolean
  sessionId?: string
  tradeData?: any
}

interface TradingSession {
  sessionId: string
  userId: string
  status: 'active' | 'completed' | 'failed'
  duration: string
  durationMinutes: number
  endTime: string
  currentPortfolioValue?: number
  totalTrades?: number
  successfulTrades?: number
  totalPnL?: number
  startTime: string
}

type AIMode = 'agent' | 'assistant'

const DURATION_OPTIONS = {
  '5': { text: '5 minutes', minutes: 5 },
  '10': { text: '10 minutes', minutes: 10 },
  '15': { text: '15 minutes', minutes: 15 },
  '30': { text: '30 minutes', minutes: 30 },
  '60': { text: '1 hour', minutes: 60 },
  '120': { text: '2 hours', minutes: 120 },
  '300': { text: '5 hours', minutes: 300 },
  '720': { text: '12 hours', minutes: 720 }
}

export default function AIAgentPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: '🤖 **Kairos AI** is online and ready!\n\n**Two Modes Available:**\n\n🔥 **Agent Mode** - Autonomous trading sessions with real-time execution\n💬 **Assistant Mode** - Interactive chat with market data access\n\nSelect your preferred mode to get started!',
      timestamp: new Date(),
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [aiMode, setAiMode] = useState<AIMode>('assistant')
  const [selectedDuration, setSelectedDuration] = useState('')
  const [currentSession, setCurrentSession] = useState<TradingSession | null>(null)
  const [sessionDialogOpen, setSessionDialogOpen] = useState(false)
  const [sessionPolling, setSessionPolling] = useState<NodeJS.Timeout | null>(null)
  const [pollingCount, setPollingCount] = useState(0)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Enhanced session status polling with retry logic
  useEffect(() => {
    if (currentSession?.status === 'active' && currentSession.sessionId) {
      console.log(`🔄 Starting polling for session: ${currentSession.sessionId}`)
      
      const interval = setInterval(async () => {
        try {
          setPollingCount(prev => prev + 1)
          await checkSessionStatus(currentSession.sessionId)
        } catch (error) {
          console.error('Polling error:', error)
        }
      }, 5000) // Check every 5 seconds for faster updates
      
      setSessionPolling(interval)
      
      return () => {
        console.log('🛑 Stopping session polling')
        clearInterval(interval)
      }
    } else if (sessionPolling) {
      clearInterval(sessionPolling)
      setSessionPolling(null)
      setPollingCount(0)
    }
  }, [currentSession?.status, currentSession?.sessionId])

  const formatMessage = (content: string) => {
    const lines = content.split('\n')
    return lines.map((line, index) => {
      if (line.startsWith('## ')) {
        return <h2 key={index} className="text-lg font-bold mt-4 mb-2 text-primary">{line.slice(3)}</h2>
      }
      if (line.startsWith('# ')) {
        return <h1 key={index} className="text-xl font-bold mt-4 mb-2 text-primary">{line.slice(2)}</h1>
      }
      
      if (line.includes('**')) {
        const parts = line.split('**')
        return (
          <p key={index} className="mb-2">
            {parts.map((part, partIndex) => 
              partIndex % 2 === 1 ? <strong key={partIndex} className="font-semibold text-foreground">{part}</strong> : part
            )}
          </p>
        )
      }
      
      if (line.startsWith('• ') || line.startsWith('- ')) {
        return <li key={index} className="ml-4 mb-1 list-disc">{line.slice(2)}</li>
      }
      
      if (/^\d+\.\s/.test(line)) {
        return <li key={index} className="ml-4 mb-1 list-decimal">{line.replace(/^\d+\.\s/, '')}</li>
      }
      
      if (line.includes('===') || line.includes('---')) {
        return <hr key={index} className="my-4 border-border" />
      }
      
      if (line.includes('🎯') || line.includes('📊') || line.includes('💰') || line.includes('🔥')) {
        return <p key={index} className="mb-2 text-sm font-medium text-primary">{line}</p>
      }
      
      if (line.trim()) {
        return <p key={index} className="mb-2 text-muted-foreground">{line}</p>
      }
      
      return <br key={index} />
    })
  }

  const downloadSessionReport = async (sessionId: string) => {
    try {
      console.log(`📄 Starting download for session: ${sessionId}`)
      
      addMessage({
        id: Date.now().toString(),
        type: 'system',
        content: '📄 **Generating your trading report...**\n\nCreating comprehensive PDF with all session data, trades, and AI analysis.',
        timestamp: new Date()
      })

      const response = await fetch(`http://localhost:8000/api/session/report/${sessionId}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/pdf',
        },
      })
      
      if (!response.ok) {
        throw new Error(`Failed to generate report: ${response.status} ${response.statusText}`)
      }

      const blob = await response.blob()
      
      if (blob.size === 0) {
        throw new Error('Empty PDF file received')
      }

      // Create download
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      const timestamp = new Date().toISOString().split('T')[0]
      const shortSessionId = sessionId.substring(0, 8)
      link.download = `Kairos_Trading_Report_${shortSessionId}_${timestamp}.pdf`
      
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      console.log('✅ PDF download completed successfully')

      addMessage({
        id: Date.now().toString(),
        type: 'system',
        content: `✅ **Report Downloaded Successfully!**\n\n📥 **File:** Kairos_Trading_Report_${shortSessionId}_${timestamp}.pdf\n📁 **Location:** Your browser's downloads folder\n\n📊 **Report includes:**\n• Complete session analysis\n• AI decision breakdown\n• Trade execution details\n• Portfolio performance\n• Risk assessment\n\n🎉 **Session completed successfully!**`,
        timestamp: new Date()
      })

    } catch (error) {
      console.error('Download error:', error)
      
      addMessage({
        id: Date.now().toString(),
        type: 'system',
        content: `❌ **Download Failed**\n\nError: ${error instanceof Error ? error.message : 'Unknown error'}\n\n🔧 **Try this:**\n• Manual download: [Click here](http://localhost:8000/api/session/report/${sessionId})\n• Check if backend server is running\n• Refresh page and try again`,
        timestamp: new Date()
      })
    }
  }

  const startTradingSession = async () => {
    if (!selectedDuration) {
      addMessage({
        id: Date.now().toString(),
        type: 'system',
        content: '⚠️ Please select a trading duration first.',
        timestamp: new Date()
      })
      return
    }

    setIsLoading(true)
    const durationData = DURATION_OPTIONS[selectedDuration as keyof typeof DURATION_OPTIONS]

    try {
      console.log(`🚀 Starting trading session for ${durationData.minutes} minutes`)
      
      addMessage({
        id: Date.now().toString(),
        type: 'system',
        content: `🚀 **Initializing Trading Session...**\n\n⏰ Duration: ${durationData.text}\n🤖 Starting AI agent...\n📊 Analyzing market conditions...\n\nPlease wait...`,
        timestamp: new Date()
      })

      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: `Start autonomous trading for ${durationData.text}`,
          duration_minutes: durationData.minutes,
          user_id: `web_user_${Date.now()}`
        }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }

      const data = await response.json()
      console.log('📡 Session response:', data)

      if (data.data?.session_id) {
        const session: TradingSession = {
          sessionId: data.data.session_id,
          userId: data.data.user_id,
          status: 'active',
          duration: durationData.text,
          durationMinutes: durationData.minutes,
          endTime: data.data.end_time,
          startTime: new Date().toISOString(),
          currentPortfolioValue: data.data.initial_portfolio_value
        }

        setCurrentSession(session)
        setSessionDialogOpen(false)
        console.log(`✅ Session created: ${session.sessionId}`)

        addMessage({
          id: Date.now().toString(),
          type: 'system',
          content: `✅ **AUTONOMOUS TRADING ACTIVATED!**\n\n🆔 **Session:** \`${session.sessionId.substring(0, 12)}...\`\n⏰ **Duration:** ${durationData.text}\n🏁 **Ends at:** ${new Date(data.data.end_time).toLocaleTimeString()}\n💰 **Starting Value:** $${data.data.initial_portfolio_value?.toLocaleString() || 'Unknown'}\n\n🤖 **AI Agent Status:**\n• ✅ Portfolio analysis complete\n• ✅ Market data connected\n• ✅ Trading engine active\n• ⏳ Making first decision...\n\n📊 **Live updates will appear below...**`,
          timestamp: new Date(),
          sessionId: session.sessionId
        })

        // Start immediate status checking
        setTimeout(() => checkSessionStatus(session.sessionId), 2000)
        
      } else {
        throw new Error('No session ID returned from server')
      }

    } catch (error) {
      console.error('❌ Session start error:', error)
      addMessage({
        id: Date.now().toString(),
        type: 'system',
        content: `❌ **Failed to Start Trading Session**\n\nError: ${error instanceof Error ? error.message : 'Unknown error'}\n\n🔧 **Troubleshooting:**\n• Ensure backend server is running on localhost:8000\n• Check browser console for detailed errors\n• Verify your internet connection\n• Try starting with a shorter duration\n\n💡 **Manual check:** Visit http://localhost:8000/health`,
        timestamp: new Date()
      })
    } finally {
      setIsLoading(false)
    }
  }

  const checkSessionStatus = async (sessionId: string) => {
    try {
      console.log(`🔍 Checking status for session: ${sessionId} (poll #${pollingCount})`)
      
      const response = await fetch(`http://localhost:8000/api/autonomous/status/${sessionId}`, {
        method: 'GET',
        cache: 'no-cache'
      })
      
      if (!response.ok) {
        console.warn(`⚠️ Status check failed: ${response.status}`)
        return
      }

      const statusData = await response.json()
      console.log('📊 Status response:', statusData)

      if (statusData.session_found) {
        
        // Update current session data
        if (currentSession && statusData.current_portfolio_value) {
          setCurrentSession(prev => prev ? {
            ...prev,
            currentPortfolioValue: statusData.current_portfolio_value,
            status: statusData.status
          } : null)
        }

        // Check if session just completed
        if (statusData.status === 'completed' && currentSession?.status === 'active') {
          console.log('🏁 Session completed! Updating UI...')
          
          setCurrentSession(prev => prev ? { ...prev, status: 'completed' } : null)
          
          addMessage({
            id: Date.now().toString(),
            type: 'session-end',
            content: `🏁 **TRADING SESSION COMPLETED!**\n\n📊 **Final Results:**\n• Session ID: \`${sessionId.substring(0, 12)}...\`\n• Duration: ${currentSession?.duration}\n• Final Portfolio: $${statusData.current_portfolio_value?.toLocaleString() || 'Unknown'}\n• Status: ${statusData.status.toUpperCase()}\n\n📄 **Generating comprehensive PDF report...**\n⏳ Download will start automatically in 3 seconds...`,
            timestamp: new Date(),
            sessionId: sessionId
          })

          // Auto-download report after session completion
          setTimeout(() => {
            downloadSessionReport(sessionId)
          }, 3000)
        }

        // Add periodic status updates for active sessions
        if (statusData.status === 'active' && pollingCount % 6 === 0) { // Every 30 seconds
          addMessage({
            id: Date.now().toString(),
            type: 'trading-update',
            content: `🔄 **Session Update** (${Math.floor(pollingCount * 5 / 60)} min)\n\n• Status: ACTIVE 🟢\n• Portfolio: $${statusData.current_portfolio_value?.toLocaleString() || 'Updating...'}\n• AI is analyzing market conditions...\n\n⏰ Time remaining: ~${Math.max(0, Math.ceil((currentSession?.durationMinutes || 0) - (pollingCount * 5 / 60)))} minutes`,
            timestamp: new Date()
          })
        }

      } else {
        console.warn('⚠️ Session not found in status check')
        if (pollingCount > 20) { // Stop polling after 100 seconds of no response
          addMessage({
            id: Date.now().toString(),
            type: 'system',
            content: '⚠️ **Lost connection to trading session**\n\nThe session may have completed or there may be a connection issue. Check the backend logs for more information.',
            timestamp: new Date()
          })
          setCurrentSession(prev => prev ? { ...prev, status: 'completed' } : null)
        }
      }
    } catch (error) {
      console.error('Status check error:', error)
      if (pollingCount > 30) { // Stop after many failures
        setCurrentSession(prev => prev ? { ...prev, status: 'failed' } : null)
      }
    }
  }

  const sendAssistantMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    addMessage(userMessage)
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/chat/assistant', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          timestamp: userMessage.timestamp.toISOString(),
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()

      addMessage({
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: data.response,
        timestamp: new Date(),
        intent: data.intent,
        confidence: data.confidence,
      })

    } catch (error) {
      console.error('Error sending message:', error)
      
      addMessage({
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `❌ **Connection Error**\n\nI'm having trouble connecting to the backend. Please make sure the AI agent server is running on \`localhost:8000\`.\n\n💡 **To start the server:**\n\`\`\`bash\ncd backend\npython api_server.py\n\`\`\`\n\nThen try your message again!`,
        timestamp: new Date(),
      })
    } finally {
      setIsLoading(false)
    }
  }

  const addMessage = (message: Message) => {
    setMessages(prev => [...prev, message])
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (aiMode === 'assistant') {
        sendAssistantMessage()
      }
    }
  }

  const stopSession = async () => {
    if (currentSession?.sessionId) {
      try {
        console.log(`🛑 Stopping session: ${currentSession.sessionId}`)
        
        const response = await fetch(`http://localhost:8000/api/autonomous/stop/${currentSession.sessionId}`, {
          method: 'POST'
        })
        
        if (response.ok) {
          setCurrentSession(prev => prev ? { ...prev, status: 'completed' } : null)
          
          addMessage({
            id: Date.now().toString(),
            type: 'system',
            content: '⏹️ **Trading session stopped manually**\n\nGenerating final report and downloading...',
            timestamp: new Date()
          })

          // Download report after manual stop
          setTimeout(() => {
            downloadSessionReport(currentSession.sessionId)
          }, 2000)
        }
      } catch (error) {
        console.error('Error stopping session:', error)
        addMessage({
          id: Date.now().toString(),
          type: 'system',
          content: '⚠️ **Error stopping session**\n\nThere was an issue stopping the session. It may have already completed.',
          timestamp: new Date()
        })
      }
    }
  }

  const quickAssistantCommands = [
    { label: "💼 Portfolio", command: "Show my current portfolio and balances" },
    { label: "₿ BTC Price", command: "What's the current Bitcoin price and market analysis?" },
    { label: "📰 Crypto News", command: "Show me the latest cryptocurrency news" },
    { label: "📊 Market Analysis", command: "Analyze the current crypto market conditions" },
  ]

  return (
    <SidebarProvider>
      <AppSidebar activePage="ai-agent" />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator
              orientation="vertical"
              className="mr-2 data-[orientation=vertical]:h-4"
            />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem>
                  <BreadcrumbLink href="/dashboard">Kairos</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>AI Agent</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>

        <div className="flex flex-1 flex-col gap-6 p-6 pt-0 h-full">
          {/* AI Mode Selector & Session Controls */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium">AI Mode:</label>
                <Select value={aiMode} onValueChange={(value: AIMode) => setAiMode(value)}>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="assistant">
                      <div className="flex items-center gap-2">
                        <MessageSquare className="h-4 w-4" />
                        Assistant
                      </div>
                    </SelectItem>
                    <SelectItem value="agent">
                      <div className="flex items-center gap-2">
                        <Bot className="h-4 w-4" />
                        Agent
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {aiMode === 'agent' && (
                <div className="flex items-center gap-2">
                  <Dialog open={sessionDialogOpen} onOpenChange={setSessionDialogOpen}>
                    <DialogTrigger asChild>
                      <Button 
                        variant="default" 
                        size="sm"
                        disabled={currentSession?.status === 'active'}
                      >
                        <Play className="h-4 w-4 mr-2" />
                        Start Trading
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>🤖 Start Autonomous Trading Session</DialogTitle>
                        <DialogDescription>
                          Select the duration for your AI trading session. The agent will make autonomous decisions and execute real trades.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div>
                          <label className="text-sm font-medium">Trading Duration:</label>
                          <Select value={selectedDuration} onValueChange={setSelectedDuration}>
                            <SelectTrigger>
                              <SelectValue placeholder="Select duration" />
                            </SelectTrigger>
                            <SelectContent>
                              {Object.entries(DURATION_OPTIONS).map(([key, option]) => (
                                <SelectItem key={key} value={key}>
                                  <div className="flex items-center gap-2">
                                    <Clock className="h-4 w-4" />
                                    {option.text}
                                  </div>
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <Alert>
                          <AlertTriangle className="h-4 w-4" />
                          <AlertDescription>
                            <strong>Real Trading Alert:</strong> The AI will execute actual trades with your portfolio. 
                            Monitor the session and ensure sufficient balance. A PDF report will be automatically downloaded when complete.
                          </AlertDescription>
                        </Alert>
                        <div className="flex gap-2">
                          <Button 
                            onClick={startTradingSession} 
                            disabled={!selectedDuration || isLoading}
                            className="flex-1"
                          >
                            {isLoading ? (
                              <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Starting...
                              </>
                            ) : (
                              <>
                                <Play className="h-4 w-4 mr-2" />
                                Start Session
                              </>
                            )}
                          </Button>
                          <Button variant="outline" onClick={() => setSessionDialogOpen(false)}>
                            Cancel
                          </Button>
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>

                  {currentSession?.status === 'active' && (
                    <Button variant="destructive" size="sm" onClick={stopSession}>
                      <Pause className="h-4 w-4 mr-2" />
                      Stop Session
                    </Button>
                  )}
                </div>
              )}
            </div>

            {/* Session Status */}
            {currentSession && (
              <div className="flex items-center gap-2">
                <Badge variant={currentSession.status === 'active' ? 'default' : 'secondary'}>
                  {currentSession.status === 'active' ? '🔥 Active' : 
                   currentSession.status === 'completed' ? '✅ Completed' : '❌ Failed'}
                </Badge>
                {currentSession.currentPortfolioValue && (
                  <Badge variant="outline">
                    ${currentSession.currentPortfolioValue.toLocaleString()}
                  </Badge>
                )}
                {currentSession.status === 'active' && (
                  <Badge variant="outline">
                    Poll #{pollingCount}
                  </Badge>
                )}
              </div>
            )}
          </div>

          {/* Main Chat Interface - Full Height */}
          <div className="flex-1 flex flex-col min-h-0">
            {/* Chat Header */}
            <div className="flex items-center justify-between pb-4">
              <div className="flex items-center gap-2">
                {aiMode === 'agent' ? (
                  <>
                    <Bot className="h-6 w-6 text-primary" />
                    <h2 className="text-xl font-semibold">Autonomous Trading Agent</h2>
                    <Badge variant="outline" className="ml-2">
                      🔥 Real Trading
                    </Badge>
                  </>
                ) : (
                  <>
                    <MessageSquare className="h-6 w-6 text-primary" />
                    <h2 className="text-xl font-semibold">AI Assistant</h2>
                    <Badge variant="outline" className="ml-2">
                      💬 Interactive Chat
                    </Badge>
                  </>
                )}
              </div>
              
              {/* Debug info */}
              {currentSession?.status === 'active' && (
                <div className="text-xs text-muted-foreground">
                  Checking status every 5s | Session: {currentSession.sessionId.substring(0, 8)}...
                </div>
              )}
            </div>

            {/* Messages Area - Flexible Height */}
            <ScrollArea className="flex-1 rounded-lg border bg-background p-0">
              <div className="space-y-6 p-6">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-4 ${
                      message.type === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {message.type !== 'user' && (
                      <Avatar className="h-10 w-10 flex-shrink-0">
                        <AvatarFallback className={
                          message.type === 'system' ? 'bg-blue-500 text-white' : 
                          message.type === 'trading-update' ? 'bg-green-500 text-white' :
                          message.type === 'session-end' ? 'bg-purple-500 text-white' :
                          'bg-primary text-primary-foreground'
                        }>
                          {message.type === 'system' ? '⚡' : 
                           message.type === 'trading-update' ? '📈' :
                           message.type === 'session-end' ? '🏁' :
                           <Bot className="h-5 w-5" />}
                        </AvatarFallback>
                      </Avatar>
                    )}
                    
                    <div
                      className={`max-w-[85%] rounded-xl p-4 ${
                        message.type === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : message.type === 'system'
                          ? 'bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800'
                          : message.type === 'trading-update'
                          ? 'bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800'
                          : message.type === 'session-end'
                          ? 'bg-purple-50 dark:bg-purple-950 border border-purple-200 dark:border-purple-800'
                          : 'bg-muted'
                      }`}
                    >
                      {message.type === 'user' ? (
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                      ) : (
                        <div className="text-sm leading-relaxed">
                          {formatMessage(message.content)}
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between mt-3 pt-2 border-t border-current/10">
                        <span className="text-xs opacity-70">
                          {message.timestamp.toLocaleTimeString()}
                        </span>
                        {message.intent && (
                          <div className="flex items-center gap-1">
                            <Badge variant="secondary" className="text-xs">
                              {message.intent}
                            </Badge>
                            {message.confidence && (
                              <Badge variant="outline" className="text-xs">
                                {Math.round(message.confidence * 100)}%
                              </Badge>
                            )}
                          </div>
                        )}
                        {message.sessionId && (
                          <div className="flex items-center gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 px-2 text-xs"
                              onClick={() => downloadSessionReport(message.sessionId!)}
                            >
                              <Download className="h-3 w-3 mr-1" />
                              PDF
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {message.type === 'user' && (
                      <Avatar className="h-10 w-10 flex-shrink-0">
                        <AvatarFallback className="bg-secondary">
                          <User className="h-5 w-5" />
                        </AvatarFallback>
                      </Avatar>
                    )}
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex gap-4 justify-start">
                    <Avatar className="h-10 w-10">
                      <AvatarFallback className="bg-primary text-primary-foreground">
                        <Bot className="h-5 w-5" />
                      </AvatarFallback>
                    </Avatar>
                    <div className="bg-muted rounded-xl p-4">
                      <div className="flex items-center gap-3">
                        <Loader2 className="h-5 w-5 animate-spin" />
                        <span className="text-sm text-muted-foreground">
                          {aiMode === 'agent' ? 'Starting trading session...' : 'AI is thinking...'}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div ref={messagesEndRef} />
            </ScrollArea>

            {/* Input Area - Only show for Assistant mode */}
            {aiMode === 'assistant' && (
              <div className="pt-6">
                {/* Quick Commands */}
                <div className="flex flex-wrap gap-2 mb-4 justify-center">
                  {quickAssistantCommands.map((cmd, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      className="text-xs"
                      onClick={() => setInput(cmd.command)}
                      disabled={isLoading}
                    >
                      {cmd.label}
                    </Button>
                  ))}
                </div>

                {/* Centered Input Container */}
                <div className="max-w-4xl mx-auto">
                  <div className="relative">
                    <Textarea
                      ref={inputRef}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask me about crypto prices, news, market analysis, trading strategies..."
                      disabled={isLoading}
                      className="min-h-[100px] pr-12 text-base resize-none rounded-xl border-2 focus:border-primary transition-colors"
                      rows={3}
                    />
                    <Button 
                      onClick={sendAssistantMessage} 
                      disabled={!input.trim() || isLoading}
                      size="icon"
                      className="absolute bottom-3 right-3 h-10 w-10 rounded-full"
                    >
                      {isLoading ? (
                        <Loader2 className="h-5 w-5 animate-spin" />
                      ) : (
                        <Send className="h-5 w-5" />
                      )}
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground text-center mt-2">
                    Press Enter to send, Shift+Enter for new line
                  </p>
                </div>
              </div>
            )}

            {/* Agent Mode Info Panel */}
            {aiMode === 'agent' && !currentSession && (
              <div className="pt-6">
                <div className="max-w-2xl mx-auto text-center space-y-4 p-6 rounded-xl bg-muted/50">
                  <h3 className="text-lg font-medium">🤖 Autonomous Trading Agent</h3>
                  <p className="text-muted-foreground">
                    Start a trading session to let the AI make autonomous trading decisions for you.
                    The agent will analyze market conditions, execute trades, and generate a comprehensive PDF report when complete.
                  </p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="p-3 bg-background rounded-lg">
                      <div className="font-medium mb-1">✅ What it does:</div>
                      <ul className="text-muted-foreground space-y-1 text-xs">
                        <li>• Real-time market analysis</li>
                        <li>• Autonomous trade execution</li>
                        <li>• Risk management</li>
                        <li>• PDF report generation</li>
                      </ul>
                    </div>
                    <div className="p-3 bg-background rounded-lg">
                      <div className="font-medium mb-1">⚠️ Important:</div>
                      <ul className="text-muted-foreground space-y-1 text-xs">
                        <li>• Uses real trading APIs</li>
                        <li>• Requires sufficient balance</li>
                        <li>• Cannot be undone</li>
                        <li>• Monitor the session</li>
                      </ul>
                    </div>
                  </div>
                  <Button 
                    variant="outline" 
                    size="lg"
                    onClick={() => setSessionDialogOpen(true)}
                    className="mt-4"
                  >
                    <Play className="h-5 w-5 mr-2" />
                    Configure Trading Session
                  </Button>
                </div>
              </div>
            )}

            {/* Active Session Dashboard */}
            {aiMode === 'agent' && currentSession?.status === 'active' && (
              <div className="pt-6">
                <Card className="max-w-2xl mx-auto">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Activity className="h-5 w-5 text-green-500" />
                      Live Trading Session
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <div className="text-sm font-medium">Session ID</div>
                        <div className="text-xs font-mono bg-muted px-2 py-1 rounded">
                          {currentSession.sessionId.substring(0, 16)}...
                        </div>
                      </div>
                      <div className="space-y-1">
                        <div className="text-sm font-medium">Duration</div>
                        <div className="text-xs">{currentSession.duration}</div>
                      </div>
                      <div className="space-y-1">
                        <div className="text-sm font-medium">Portfolio Value</div>
                        <div className="text-sm font-semibold text-green-600">
                          ${currentSession.currentPortfolioValue?.toLocaleString() || 'Updating...'}
                        </div>
                      </div>
                      <div className="space-y-1">
                        <div className="text-sm font-medium">Status Checks</div>
                        <div className="text-xs text-muted-foreground">
                          #{pollingCount} (every 5s)
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex gap-2 pt-2">
                      <Button 
                        variant="destructive" 
                        size="sm" 
                        onClick={stopSession}
                        className="flex-1"
                      >
                        <Pause className="h-4 w-4 mr-2" />
                        Stop Session
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => checkSessionStatus(currentSession.sessionId)}
                      >
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}