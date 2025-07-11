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
import { Bot, User, Send, TrendingUp, Wallet, DollarSign, Activity, Loader2 } from "lucide-react"

interface Message {
  id: string
  type: 'user' | 'ai' | 'system'
  content: string
  timestamp: Date
  intent?: string
  confidence?: number
  isStreaming?: boolean
}

interface ChatStats {
  totalTrades: number
  portfolioValue: string
  lastUpdate: string
}

export default function AIAgentPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: '🚀 **Gemini AI Trading Agent** is online and ready!\n\n✅ **Full Capabilities Active:**\n• Real trading execution via Recall API\n• Live portfolio & balance management\n• Real-time price monitoring\n• Latest cryptocurrency news & sentiment\n• Complete trading history access\n• Advanced AI analysis & insights\n\n💰 **Supported Tokens:** USDC, WETH, WBTC, DAI, USDT, UNI, LINK, ETH\n\n🎯 **Try commands like:**\n• "Trade 500 USDC to WETH"\n• "Show my portfolio"\n• "What\'s the price of Bitcoin?"\n• "Show me trending crypto news"',
      timestamp: new Date(),
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [chatStats, setChatStats] = useState<ChatStats>({
    totalTrades: 0,
    portfolioValue: '$0.00',
    lastUpdate: 'Never'
  })
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const formatMessage = (content: string) => {
    // Convert markdown-like formatting to JSX
    const lines = content.split('\n')
    return lines.map((line, index) => {
      // Handle headers
      if (line.startsWith('## ')) {
        return <h2 key={index} className="text-lg font-bold mt-4 mb-2 text-primary">{line.slice(3)}</h2>
      }
      if (line.startsWith('# ')) {
        return <h1 key={index} className="text-xl font-bold mt-4 mb-2 text-primary">{line.slice(2)}</h1>
      }
      
      // Handle bold text with **
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
      
      // Handle bullet points
      if (line.startsWith('• ') || line.startsWith('- ')) {
        return <li key={index} className="ml-4 mb-1 list-disc">{line.slice(2)}</li>
      }
      
      // Handle numbered lists
      if (/^\d+\.\s/.test(line)) {
        return <li key={index} className="ml-4 mb-1 list-decimal">{line.replace(/^\d+\.\s/, '')}</li>
      }
      
      // Handle section separators
      if (line.includes('===') || line.includes('---')) {
        return <hr key={index} className="my-4 border-border" />
      }
      
      // Handle emojis and special formatting
      if (line.includes('🎯') || line.includes('📊') || line.includes('💰') || line.includes('🔥')) {
        return <p key={index} className="mb-2 text-sm font-medium text-primary">{line}</p>
      }
      
      // Regular lines
      if (line.trim()) {
        return <p key={index} className="mb-2 text-muted-foreground">{line}</p>
      }
      
      // Empty lines
      return <br key={index} />
    })
  }

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Call the backend AI agent
      const response = await fetch('http://localhost:8000/api/chat', {
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
        throw new Error('Failed to get response from AI agent')
      }

      const data = await response.json()

      // Add AI response
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: data.response,
        timestamp: new Date(),
        intent: data.intent,
        confidence: data.confidence,
      }

      setMessages(prev => [...prev, aiMessage])

      // Update stats if provided
      if (data.stats) {
        setChatStats(data.stats)
      }

    } catch (error) {
      console.error('Error sending message:', error)
      
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: '❌ **Connection Error**\n\nI\'m having trouble connecting to the backend. Please make sure the AI agent server is running on `localhost:8000`.\n\n💡 **To start the server:**\n```bash\ncd backend\npython main.py\n```\n\nThen try your message again!',
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const quickCommands = [
    { label: "Show Portfolio", command: "Show my portfolio" },
    { label: "WETH Price", command: "What's the price of WETH?" },
    { label: "Trending News", command: "Show me trending crypto news" },
    { label: "Trade History", command: "Show my trading history" },
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
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>AI Agent</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>

        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          {/* Main Chat Interface */}
          <Card className="flex-1 flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-primary" />
                Gemini AI Trading Agent
                <Badge variant="outline" className="ml-auto">
                  🔥 Real Trading Enabled
                </Badge>
              </CardTitle>
            </CardHeader>
            
            <CardContent className="flex-1 flex flex-col p-0">
              {/* Messages Area */}
              <ScrollArea className="flex-1 p-4">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${
                        message.type === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      {message.type !== 'user' && (
                        <Avatar className="h-8 w-8">
                          <AvatarFallback className={
                            message.type === 'system' ? 'bg-blue-500 text-white' : 'bg-primary text-primary-foreground'
                          }>
                            {message.type === 'system' ? '⚡' : <Bot className="h-4 w-4" />}
                          </AvatarFallback>
                        </Avatar>
                      )}
                      
                      <div
                        className={`max-w-[80%] rounded-lg p-3 ${
                          message.type === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : message.type === 'system'
                            ? 'bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800'
                            : 'bg-muted'
                        }`}
                      >
                        {message.type === 'user' ? (
                          <p className="text-sm">{message.content}</p>
                        ) : (
                          <div className="text-sm">
                            {formatMessage(message.content)}
                          </div>
                        )}
                        
                        <div className="flex items-center justify-between mt-2 pt-2 border-t border-current/10">
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
                        <Avatar className="h-8 w-8">
                          <AvatarFallback className="bg-secondary">
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
                          <Bot className="h-4 w-4" />
                        </AvatarFallback>
                      </Avatar>
                      <div className="bg-muted rounded-lg p-3">
                        <div className="flex items-center gap-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span className="text-sm text-muted-foreground">
                            AI is analyzing and processing...
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <div ref={messagesEndRef} />
              </ScrollArea>

              {/* Quick Commands */}
              <div className="p-4 border-t">
                <div className="flex flex-wrap gap-2 mb-3">
                  {quickCommands.map((cmd, index) => (
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

                {/* Input Area */}
                <div className="flex gap-2">
                  <Input
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your trading command... (e.g., 'Trade 500 USDC to WETH')"
                    disabled={isLoading}
                    className="flex-1"
                  />
                  <Button 
                    onClick={sendMessage} 
                    disabled={!input.trim() || isLoading}
                    size="icon"
                  >
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}