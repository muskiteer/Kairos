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
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { getApiUrl } from '@/lib/config'
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
  Activity, 
  Loader2,
  Play,
  Pause,
  Download,
  Clock,
  AlertTriangle,
  MessageSquare,
  RefreshCw
} from "lucide-react"

interface Message {
  id: string
  type: 'user' | 'ai' | 'system' | 'trading-update' | 'session-end'
  content: string
  timestamp: Date
  intent?: string
  confidence?: number
  sessionId?: string
}

interface TradingSession {
  sessionId: string
  userId: string
  status: 'active' | 'completed' | 'failed'
  duration: string
  durationMinutes: number
  endTime: string
  currentPortfolioValue?: number
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

// Logo K Icon Component
const LogoKIcon = ({ className = "h-5 w-5" }: { className?: string }) => (
  <svg
    width="32"
    height="32"
    viewBox="0 0 32 32"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={className}
  >
    {/* Vertical bar */}
    <rect x="10" y="8" width="2.5" height="16" rx="1" className="fill-current" />
    {/* Upper diagonal */}
    <path
      d="M13 16 L21.5 9.5 C22 9 23 9.5 23.5 10 L24.5 11 C25 11.5 24 12.5 23.5 13 L16 17 Z"
      className="fill-current"
    />
    {/* Lower diagonal */}
    <path
      d="M13 16 L21.5 22.5 C22 23 23 22.5 23.5 22 L24.5 21 C25 20.5 24 19.5 23.5 19 L16 15 Z"
      className="fill-current"
    />
  </svg>
)

export default function AIAgentPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: '🤖 **Kairos AI** is online and ready!\n\n**Two Modes Available:**\n\n🔥 **Agent Mode** - Autonomous trading sessions\n💬 **Assistant Mode** - Interactive chat\n\nSelect your preferred mode to get started!',
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

  useEffect(() => {
    if (currentSession?.status === 'active' && currentSession.sessionId) {
      const interval = setInterval(async () => {
        try {
          setPollingCount(prev => prev + 1)
          await checkSessionStatus(currentSession.sessionId)
        } catch (error) {
          console.error('Polling error:', error)
        }
      }, 5000)
      
      setSessionPolling(interval)
      
      return () => {
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
      addMessage({
        id: Date.now().toString(),
        type: 'system',
        content: '📄 **Generating trading report...**',
        timestamp: new Date()
      })

      const response = await fetch(getApiUrl(`/api/session/report/${sessionId}`), {
        method: 'GET',
        headers: {
          'Accept': 'application/pdf',
        },
      })
      
      if (!response.ok) {
        throw new Error(`Failed to generate report: ${response.status}`)
      }

      const blob = await response.blob()
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

      addMessage({
        id: Date.now().toString(),
        type: 'system',
        content: `✅ **Report Downloaded!**\n\n📥 File: Kairos_Trading_Report_${shortSessionId}_${timestamp}.pdf`,
        timestamp: new Date()
      })

    } catch (error) {
      addMessage({
        id: Date.now().toString(),
        type: 'system',
        content: `❌ **Download Failed**\n\nError: ${error instanceof Error ? error.message : 'Unknown error'}`,
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
      addMessage({
        id: Date.now().toString(),
        type: 'system',
        content: `🚀 **Starting Trading Session...**\n\n⏰ Duration: ${durationData.text}\n🤖 Initializing AI agent...`,
        timestamp: new Date()
      })
      
      const response = await fetch(getApiUrl('/api/chat'), {
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

        addMessage({
          id: Date.now().toString(),
          type: 'system',
          content: `✅ **TRADING SESSION ACTIVE!**\n\n🆔 Session: \`${session.sessionId.substring(0, 12)}...\`\n⏰ Duration: ${durationData.text}\n💰 Starting Value: $${data.data.initial_portfolio_value?.toLocaleString() || 'Unknown'}\n\n🤖 AI Agent is now trading autonomously...`,
          timestamp: new Date(),
          sessionId: session.sessionId
        })

        setTimeout(() => checkSessionStatus(session.sessionId), 2000)
        
      } else {
        throw new Error('No session ID returned from server')
      }

    } catch (error) {
      addMessage({
        id: Date.now().toString(),
        type: 'system',
        content: `❌ **Failed to Start Session**\n\nError: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      })
    } finally {
      setIsLoading(false)
    }
  }

  const checkSessionStatus = async (sessionId: string) => {
    try {
      const response = await fetch(getApiUrl(`/api/autonomous/status/${sessionId}`), {
        method: 'GET',
        cache: 'no-cache'
      })
      
      if (!response.ok) return

      const statusData = await response.json()

      if (statusData.session_found) {
        if (currentSession && statusData.current_portfolio_value) {
          setCurrentSession(prev => prev ? {
            ...prev,
            currentPortfolioValue: statusData.current_portfolio_value,
            status: statusData.status
          } : null)
        }

        if (statusData.status === 'completed' && currentSession?.status === 'active') {
          setCurrentSession(prev => prev ? { ...prev, status: 'completed' } : null)
          
          addMessage({
            id: Date.now().toString(),
            type: 'session-end',
            content: `🏁 **TRADING SESSION COMPLETED!**\n\n📊 Final Results:\n• Session: \`${sessionId.substring(0, 12)}...\`\n• Portfolio: $${statusData.current_portfolio_value?.toLocaleString() || 'Unknown'}\n\n📄 Generating PDF report...`,
            timestamp: new Date(),
            sessionId: sessionId
          })

          setTimeout(() => {
            downloadSessionReport(sessionId)
          }, 3000)
        }

        if (statusData.status === 'active' && pollingCount % 6 === 0) {
          addMessage({
            id: Date.now().toString(),
            type: 'trading-update',
            content: `🔄 **Session Update** (${Math.floor(pollingCount * 5 / 60)} min)\n\n• Status: ACTIVE 🟢\n• Portfolio: $${statusData.current_portfolio_value?.toLocaleString() || 'Updating...'}`,
            timestamp: new Date()
          })
        }
      }
    } catch (error) {
      console.error('Status check error:', error)
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
      const response = await fetch(getApiUrl('/api/chat/assistant'), {
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
      addMessage({
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `❌ **Connection Error**\n\nTrouble connecting to backend. Ensure server is running on \`localhost:8000\`.`,
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
        const response = await fetch(getApiUrl(`/api/chat/autonomous/stop/${currentSession.sessionId}`), {
          method: 'POST'
        })
        
        if (response.ok) {
          setCurrentSession(prev => prev ? { ...prev, status: 'completed' } : null)
          
          addMessage({
            id: Date.now().toString(),
            type: 'system',
            content: '⏹️ **Session stopped manually**',
            timestamp: new Date()
          })

          setTimeout(() => {
            downloadSessionReport(currentSession.sessionId)
          }, 2000)
        }
      } catch (error) {
        addMessage({
          id: Date.now().toString(),
          type: 'system',
          content: '⚠️ **Error stopping session**',
          timestamp: new Date()
        })
      }
    }
  }

  const quickCommands = [
    { label: "💼 Portfolio", command: "Show my current portfolio" },
    { label: "₿ BTC Price", command: "Bitcoin price analysis" },
    { label: "📰 News", command: "Latest crypto news" },
    { label: "📊 Analysis", command: "Market analysis" },
  ]

  return (
    <SidebarProvider>
      <AppSidebar activePage="kairos-ai" />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem>
                  <BreadcrumbLink href="/dashboard">Kairos</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                  <BreadcrumbPage>Kairos AI</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>

          {/* Controls */}
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0 h-[calc(100vh-64px)] overflow-hidden">
          <div className="flex items-center justify-between flex-shrink-0">
            <div className="flex items-center gap-4">
              <Select value={aiMode} onValueChange={(value: AIMode) => setAiMode(value)}>
                <SelectTrigger className="w-[140px]">
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

              {aiMode === 'agent' && (
                <div className="flex gap-2">
                  <Dialog open={sessionDialogOpen} onOpenChange={setSessionDialogOpen}>
                    <DialogTrigger asChild>
                      <Button 
                        size="sm"
                        disabled={currentSession?.status === 'active'}
                      >
                        <Play className="h-4 w-4 mr-2" />
                        Start Trading
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Start Trading Session</DialogTitle>
                        <DialogDescription>
                          Select duration for autonomous trading.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
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
                        <Alert>
                          <AlertTriangle className="h-4 w-4" />
                          <AlertDescription>
                            AI will execute real trades. Monitor session carefully.
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
                                Start
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
                      Stop
                    </Button>
                  )}
                </div>
              )}
            </div>

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

          {/* Main Chat */}
          <Card className="flex-1 flex flex-col overflow-hidden">
            <CardHeader className="pb-3 flex-shrink-0">
              <CardTitle className="flex items-center gap-2">
                {aiMode === 'agent' ? (
                  <>
                    <Bot className="h-5 w-5" />
                    Trading Agent
                    <Badge variant="outline">🔥 Live</Badge>
                  </>
                ) : (
                  <>
                    <MessageSquare className="h-5 w-5" />
                    AI Assistant
                    <Badge variant="outline">💬 Chat</Badge>
                  </>
                )}
              </CardTitle>
            </CardHeader>

            <CardContent className="flex-1 flex flex-col overflow-hidden p-0">
              <div className="flex-1 overflow-hidden relative">
                <ScrollArea className="h-full w-full absolute inset-0 px-6">
                  <div className="space-y-4 py-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${
                        message.type === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      {message.type !== 'user' && (
                        <Avatar className="h-8 w-8 flex-shrink-0">
                          <AvatarFallback className={
                            message.type === 'system' ? 'bg-blue-500 text-white' : 
                            message.type === 'trading-update' ? 'bg-green-500 text-white' :
                            message.type === 'session-end' ? 'bg-purple-500 text-white' :
                            'bg-primary text-primary-foreground'
                          }>
                            {message.type === 'system' ? '⚡' : 
                             message.type === 'trading-update' ? '📈' :
                             message.type === 'session-end' ? '🏁' :
                             <LogoKIcon className="h-4 w-4" />}
                          </AvatarFallback>
                        </Avatar>
                      )}
                      
                      <div
                        className={`max-w-[80%] rounded-lg p-3 ${
                          message.type === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : message.type === 'system'
                            ? 'bg-blue-50 dark:bg-blue-950 border'
                            : message.type === 'trading-update'
                            ? 'bg-green-50 dark:bg-green-950 border'
                            : message.type === 'session-end'
                            ? 'bg-purple-50 dark:bg-purple-950 border'
                            : 'bg-muted'
                        }`}
                      >
                        <div className="text-sm leading-relaxed">
                          {message.type === 'user' ? (
                            <p className="whitespace-pre-wrap">{message.content}</p>
                          ) : (
                            formatMessage(message.content)
                          )}
                        </div>
                        
                        <div className="flex items-center justify-between mt-2 pt-2 border-t border-current/10">
                          <span className="text-xs opacity-70">
                            {message.timestamp.toLocaleTimeString()}
                          </span>
                          {message.sessionId && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-5 px-2 text-xs"
                              onClick={() => downloadSessionReport(message.sessionId!)}
                            >
                              <Download className="h-3 w-3 mr-1" />
                              PDF
                            </Button>
                          )}
                        </div>
                      </div>
                      
                      {message.type === 'user' && (
                        <Avatar className="h-8 w-8 flex-shrink-0">
                          <AvatarFallback>
                            <User className="h-4 w-4" />
                          </AvatarFallback>
                        </Avatar>
                      )}
                    </div>
                  ))}
                  
                  {isLoading && (
                    <div className="flex gap-3 justify-start">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-primary text-primary-foreground">
                          <LogoKIcon className="h-4 w-4" />
                        </AvatarFallback>
                      </Avatar>
                      <div className="bg-muted rounded-lg p-3">
                        <div className="flex items-center gap-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span className="text-sm text-muted-foreground">
                            {aiMode === 'agent' ? 'Starting session...' : 'Thinking...'}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                  </div>
                  <div ref={messagesEndRef} />
                </ScrollArea>
              </div>

              {/* Input for Assistant mode */}
              {aiMode === 'assistant' && (
                <div className="p-4 border-t">
                  <div className="flex flex-wrap gap-2 mb-4 justify-center">
                    {quickCommands.map((cmd, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        onClick={() => setInput(cmd.command)}
                        disabled={isLoading}
                      >
                        {cmd.label}
                      </Button>
                    ))}
                  </div>

                  <div className="relative">
                    <Textarea
                      ref={inputRef}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask about crypto prices, news, analysis..."
                      disabled={isLoading}
                      className="min-h-[80px] pr-12 resize-none"
                      rows={3}
                    />
                    <Button 
                      onClick={sendAssistantMessage} 
                      disabled={!input.trim() || isLoading}
                      size="icon"
                      className="absolute bottom-2 right-2 h-8 w-8"
                    >
                      {isLoading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Send className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground text-center mt-2">
                    Press Enter to send • Shift+Enter for new line
                  </p>
                </div>
              )}

              {/* Agent mode info */}
              {aiMode === 'agent' && !currentSession && (
                <div className="p-4 border-t">
                  <div className="text-center space-y-4 p-4 rounded-lg bg-muted/50">
                    <h3 className="font-medium">🤖 Autonomous Trading Agent</h3>
                    <p className="text-sm text-muted-foreground">
                      Start a session to let AI make autonomous trading decisions and generate PDF reports.
                    </p>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="p-2 bg-background rounded">
                        <div className="font-medium mb-1">✅ Features:</div>
                        <ul className="text-muted-foreground space-y-0.5">
                          <li>• Market analysis</li>
                          <li>• Auto execution</li>
                          <li>• PDF reports</li>
                        </ul>
                      </div>
                      <div className="p-2 bg-background rounded">
                        <div className="font-medium mb-1">⚠️ Notice:</div>
                        <ul className="text-muted-foreground space-y-0.5">
                          <li>• Real trading</li>
                          <li>• Monitor session</li>
                          <li>• Ensure balance</li>
                        </ul>
                      </div>
                    </div>
                    <Button 
                      variant="outline"
                      onClick={() => setSessionDialogOpen(true)}
                    >
                      <Play className="h-4 w-4 mr-2" />
                      Start Session
                    </Button>
                  </div>
                </div>
              )}

              {/* Active session dashboard */}
              {aiMode === 'agent' && currentSession?.status === 'active' && (
                <div className="p-4 border-t">
                  <div className="p-4 rounded-lg border bg-card">
                    <div className="flex items-center gap-2 mb-3">
                      <Activity className="h-4 w-4 text-green-500" />
                      <span className="font-medium text-sm">Live Session</span>
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <div className="font-medium">Session</div>
                        <div className="font-mono text-muted-foreground">
                          {currentSession.sessionId.substring(0, 12)}...
                        </div>
                      </div>
                      <div>
                        <div className="font-medium">Duration</div>
                        <div className="text-muted-foreground">{currentSession.duration}</div>
                      </div>
                      <div>
                        <div className="font-medium">Portfolio</div>
                        <div className="font-semibold text-green-600">
                          ${currentSession.currentPortfolioValue?.toLocaleString() || 'Updating...'}
                        </div>
                      </div>
                      <div>
                        <div className="font-medium">Checks</div>
                        <div className="text-muted-foreground">#{pollingCount}</div>
                      </div>
                    </div>
                    
                    <div className="flex gap-2 mt-3">
                      <Button 
                        variant="destructive" 
                        size="sm" 
                        onClick={stopSession}
                        className="flex-1"
                      >
                        <Pause className="h-4 w-4 mr-1" />
                        Stop
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => checkSessionStatus(currentSession.sessionId)}
                      >
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}