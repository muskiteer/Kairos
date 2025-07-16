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
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  TrendingUp, 
  TrendingDown,
  DollarSign, 
  Wallet, 
  RefreshCw,
  Activity,
  BarChart3,
  Newspaper,
  Eye,
  ArrowUpRight,
  ArrowDownRight,
  Loader2
} from "lucide-react"

// Supported tokens for price tracking
const TOP_TOKENS = [
  { symbol: "WETH", name: "Wrapped Ether", color: "text-blue-600" },
  { symbol: "WBTC", name: "Wrapped Bitcoin", color: "text-orange-600" },
  { symbol: "USDC", name: "USD Coin", color: "text-green-600" },
  { symbol: "DAI", name: "Dai Stablecoin", color: "text-yellow-600" },
  { symbol: "UNI", name: "Uniswap", color: "text-pink-600" },
  { symbol: "LINK", name: "Chainlink", color: "text-blue-500" },
  { symbol: "USDT", name: "Tether USD", color: "text-green-500" },
  { symbol: "ETH", name: "Ethereum", color: "text-purple-600" }
]

interface TokenPrice {
  symbol: string
  price: number
  change24h?: number
  timestamp: string
}

interface TokenBalance {
  symbol: string
  amount: number
  value: number
}

interface NewsItem {
  title: string
  source: string
  date: string
  sentiment?: 'bullish' | 'bearish' | 'neutral'
}

interface PortfolioStats {
  totalValue: number
  totalTokens: number
  topHolding: string
  dayChange: number
}

export default function DashboardPage() {
  const [tokenPrices, setTokenPrices] = useState<Record<string, TokenPrice>>({})
  const [tokenBalances, setTokenBalances] = useState<Record<string, TokenBalance>>({})
  const [portfolioStats, setPortfolioStats] = useState<PortfolioStats>({
    totalValue: 0,
    totalTokens: 0,
    topHolding: "",
    dayChange: 0
  })
  const [newsItems, setNewsItems] = useState<NewsItem[]>([])
  const [isLoadingPrices, setIsLoadingPrices] = useState(false)
  const [isLoadingBalances, setIsLoadingBalances] = useState(false)
  const [isLoadingNews, setIsLoadingNews] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  // Fetch token price
  const fetchTokenPrice = async (symbol: string): Promise<TokenPrice | null> => {
    try {
      const response = await fetch(`http://localhost:8000/api/price/${symbol}`)
      if (response.ok) {
        const data = await response.json()
        return {
          symbol,
          price: data.price || 0,
          timestamp: data.timestamp
        }
      }
    } catch (error) {
      console.error(`Failed to fetch ${symbol} price:`, error)
    }
    return null
  }

  // Fetch token balance
  const fetchTokenBalance = async (symbol: string): Promise<TokenBalance | null> => {
    try {
      const response = await fetch(`http://localhost:8000/api/balance/${symbol}`)
      if (response.ok) {
        const data = await response.json()
        const amount = data.amount || 0
        const price = tokenPrices[symbol]?.price || 0
        return {
          symbol,
          amount,
          value: amount * price
        }
      }
    } catch (error) {
      console.error(`Failed to fetch ${symbol} balance:`, error)
    }
    return null
  }

  // Fetch all token prices
  const loadAllPrices = async () => {
    setIsLoadingPrices(true)
    const prices: Record<string, TokenPrice> = {}
    
    for (const token of TOP_TOKENS) {
      const priceData = await fetchTokenPrice(token.symbol)
      if (priceData) {
        prices[token.symbol] = priceData
      }
    }
    
    setTokenPrices(prices)
    setIsLoadingPrices(false)
    setLastUpdate(new Date())
  }

  // Fetch all token balances
  const loadAllBalances = async () => {
    setIsLoadingBalances(true)
    const balances: Record<string, TokenBalance> = {}
    
    for (const token of TOP_TOKENS) {
      const balanceData = await fetchTokenBalance(token.symbol)
      if (balanceData) {
        balances[token.symbol] = balanceData
      }
    }
    
    setTokenBalances(balances)
    
    // Calculate portfolio stats
    const totalValue = Object.values(balances).reduce((sum, balance) => sum + balance.value, 0)
    const activeTokens = Object.values(balances).filter(balance => balance.amount > 0).length
    const topHolding = Object.entries(balances)
      .sort(([,a], [,b]) => b.value - a.value)
      .find(([, balance]) => balance.amount > 0)?.[0] || ""
    
    setPortfolioStats({
      totalValue,
      totalTokens: activeTokens,
      topHolding,
      dayChange: Math.random() * 10 - 5 // Mock change for demo
    })
    
    setIsLoadingBalances(false)
  }

  // Fetch latest crypto news
  const loadLatestNews = async () => {
  setIsLoadingNews(true)
  try {
    const response = await fetch('http://localhost:8000/api/news?limit=6&news_type=trending', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (response.ok) {
      const data = await response.json()
      console.log('News data received:', data) // Debug log
      
      // Use the direct news data from our API
      if (data.news && Array.isArray(data.news)) {
        const parsedNews = data.news.map((item: any, index: number) => ({
          title: item.title || 'No title',
          source: item.source || 'CoinPanic',
          date: new Date(item.published_at || Date.now()).toLocaleDateString(),
          sentiment: item.votes?.positive > item.votes?.negative ? 'bullish' : 
                    item.votes?.negative > item.votes?.positive ? 'bearish' : 'neutral',
          url: item.url || '#'
        }))
        setNewsItems(parsedNews)
      } else {
        console.warn('No news items found in response')
        setNewsItems([])
      }
    } else {
      console.error('News API response not ok:', response.status)
    }
  } catch (error) {
    console.error('Failed to fetch news:', error)
    setNewsItems([])
  }
  setIsLoadingNews(false)
}

  // Auto-refresh data
  useEffect(() => {
    loadAllPrices()
    loadAllBalances()
    loadLatestNews()

    const priceInterval = setInterval(loadAllPrices, 30000) // Every 30 seconds
    const balanceInterval = setInterval(loadAllBalances, 60000) // Every minute
    const newsInterval = setInterval(loadLatestNews, 300000) // Every 5 minutes

    return () => {
      clearInterval(priceInterval)
      clearInterval(balanceInterval)
      clearInterval(newsInterval)
    }
  }, [])

  // Update balances when prices change
  useEffect(() => {
    if (Object.keys(tokenPrices).length > 0) {
      loadAllBalances()
    }
  }, [tokenPrices])

  const formatPrice = (price: number) => {
    if (price >= 1000) {
      return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    }
    return `$${price.toFixed(4)}`
  }

  const formatValue = (value: number) => {
    return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  return (
    <SidebarProvider>
      <AppSidebar activePage="dashboard" />
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
                  <BreadcrumbLink href="/dashboard">Kairos</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbItem>
                  <BreadcrumbPage>Dashboard</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
          <div className="ml-auto px-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                loadAllPrices()
                loadAllBalances()
                loadLatestNews()
              }}
              disabled={isLoadingPrices || isLoadingBalances || isLoadingNews}
            >
              {(isLoadingPrices || isLoadingBalances || isLoadingNews) ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Refresh All
            </Button>
          </div>
        </header>

        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          {/* Portfolio Overview Cards */}
          <div className="grid auto-rows-min gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Portfolio</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatValue(portfolioStats.totalValue)}</div>
                <p className="text-xs text-muted-foreground flex items-center">
                  {portfolioStats.dayChange >= 0 ? (
                    <ArrowUpRight className="h-3 w-3 text-green-600 mr-1" />
                  ) : (
                    <ArrowDownRight className="h-3 w-3 text-red-600 mr-1" />
                  )}
                  {Math.abs(portfolioStats.dayChange).toFixed(2)}% from yesterday
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Tokens</CardTitle>
                <Wallet className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{portfolioStats.totalTokens}</div>
                <p className="text-xs text-muted-foreground">
                  Out of {TOP_TOKENS.length} supported
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Top Holding</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{portfolioStats.topHolding || "N/A"}</div>
                <p className="text-xs text-muted-foreground">
                  {portfolioStats.topHolding && tokenBalances[portfolioStats.topHolding] 
                    ? formatValue(tokenBalances[portfolioStats.topHolding].value)
                    : "No holdings"}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Last Update</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">Live</div>
                <p className="text-xs text-muted-foreground">
                  {lastUpdate.toLocaleTimeString()}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Main Content Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* Live Token Prices */}
            <Card className="md:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Live Token Prices
                  {isLoadingPrices && <Loader2 className="h-4 w-4 animate-spin" />}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  <div className="space-y-3">
                    {TOP_TOKENS.map((token) => {
                      const priceData = tokenPrices[token.symbol]
                      const change = Math.random() * 10 - 5 // Mock 24h change
                      
                      return (
                        <div key={token.symbol} className="flex items-center justify-between p-3 rounded-lg border">
                          <div className="flex items-center gap-3">
                            <div className={`w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs font-bold ${token.color}`}>
                              {token.symbol.slice(0, 2)}
                            </div>
                            <div>
                              <p className="font-medium">{token.symbol}</p>
                              <p className="text-xs text-muted-foreground">{token.name}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="font-medium">
                              {priceData ? formatPrice(priceData.price) : 'Loading...'}
                            </p>
                            <p className={`text-xs flex items-center ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {change >= 0 ? (
                                <TrendingUp className="h-3 w-3 mr-1" />
                              ) : (
                                <TrendingDown className="h-3 w-3 mr-1" />
                              )}
                              {Math.abs(change).toFixed(2)}%
                            </p>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Portfolio Holdings */}
            <Card className="md:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Wallet className="h-5 w-5" />
                  Portfolio Holdings
                  {isLoadingBalances && <Loader2 className="h-4 w-4 animate-spin" />}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  <div className="space-y-3">
                    {TOP_TOKENS.map((token) => {
                      const balance = tokenBalances[token.symbol]
                      const hasBalance = balance && balance.amount > 0
                      
                      return (
                        <div key={token.symbol} className={`flex items-center justify-between p-3 rounded-lg border ${hasBalance ? 'bg-muted/50' : 'opacity-50'}`}>
                          <div className="flex items-center gap-3">
                            <div className={`w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs font-bold ${token.color}`}>
                              {token.symbol.slice(0, 2)}
                            </div>
                            <div>
                              <p className="font-medium">{token.symbol}</p>
                              <p className="text-xs text-muted-foreground">
                                {balance ? balance.amount.toFixed(6) : '0.000000'}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="font-medium">
                              {balance ? formatValue(balance.value) : '$0.00'}
                            </p>
                            {hasBalance && (
                              <Badge variant="secondary" className="text-xs">
                                Active
                              </Badge>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Latest Crypto News */}
            <Card className="md:col-span-2 lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Newspaper className="h-5 w-5" />
                  Latest Crypto News
                  {isLoadingNews && <Loader2 className="h-4 w-4 animate-spin" />}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  <div className="space-y-4">
                    {newsItems.map((news, index) => (
                      <div key={index} className="p-3 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors">
                        <div className="flex items-start gap-2 mb-2">
                          <Badge 
                            variant={
                              news.sentiment === 'bullish' ? 'default' : 
                              news.sentiment === 'bearish' ? 'destructive' : 
                              'secondary'
                            }
                            className="text-xs"
                          >
                            {news.sentiment === 'bullish' ? '📈 Bullish' : 
                             news.sentiment === 'bearish' ? '📉 Bearish' : 
                             '📰 Neutral'}
                          </Badge>
                        </div>
                        <h4 className="font-medium text-sm leading-tight mb-2 line-clamp-2">
                          {news.title}
                        </h4>
                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                          <span>{news.source}</span>
                          <span>{news.date}</span>
                        </div>
                      </div>
                    ))}
                    
                    {newsItems.length === 0 && !isLoadingNews && (
                      <div className="text-center text-muted-foreground py-8">
                        <Newspaper className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p>No news available</p>
                        <p className="text-xs">Check your connection</p>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 md:grid-cols-4">
                <Button variant="outline" className="h-16">
                  <div className="text-center">
                    <ArrowUpRight className="h-5 w-5 mx-auto mb-1" />
                    <p className="text-xs">Buy Crypto</p>
                  </div>
                </Button>
                <Button variant="outline" className="h-16">
                  <div className="text-center">
                    <ArrowDownRight className="h-5 w-5 mx-auto mb-1" />
                    <p className="text-xs">Sell Crypto</p>
                  </div>
                </Button>
                <Button variant="outline" className="h-16">
                  <div className="text-center">
                    <Eye className="h-5 w-5 mx-auto mb-1" />
                    <p className="text-xs">View Portfolio</p>
                  </div>
                </Button>
                <Button variant="outline" className="h-16">
                  <div className="text-center">
                    <BarChart3 className="h-5 w-5 mx-auto mb-1" />
                    <p className="text-xs">Trading Charts</p>
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}