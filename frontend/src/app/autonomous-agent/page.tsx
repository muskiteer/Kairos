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
  Square,
  Clock,
  Target,
  Brain,
  BarChart3,
  Newspaper,
  AlertTriangle,
  CheckCircle,
  XCircle
} from "lucide-react"

interface AutonomousSession {
  session_id: string
  status: 'active' | 'completed' | 'stopped'
  duration_text: string
  start_time: string
  end_time: string
  performance: {
    total_trades: number
    successful_trades: number
    total_profit_loss: number
    start_portfolio_value: number
    current_portfolio_value: number
    roi_percentage: number
  }
  last_cycle?: string
  current_strategy?: string
  current_reasoning?: string[]
}

interface RealtimeUpdate {
  id: string
  timestamp: string
  type: 'decision' | 'trade' | 'analysis' | 'news' | 'error'
  title: string
  content: string
  strategy?: string
  confidence?: number
  status?: 'success' | 'pending' | 'failed'
}

interface Activity {
  id?: string;  // Add optional id field
  timestamp: string;
  type: 'decision' | 'trade' | 'analysis' | 'error';
  reasoning: string;
  strategy: string;
  result?: string;
}

export default function AutonomousAgentPage() {
  const [session, setSession] = useState<AutonomousSession | null>(null)
  const [realtimeUpdates, setRealtimeUpdates] = useState<RealtimeUpdate[]>([])
  const [duration, setDuration] = useState("")
  const [isStarting, setIsStarting] = useState(false)
  const [isStopping, setIsStopping] = useState(false)
  
  const updatesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    updatesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [realtimeUpdates])

  // Simulate real-time updates polling
  useEffect(() => {
    if (!session || session.status !== 'active') return

    const interval = setInterval(async () => {
      try {
        // Get session status
        const statusResponse = await fetch(`http://localhost:8000/api/autonomous/status/${session.session_id}`)
        if (statusResponse.ok) {
          const statusData = await statusResponse.json()
          if (statusData.session_found) {
            setSession(statusData.session_data)
            
            // Add new reasoning updates
            if (statusData.session_data.reasoning_log) {
              const latestLog = statusData.session_data.reasoning_log.slice(-1)[0]
              if (latestLog && latestLog.timestamp !== realtimeUpdates[0]?.timestamp) {
                const update: RealtimeUpdate = {
                  id: Date.now().toString(),
                  timestamp: latestLog.timestamp,
                  type: latestLog.decision?.strategy_used ? 'decision' : 'analysis',
                  title: latestLog.decision?.strategy_used 
                    ? `🎯 Strategy: ${latestLog.decision.strategy_used.replace('_', ' ').toUpperCase()}`
                    : '🔍 Market Analysis',
                  content: latestLog.decision?.reasoning?.join('\n') || 'Analyzing market conditions...',
                  strategy: latestLog.decision?.strategy_used,
                  confidence: latestLog.decision?.confidence,
                  status: latestLog.execution_result?.success ? 'success' : 
                          latestLog.execution_result ? 'failed' : 'pending'
                }
                setRealtimeUpdates(prev => [update, ...prev.slice(0, 19)]) // Keep last 20
              }
            }
          }
        }
      } catch (error) {
        console.error('Error polling session status:', error)
      }
    }, 5000) // Poll every 5 seconds

    return () => clearInterval(interval)
  }, [session, realtimeUpdates])

  const startAutonomousTrading = async () => {
    if (!duration.trim()) {
      alert('Please specify duration (e.g., "2hr", "30min", "1day")')
      return
    }

    setIsStarting(true)
    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: `start trading session for ${duration} for testing and strategy optimization`,
          timestamp: new Date().toISOString(),
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to start autonomous trading')
      }

      const data = await response.json()
      
      if (data.intent === 'autonomous_activated') {
        setSession({
          session_id: data.data.session_id,
          status: 'active',
          duration_text: data.data.autonomous_params.duration_text,
          start_time: data.data.autonomous_params.start_time,
          end_time: data.data.autonomous_params.end_time,
          performance: {
            total_trades: 0,
            successful_trades: 0,
            total_profit_loss: 0,
            start_portfolio_value: 0,
            current_portfolio_value: 0,
            roi_percentage: 0
          }
        })
        
        // Add initial update
        const initialUpdate: RealtimeUpdate = {
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          type: 'decision',
          title: '🚀 AUTONOMOUS TRADING ACTIVATED',
          content: `Session started for ${data.data.autonomous_params.duration_text}\nAI agent is now analyzing market conditions and building trading strategies.`,
          status: 'success'
        }
        setRealtimeUpdates([initialUpdate])
      }

    } catch (error) {
      console.error('Error starting autonomous trading:', error)
      alert('Failed to start autonomous trading. Make sure the backend is running.')
    } finally {
      setIsStarting(false)
    }
  }

  const stopAutonomousTrading = async () => {
    if (!session) return

    setIsStopping(true)
    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: 'stop autonomous',
          timestamp: new Date().toISOString(),
        }),
      })

      if (response.ok) {
        setSession(prev => prev ? { ...prev, status: 'stopped' } : null)
        
        const stopUpdate: RealtimeUpdate = {
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          type: 'decision',
          title: '🛑 AUTONOMOUS TRADING STOPPED',
          content: 'Session manually stopped by user.\nGenerating final performance report...',
          status: 'success'
        }
        setRealtimeUpdates(prev => [stopUpdate, ...prev])
      }

    } catch (error) {
      console.error('Error stopping autonomous trading:', error)
    } finally {
      setIsStopping(false)
    }
  }

  const getUpdateIcon = (type: string, status?: string) => {
    switch (type) {
      case 'decision':
        return status === 'success' ? <CheckCircle className="h-4 w-4 text-green-500" /> :
               status === 'failed' ? <XCircle className="h-4 w-4 text-red-500" /> :
               <Brain className="h-4 w-4 text-blue-500" />
      case 'trade':
        return <TrendingUp className="h-4 w-4 text-purple-500" />
      case 'analysis':
        return <BarChart3 className="h-4 w-4 text-orange-500" />
      case 'news':
        return <Newspaper className="h-4 w-4 text-yellow-500" />
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      default:
        return <Activity className="h-4 w-4 text-gray-500" />
    }
  }

  const formatContent = (content: string) => {
    return content.split('\n').map((line, index) => (
      <p key={index} className="text-sm text-muted-foreground mb-1">
        {line}
      </p>
    ))
  }

  const quickDurations = ["30min", "1hr", "2hr", "6hr", "12hr", "24hr", "2days"]

  return (
    <SidebarProvider>
      <AppSidebar activePage="autonomous-agent" />
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
                  <BreadcrumbPage>Autonomous Agent</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>

        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          {/* Session Control Panel */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-primary" />
                Kairos Autonomous Trading Agent
                {session?.status === 'active' && (
                  <Badge className="bg-green-500 text-white animate-pulse">
                    🔴 LIVE TRADING
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!session || session.status !== 'active' ? (
                <div className="space-y-4">
                  <div className="flex gap-2 items-center">
                    <Input
                      value={duration}
                      onChange={(e) => setDuration(e.target.value)}
                      placeholder="Duration (e.g., 2hr, 30min, 1day)"
                      className="flex-1"
                    />
                    <Button 
                      onClick={startAutonomousTrading}
                      disabled={isStarting}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      {isStarting ? (
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      ) : (
                        <Play className="h-4 w-4 mr-2" />
                      )}
                      Start Autonomous Trading
                    </Button>
                  </div>
                  
                  <div className="flex gap-2 flex-wrap">
                    <span className="text-sm text-muted-foreground mr-2">Quick select:</span>
                    {quickDurations.map((dur) => (
                      <Button
                        key={dur}
                        variant="outline"
                        size="sm"
                        onClick={() => setDuration(dur)}
                        className="text-xs"
                      >
                        {dur}
                      </Button>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div>
                        <p className="font-medium">Session: {session.session_id.slice(0, 8)}</p>
                        <p className="text-sm text-muted-foreground">Duration: {session.duration_text}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold text-green-600">
                          {session.performance.roi_percentage.toFixed(2)}%
                        </p>
                        <p className="text-xs text-muted-foreground">ROI</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xl font-semibold">
                          {session.performance.total_trades}
                        </p>
                        <p className="text-xs text-muted-foreground">Total Trades</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xl font-semibold text-blue-600">
                          {session.performance.successful_trades}/{session.performance.total_trades}
                        </p>
                        <p className="text-xs text-muted-foreground">Success Rate</p>
                      </div>
                    </div>
                    
                    <Button 
                      onClick={stopAutonomousTrading}
                      disabled={isStopping}
                      variant="destructive"
                    >
                      {isStopping ? (
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      ) : (
                        <Square className="h-4 w-4 mr-2" />
                      )}
                      Stop Trading
                    </Button>
                  </div>

                  {/* Progress Bar */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Session Progress</span>
                      <span>{new Date(session.start_time).toLocaleString()} - {new Date(session.end_time).toLocaleString()}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${Math.min(100, Math.max(0, 
                            ((new Date().getTime() - new Date(session.start_time).getTime()) / 
                             (new Date(session.end_time).getTime() - new Date(session.start_time).getTime())) * 100
                          ))}%`
                        }}
                      />
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Real-time Activity Feed */}
          {session && (
            <Card className="flex-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Real-time AI Decision Stream
                  <Badge variant="outline" className="ml-auto animate-pulse">
                    {realtimeUpdates.length} updates
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <ScrollArea className="h-[500px] p-4">
                  <div className="space-y-3">
                    {realtimeUpdates.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Waiting for AI agent activity...</p>
                        <p className="text-sm">The agent will start analyzing market conditions shortly.</p>
                      </div>
                    ) : (
                      realtimeUpdates.map((update) => (
                        <div key={update.id} className="border rounded-lg p-3 space-y-2">
                          <div className="flex items-start gap-3">
                            {getUpdateIcon(update.type, update.status)}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between">
                                <h4 className="font-medium text-sm">{update.title}</h4>
                                <span className="text-xs text-muted-foreground">
                                  {new Date(update.timestamp).toLocaleTimeString()}
                                </span>
                              </div>
                              <div className="mt-2">
                                {formatContent(update.content)}
                              </div>
                              {update.strategy && (
                                <div className="flex items-center gap-2 mt-2">
                                  <Badge variant="secondary" className="text-xs">
                                    {update.strategy.replace('_', ' ').toUpperCase()}
                                  </Badge>
                                  {update.confidence && (
                                    <Badge variant="outline" className="text-xs">
                                      {Math.round(update.confidence * 100)}% confidence
                                    </Badge>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                  <div ref={updatesEndRef} />
                </ScrollArea>
              </CardContent>
            </Card>
          )}

          {/* Feature Explanation */}
          {!session && (
            <Card>
              <CardHeader>
                <CardTitle>🤖 Autonomous Trading Features</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <h4 className="font-semibold mb-2">🧠 AI Decision Making</h4>
                    <ul className="space-y-1 text-muted-foreground">
                      <li>• 7+ Advanced trading strategies</li>
                      <li>• Real-time news sentiment analysis</li>
                      <li>• Dynamic portfolio rebalancing</li>
                      <li>• Risk management & position sizing</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">📊 Real-time Monitoring</h4>
                    <ul className="space-y-1 text-muted-foreground">
                      <li>• Live decision reasoning</li>
                      <li>• Strategy performance tracking</li>
                      <li>• Market analysis updates</li>
                      <li>• Trade execution notifications</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">📈 Smart Trading</h4>
                    <ul className="space-y-1 text-muted-foreground">
                      <li>• Momentum & mean reversion</li>
                      <li>• News-driven sentiment trading</li>
                      <li>• Multi-asset correlation analysis</li>
                      <li>• Counter-trend opportunities</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">🔒 Risk Management</h4>
                    <ul className="space-y-1 text-muted-foreground">
                      <li>• Advanced risk scoring</li>
                      <li>• Position size optimization</li>
                      <li>• Portfolio diversification</li>
                      <li>• Stop-loss & take-profit logic</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
