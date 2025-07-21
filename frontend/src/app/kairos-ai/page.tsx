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
  '10': { text: '10 minutes', minutes: 10 },
  '30': { text: '30 minutes', minutes: 30 },
  '60': { text: '1 hour', minutes: 60 },
  '120': { text: '2 hours', minutes: 120 },
  '300': { text: '5 hours', minutes: 300 },
  '720': { text: '12 hours', minutes: 720 },
  '1440': { text: '24 hours', minutes: 1440 }
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
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Session status polling
  useEffect(() => {
    if (currentSession?.status === 'active' && currentSession.sessionId) {
      const interval = setInterval(() => {
        checkSessionStatus(currentSession.sessionId)
      }, 10000) // Check every 10 seconds
      setSessionPolling(interval)
      
      return () => clearInterval(interval)
    } else if (sessionPolling) {
      clearInterval(sessionPolling)
      setSessionPolling(null)
    }
  }, [currentSession])

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
      addMessage({
        id: Date.now().toString(),
        type: 'system',
        content: `🚀 Starting autonomous trading session for ${durationData.text}...`,
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
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()

      if (data.data?.session_id) {
        const session: TradingSession = {
          sessionId: data.data.session_id,
          userId: data.data.user_id,
          status: 'active',
          duration: durationData.text,
          durationMinutes: durationData.minutes,
          endTime: data.data.end_time,
          startTime: new Date().toISOString()
        }

        setCurrentSession(session)
        setSessionDialogOpen(false)

        addMessage({
          id: Date.now().toString(),
          type: 'system',
          content: `✅ **Trading Session Started Successfully!**\n\n🆔 **Session ID:** \`${data.data.session_id.substring(0, 8)}...\`\n⏰ **Duration:** ${durationData.text}\n📅 **End Time:** ${new Date(data.data.end_time).toLocaleString()}\n\n🤖 **The AI agent is now:**\n• Analyzing market conditions\n• Making autonomous trading decisions\n• Monitoring portfolio performance\n• Learning from each trade\n\nReal-time updates will appear below...`,
          timestamp: new Date(),
          sessionId: data.data.session_id
        })
      } else {
        throw new Error('No session ID returned from server')
      }

    } catch (error) {
      console.error('Error starting trading session:', error)
      addMessage({
        id: Date.now().toString(),
        type: 'system',
        content: `❌ **Failed to start trading session**\n\nError: ${error instanceof Error ? error.message : 'Unknown error'}\n\n💡 **Troubleshooting:**\n• Ensure the API server is running on localhost:8000\n• Check your internet connection\n• Try again in a moment`,
        timestamp: new Date()
      })
    } finally {
      setIsLoading(false)
    }
  }

  const checkSessionStatus = async (sessionId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/autonomous/status/${sessionId}`)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const statusData = await response.json()

      if (statusData.session_found) {
        if (statusData.status === 'completed' && currentSession?.status === 'active') {
          // Session just completed
          setCurrentSession(prev => prev ? { ...prev, status: 'completed' } : null)
          
          addMessage({
            id: Date.now().toString(),
            type: 'session-end',
            content: `🏁 **Trading Session Completed!**\n\n📊 **Final Results:**\n• Portfolio Value: $${statusData.current_portfolio_value?.toLocaleString() || 'N/A'}\n• Session Duration: ${currentSession?.duration}\n\n📄 **Generating PDF report...**`,
            timestamp: new Date(),
            sessionId: sessionId
          })

          // Trigger PDF download
          downloadSessionReport(sessionId)
        }

        // Update session data
        if (currentSession) {
          setCurrentSession(prev => prev ? {
            ...prev,
            currentPortfolioValue: statusData.current_portfolio_value,
            status: statusData.status
          } : null)
        }
      }
    } catch (error) {
      console.error('Error checking session status:', error)
    }
  }

  const downloadSessionReport = async (sessionId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/session/report/${sessionId}`)
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.style.display = 'none'
        a.href = url
        a.download = `kairos_session_${sessionId.substring(0, 8)}_${new Date().toISOString().split('T')[0]}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)

        addMessage({
          id: Date.now().toString(),
          type: 'system',
          content: '📥 **PDF Report Downloaded!**\n\nYour trading session report has been downloaded to your default downloads folder.',
          timestamp: new Date()
        })
      }
    } catch (error) {
      console.error('Error downloading report:', error)
      addMessage({
        id: Date.now().toString(),
        type: 'system',
        content: '⚠️ **Report Download Failed**\n\nUnable to download the PDF report. The session data has been saved and you can request the report later.',
        timestamp: new Date()
      })
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
        await fetch(`http://localhost:8000/api/autonomous/stop/${currentSession.sessionId}`, {
          method: 'POST'
        })
        
        setCurrentSession(prev => prev ? { ...prev, status: 'completed' } : null)
        
        addMessage({
          id: Date.now().toString(),
          type: 'system',
          content: '⏹️ **Trading session stopped manually.**\n\nGenerating final report...',
          timestamp: new Date()
        })
      } catch (error) {
        console.error('Error stopping session:', error)
      }
    }
  }

  const quickAssistantCommands = [
    { label: "Portfolio", command: "Show my current portfolio" },
    { label: "BTC Price", command: "What's the current Bitcoin price?" },
    { label: "Crypto News", command: "Show me the latest crypto news" },
    { label: "Market Analysis", command: "Analyze the current crypto market" },
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
                            The AI will make real trading decisions and execute trades automatically. 
                            Monitor your session and ensure you have sufficient balance.
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
                  {currentSession.status === 'active' ? '🔥 Active' : '✅ Completed'}
                </Badge>
                {currentSession.currentPortfolioValue && (
                  <Badge variant="outline">
                    ${currentSession.currentPortfolioValue.toLocaleString()}
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
                    The agent will analyze market conditions and execute trades based on advanced algorithms.
                  </p>
                  <Button 
                    variant="outline" 
                    size="lg"
                    onClick={() => setSessionDialogOpen(true)}
                    className="mt-2"
                  >
                    <Play className="h-5 w-5 mr-2" />
                    Configure Trading Session
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}