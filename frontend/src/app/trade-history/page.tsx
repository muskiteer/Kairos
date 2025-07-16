"use client"

import { useState, useEffect } from "react"
import { AppSidebar } from "@/components/app-sidebar"
import {
  Breadcrumb,
  BreadcrumbItem,
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
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  History, 
  RefreshCw, 
  TrendingUp, 
  TrendingDown,
  Calendar,
  Clock,
  DollarSign,
  ArrowRightLeft,
  ExternalLink,
  Filter,
  Download,
  Loader2,
  CheckCircle,
  XCircle
} from "lucide-react"

interface Trade {
  id: string
  timestamp: string
  fromToken: string
  toToken: string
  fromAmount: number
  toAmount: number
  fromPrice: number
  toPrice: number
  totalValue: number
  chain: string
  txHash: string
  status: 'success' | 'failed' | 'pending'
  gasUsed?: number
  gasFee?: number
  slippage?: number
  type: 'buy' | 'sell' | 'swap'
  session_id?: string  // For AI trades
  strategy?: string    // For AI trades
  source?: 'manual' | 'ai_agent'  // Trade source
}

interface TradeStats {
  totalTrades: number
  totalVolume: number
  successRate: number
  totalFees: number
  avgTradeSize: number
  mostTradedToken: string
}

export default function TradeHistoryPage() {
  const [trades, setTrades] = useState<Trade[]>([])
  const [tradeStats, setTradeStats] = useState<TradeStats>({
    totalTrades: 0,
    totalVolume: 0,
    successRate: 0,
    totalFees: 0,
    avgTradeSize: 0,
    mostTradedToken: ""
  })
  const [isLoading, setIsLoading] = useState(false)
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'success' | 'failed' | 'pending'>('all')
  const [selectedSource, setSelectedSource] = useState<'all' | 'manual' | 'ai_agent'>('all')
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const [loadingMessage, setLoadingMessage] = useState("")

  // Cache system to prevent multiple API calls
  const [cachedData, setCachedData] = useState<{trades: Trade[], stats: TradeStats, timestamp: number} | null>(null)
  const CACHE_DURATION = 30000 // 30 seconds

  // Fetch trade history from API - OPTIMIZED
  const fetchTradeHistory = async (useCache = true) => {
    // Check cache first
    if (useCache && cachedData && (Date.now() - cachedData.timestamp) < CACHE_DURATION) {
      console.log("📦 Using cached trade data")
      setTrades(cachedData.trades)
      setTradeStats(cachedData.stats)
      setLastUpdate(new Date(cachedData.timestamp))
      return
    }

    setIsLoading(true)
    setLoadingMessage("Loading trade history...")
    
    try {
      const startTime = Date.now()
      console.log("🚀 Fetching fresh trade history...")
      
      // Use a timeout to prevent hanging
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000) // 10 second timeout
      
      setLoadingMessage("Fetching manual trades...")
      
      // Fetch both manual trades and AI agent trades in parallel
      const [manualResponse, aiResponse] = await Promise.allSettled([
        fetch('http://localhost:8000/api/trades/history', {
          signal: controller.signal,
          headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' }
        }),
        fetch('http://localhost:8000/api/ai-agent/trades', {
          signal: controller.signal,
          headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' }
        })
      ])
      
      clearTimeout(timeoutId)
      
      let allTrades: Trade[] = []
      let combinedStats = {
        totalTrades: 0,
        totalVolume: 0,
        successRate: 0,
        totalFees: 0,
        avgTradeSize: 0,
        mostTradedToken: ""
      }
      
      // Process manual trades
      if (manualResponse.status === 'fulfilled' && manualResponse.value.ok) {
        const manualData = await manualResponse.value.json()
        if (manualData.trades && Array.isArray(manualData.trades)) {
          const manualTrades = manualData.trades.map((trade: any, index: number) => ({
            ...trade,
            id: trade.id || `manual_${index}`,
            source: 'manual' as const
          }))
          allTrades.push(...manualTrades)
          console.log(`📊 Loaded ${manualTrades.length} manual trades`)
        }
      }
      
      setLoadingMessage("Fetching AI agent trades...")
      
      // Process AI agent trades
      if (aiResponse.status === 'fulfilled' && aiResponse.value.ok) {
        const aiData = await aiResponse.value.json()
        if (aiData.trades && Array.isArray(aiData.trades)) {
          const aiTrades = aiData.trades.map((trade: any, index: number) => ({
            ...trade,
            id: trade.id || `ai_${index}`,
            source: 'ai_agent' as const
          }))
          allTrades.push(...aiTrades)
          console.log(`🤖 Loaded ${aiTrades.length} AI agent trades`)
        }
      }
      
      // Sort all trades by timestamp (newest first)
      allTrades.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      
      // Calculate combined statistics
      const totalTrades = allTrades.length
      const successfulTrades = allTrades.filter(t => t.status === 'success').length
      const totalVolume = allTrades.reduce((sum, t) => sum + (t.totalValue || 0), 0)
      const totalFees = allTrades.reduce((sum, t) => sum + (t.gasFee || 0), 0)
      
      // Calculate REAL most traded token from actual trades
      const tokenFrequency: Record<string, number> = {}
      allTrades.forEach(trade => {
        [trade.fromToken, trade.toToken].forEach(token => {
          if (token && token !== "UNKNOWN") {
            tokenFrequency[token] = (tokenFrequency[token] || 0) + 1
          }
        })
      })
      
      const mostTradedToken = Object.keys(tokenFrequency).length > 0 
        ? Object.entries(tokenFrequency).reduce((a, b) => a[1] > b[1] ? a : b)[0]
        : "N/A"
      
      combinedStats = {
        totalTrades,
        totalVolume,
        successRate: totalTrades > 0 ? (successfulTrades / totalTrades) * 100 : 0,
        totalFees,
        avgTradeSize: totalTrades > 0 ? totalVolume / totalTrades : 0,
        mostTradedToken // REAL most traded token from actual data
      }
      
      const loadTime = Date.now() - startTime
      
      // Update state and cache
      setTrades(allTrades)
      setTradeStats(combinedStats)
      
      // Cache the data
      setCachedData({
        trades: allTrades,
        stats: combinedStats,
        timestamp: Date.now()
      })
      
      setLoadingMessage(`Loaded ${totalTrades} trades (${successfulTrades} successful) in ${loadTime}ms`)
      console.log(`📊 Total trades loaded: ${totalTrades} in ${loadTime}ms`)
      
    } catch (error: any) {
      console.error('❌ Trade history fetch error:', error)
      
      if (error.name === 'AbortError') {
        setLoadingMessage("Request timed out - please try again")
      } else {
        setLoadingMessage("Network error occurred")
      }
      
      setTrades([])
      setTradeStats({
        totalTrades: 0,
        totalVolume: 0,
        successRate: 0,
        totalFees: 0,
        avgTradeSize: 0,
        mostTradedToken: ""
      })
    }
    
    setIsLoading(false)
    setLastUpdate(new Date())
  }

  const exportTradesToCSV = () => {
    try {
      // Create CSV headers
      const headers = [
        'ID', 'Timestamp', 'Type', 'From Token', 'To Token', 
        'From Amount', 'To Amount', 'From Price', 'To Price', 
        'Total Value', 'Chain', 'Gas Fee', 'Status', 'Transaction Hash'
      ]
      
      // Create CSV rows
      const csvData = [
        headers.join(','),
        ...filteredTrades.map(trade => [
          `"${trade.id}"`,
          `"${formatDate(trade.timestamp)}"`,
          `"${trade.type}"`,
          `"${trade.fromToken}"`,
          `"${trade.toToken}"`,
          trade.fromAmount.toString(),
          trade.toAmount.toString(),
          trade.fromPrice.toString(),
          trade.toPrice.toString(),
          trade.totalValue.toString(),
          `"${trade.chain}"`,
          trade.gasFee?.toString() || '0',
          `"${trade.status}"`,
          `"${trade.txHash}"`
        ].join(','))
      ].join('\n')

      // Create and download file
      const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      if (link.download !== undefined) {
        const url = URL.createObjectURL(blob)
        link.setAttribute('href', url)
        link.setAttribute('download', `kairos_trade_history_${new Date().toISOString().split('T')[0]}.csv`)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    } catch (error) {
      console.error('❌ Export failed:', error)
      alert('Failed to export trade history. Please try again.')
    }
  }

  // Load data on component mount
  useEffect(() => {
    fetchTradeHistory()
  }, [])

  // Filter trades based on status and source
  const filteredTrades = trades.filter(trade => {
    const statusMatch = selectedFilter === 'all' || trade.status === selectedFilter
    const sourceMatch = selectedSource === 'all' || trade.source === selectedSource
    return statusMatch && sourceMatch
  })

  const formatCurrency = (amount: number) => {
    return `$${amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  const formatToken = (amount: number, decimals = 6) => {
    return amount.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
  }

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />
      case 'pending':
        return <Loader2 className="h-4 w-4 text-yellow-600 animate-spin" />
      default:
        return null
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Success</Badge>
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">Pending</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'buy':
        return <TrendingUp className="h-4 w-4 text-green-600" />
      case 'sell':
        return <TrendingDown className="h-4 w-4 text-red-600" />
      case 'swap':
        return <ArrowRightLeft className="h-4 w-4 text-blue-600" />
      default:
        return <ArrowRightLeft className="h-4 w-4" />
    }
  }

  const getExplorerUrl = (txHash: string, chain: string) => {
    const explorers: Record<string, string> = {
      'ethereum': 'https://etherscan.io/tx/',
      'polygon': 'https://polygonscan.com/tx/',
      'bsc': 'https://bscscan.com/tx/',
      'arbitrum': 'https://arbiscan.io/tx/',
      'optimism': 'https://optimistic.etherscan.io/tx/',
      'base': 'https://basescan.org/tx/',
      'avalanche': 'https://snowtrace.io/tx/'
    }
    
    const normalizedChain = chain.toLowerCase()
    const baseUrl = explorers[normalizedChain] || explorers['ethereum']
    return `${baseUrl}${txHash}`
  }

  return (
    <SidebarProvider>
      <AppSidebar activePage="trade-history" />
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
                  <BreadcrumbPage>Trade History</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
          <div className="ml-auto px-4 flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={exportTradesToCSV}
              disabled={isLoading || filteredTrades.length === 0}
            >
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchTradeHistory(false)} // Force refresh without cache
              disabled={isLoading}
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              {isLoading ? "Loading..." : "Refresh"}
            </Button>
          </div>
        </header>

        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          {/* Trade Statistics Cards */}
          <div className="grid auto-rows-min gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Trades</CardTitle>
                <History className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{tradeStats.totalTrades}</div>
                <p className="text-xs text-muted-foreground">
                  {filteredTrades.length} showing
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Volume</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(tradeStats.totalVolume)}</div>
                <p className="text-xs text-muted-foreground">
                  Avg: {formatCurrency(tradeStats.avgTradeSize)}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{tradeStats.successRate.toFixed(1)}%</div>
                <p className="text-xs text-muted-foreground">
                  Total fees: {formatCurrency(tradeStats.totalFees)}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Most Traded</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{tradeStats.mostTradedToken || "N/A"}</div>
                <p className="text-xs text-muted-foreground">
                  Last update: {lastUpdate.toLocaleTimeString()}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Filters and Trade Table */}
          <Card className="flex-1">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <History className="h-5 w-5" />
                  Trade History
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4 text-muted-foreground" />
                  <div className="flex gap-1">
                    {(['all', 'success', 'failed', 'pending'] as const).map((filter) => (
                      <Button
                        key={filter}
                        variant={selectedFilter === filter ? "default" : "outline"}
                        size="sm"
                        onClick={() => setSelectedFilter(filter)}
                      >
                        {filter.charAt(0).toUpperCase() + filter.slice(1)}
                      </Button>
                    ))}
                  </div>
                  <div className="h-4 w-px bg-border mx-2" />
                  <div className="flex gap-1">
                    {(['all', 'manual', 'ai_agent'] as const).map((source) => (
                      <Button
                        key={source}
                        variant={selectedSource === source ? "default" : "outline"}
                        size="sm"
                        onClick={() => setSelectedSource(source)}
                      >
                        {source === 'ai_agent' ? '🤖 AI Agent' : 
                         source === 'manual' ? '👤 Manual' : 
                         '📊 All'}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <ScrollArea className="h-[600px]">
                <div className="w-full">
                  <table className="w-full">
                    <thead className="border-b bg-muted/50">
                      <tr className="text-left">
                        <th className="p-3 text-sm font-medium">Status</th>
                        <th className="p-3 text-sm font-medium">Source</th>
                        <th className="p-3 text-sm font-medium">Time</th>
                        <th className="p-3 text-sm font-medium">Type</th>
                        <th className="p-3 text-sm font-medium">From</th>
                        <th className="p-3 text-sm font-medium">To</th>
                        <th className="p-3 text-sm font-medium">Amount</th>
                        <th className="p-3 text-sm font-medium">Price</th>
                        <th className="p-3 text-sm font-medium">Total Value</th>
                        <th className="p-3 text-sm font-medium">Chain</th>
                        <th className="p-3 text-sm font-medium">Gas Fee</th>
                        <th className="p-3 text-sm font-medium">Transaction</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredTrades.map((trade) => (
                        <tr key={trade.id} className="border-b hover:bg-muted/50 transition-colors">
                          <td className="p-3">
                            <div className="flex items-center gap-2">
                              {getStatusIcon(trade.status)}
                              {getStatusBadge(trade.status)}
                            </div>
                          </td>
                          <td className="p-3">
                            <div className="flex items-center gap-2">
                              {trade.source === 'ai_agent' ? (
                                <Badge className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                                  🤖 AI Agent
                                </Badge>
                              ) : (
                                <Badge variant="outline">
                                  👤 Manual
                                </Badge>
                              )}
                              {trade.strategy && (
                                <span className="text-xs text-muted-foreground">
                                  {trade.strategy}
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="p-3">
                            <div className="flex items-center gap-2 text-sm">
                              <Clock className="h-3 w-3 text-muted-foreground" />
                              <div>
                                <div>{new Date(trade.timestamp).toLocaleDateString()}</div>
                                <div className="text-xs text-muted-foreground">
                                  {new Date(trade.timestamp).toLocaleTimeString()}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="p-3">
                            <div className="flex items-center gap-2">
                              {getTypeIcon(trade.type)}
                              <Badge variant="outline" className="capitalize">
                                {trade.type}
                              </Badge>
                            </div>
                          </td>
                          <td className="p-3">
                            <div className="font-medium">{trade.fromToken}</div>
                            <div className="text-sm text-muted-foreground">
                              {formatToken(trade.fromAmount)}
                            </div>
                          </td>
                          <td className="p-3">
                            <div className="font-medium">{trade.toToken}</div>
                            <div className="text-sm text-muted-foreground">
                              {formatToken(trade.toAmount)}
                            </div>
                          </td>
                          <td className="p-3">
                            <div className="text-sm">
                              <div>{formatToken(trade.fromAmount)} {trade.fromToken}</div>
                              <div className="text-muted-foreground">→ {formatToken(trade.toAmount)} {trade.toToken}</div>
                            </div>
                          </td>
                          <td className="p-3">
                            <div className="text-sm">
                              <div>${trade.fromPrice.toFixed(4)}</div>
                              <div className="text-muted-foreground">→ ${trade.toPrice.toFixed(4)}</div>
                            </div>
                          </td>
                          <td className="p-3">
                            <div className="font-medium">{formatCurrency(trade.totalValue)}</div>
                            {trade.slippage && (
                              <div className="text-xs text-muted-foreground">
                                Slippage: {trade.slippage}%
                              </div>
                            )}
                          </td>
                          <td className="p-3">
                            <Badge variant="secondary">{trade.chain}</Badge>
                          </td>
                          <td className="p-3">
                            <div className="text-sm">
                              <div>{formatCurrency(trade.gasFee || 0)}</div>
                              {trade.gasUsed && (
                                <div className="text-xs text-muted-foreground">
                                  {trade.gasUsed.toLocaleString()} gas
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="p-3">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0"
                              onClick={() => window.open(getExplorerUrl(trade.txHash, trade.chain), '_blank')}
                            >
                              <ExternalLink className="h-3 w-3" />
                            </Button>
                            <div className="text-xs text-muted-foreground font-mono mt-1">
                              {trade.txHash.slice(0, 10)}...{trade.txHash.slice(-8)}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  
                  {isLoading && (
                    <div className="text-center py-12">
                      <Loader2 className="h-8 w-8 mx-auto text-muted-foreground mb-4 animate-spin" />
                      <p className="text-lg font-medium">Loading trade history...</p>
                      <p className="text-sm text-muted-foreground">{loadingMessage}</p>
                    </div>
                  )}
                  
                  {filteredTrades.length === 0 && !isLoading && (
                    <div className="text-center py-12">
                      <History className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                      <p className="text-lg font-medium">No trades found</p>
                      <p className="text-muted-foreground">
                        {selectedFilter !== 'all' 
                          ? `No ${selectedFilter} trades in your history` 
                          : 'Start trading to see your transaction history here'
                        }
                      </p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}