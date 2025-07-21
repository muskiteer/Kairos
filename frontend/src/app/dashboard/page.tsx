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
  { symbol: "ethereum", name: "Ethereum", ticker: "ETH", color: "text-purple-600" },
  { symbol: "bitcoin", name: "Bitcoin", ticker: "BTC", color: "text-orange-600" },
  { symbol: "usd-coin", name: "USD Coin", ticker: "USDC", color: "text-green-600" },
  { symbol: "dai", name: "Dai", ticker: "DAI", color: "text-yellow-600" },
  { symbol: "uniswap", name: "Uniswap", ticker: "UNI", color: "text-pink-600" },
  { symbol: "chainlink", name: "Chainlink", ticker: "LINK", color: "text-blue-500" },
  { symbol: "tether", name: "Tether", ticker: "USDT", color: "text-green-500" },
  { symbol: "wrapped-bitcoin", name: "Wrapped Bitcoin", ticker: "WBTC", color: "text-orange-500" }
]

interface TokenPrice {
  symbol: string
  ticker: string
  name: string
  price: number
  change24h: number
  timestamp: string
}

interface TokenBalance {
  symbol: string
  ticker: string
  amount: number
  value: number
}

interface NewsItem {
  title: string
  source: string
  date: string
  sentiment: 'bullish' | 'bearish' | 'neutral'
  url: string
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
    totalTokens: 10,
    topHolding: "ETH",
    dayChange: 0
  })
  const [newsItems, setNewsItems] = useState<NewsItem[]>([])
  const [isLoadingPrices, setIsLoadingPrices] = useState(false)
  const [isLoadingNews, setIsLoadingNews] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  // Parse RSS feed
  const parseRSSFeed = async (url: string): Promise<NewsItem[]> => {
    try {
      // Use a CORS proxy for RSS feeds
      const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`
      const response = await fetch(proxyUrl)
      const text = await response.text()
      
      const parser = new DOMParser()
      const doc = parser.parseFromString(text, 'application/xml')
      const items = doc.querySelectorAll('item')
      
      const news: NewsItem[] = []
      items.forEach((item, index) => {
        if (index < 5) { // Limit to 5 items per source
          const title = item.querySelector('title')?.textContent || ''
          const pubDate = item.querySelector('pubDate')?.textContent || ''
          const link = item.querySelector('link')?.textContent || ''
          
          let source = 'Unknown'
          if (url.includes('coindesk')) source = 'CoinDesk'
          else if (url.includes('cointelegraph')) source = 'Cointelegraph'
          else if (url.includes('cryptoslate')) source = 'CryptoSlate'
          
          // Simple sentiment analysis based on keywords
          const titleLower = title.toLowerCase()
          let sentiment: 'bullish' | 'bearish' | 'neutral' = 'neutral'
          
          const bullishWords = ['rise', 'surge', 'rally', 'bull', 'up', 'gain', 'growth', 'positive', 'breakthrough']
          const bearishWords = ['fall', 'drop', 'crash', 'bear', 'down', 'decline', 'loss', 'negative', 'warning']
          
          if (bullishWords.some(word => titleLower.includes(word))) {
            sentiment = 'bullish'
          } else if (bearishWords.some(word => titleLower.includes(word))) {
            sentiment = 'bearish'
          }
          
          news.push({
            title,
            source,
            date: new Date(pubDate).toLocaleDateString(),
            sentiment,
            url: link
          })
        }
      })
      
      return news
    } catch (error) {
      console.error(`Failed to parse RSS feed ${url}:`, error)
      return []
    }
  }

  // Fetch token prices from CoinGecko
  const loadAllPrices = async () => {
    setIsLoadingPrices(true)
    try {
      const tokenIds = TOP_TOKENS.map(token => token.symbol).join(',')
      const response = await fetch(
        `https://api.coingecko.com/api/v3/simple/price?ids=${tokenIds}&vs_currencies=usd&include_24hr_change=true`
      )
      
      if (response.ok) {
        const data = await response.json()
        const prices: Record<string, TokenPrice> = {}
        
        TOP_TOKENS.forEach(token => {
          if (data[token.symbol]) {
            prices[token.symbol] = {
              symbol: token.symbol,
              ticker: token.ticker,
              name: token.name,
              price: data[token.symbol].usd,
              change24h: data[token.symbol].usd_24h_change || 0,
              timestamp: new Date().toISOString()
            }
          }
        })
        
        setTokenPrices(prices)
        
        // Generate portfolio balances with ETH as top holding
        const balances: Record<string, TokenBalance> = {}
        const basePortfolioValue = 30000 + Math.random() * 1000 // 30000-31000 range
        
        // ETH gets 40% allocation (top holding)
        const ethPrice = prices['ethereum']?.price || 3000
        const ethAllocation = basePortfolioValue * 0.4
        const ethAmount = ethAllocation / ethPrice
        
        balances['ethereum'] = {
          symbol: 'ethereum',
          ticker: 'ETH',
          amount: ethAmount,
          value: ethAllocation
        }
        
        // Distribute remaining 60% among other tokens
        const remainingValue = basePortfolioValue * 0.6
        const otherTokens = TOP_TOKENS.filter(t => t.symbol !== 'ethereum')
        
        otherTokens.forEach((token, index) => {
          const tokenPrice = prices[token.symbol]
          if (tokenPrice) {
            // Randomly assign between 5-15% of remaining value
            const allocation = (remainingValue / otherTokens.length) * (0.8 + Math.random() * 0.4)
            const amount = allocation / tokenPrice.price
            
            balances[token.symbol] = {
              symbol: token.symbol,
              ticker: token.ticker,
              amount: amount,
              value: allocation
            }
          }
        })
        
        setTokenBalances(balances)
        
        // Calculate portfolio stats
        const totalValue = Object.values(balances).reduce((sum, balance) => sum + balance.value, 0)
        const dayChange = (Math.random() - 0.5) * 10 // Random daily change between -5% and +5%
        
        setPortfolioStats({
          totalValue,
          totalTokens: 10,
          topHolding: "ETH",
          dayChange
        })
      }
    } catch (error) {
      console.error('Failed to fetch prices:', error)
    }
    setIsLoadingPrices(false)
    setLastUpdate(new Date())
  }

  // Fetch latest crypto news from RSS feeds
  const loadLatestNews = async () => {
    setIsLoadingNews(true)
    try {
      const rssFeeds = [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
        "https://cryptoslate.com/feed/"
      ]
      
      const allNews: NewsItem[] = []
      
      for (const feed of rssFeeds) {
        const feedNews = await parseRSSFeed(feed)
        allNews.push(...feedNews)
      }
      
      // Sort by date and take latest 10 items
      const sortedNews = allNews
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
        .slice(0, 10)
      
      setNewsItems(sortedNews)
    } catch (error) {
      console.error('Failed to fetch news:', error)
    }
    setIsLoadingNews(false)
  }

  // Auto-refresh data
  useEffect(() => {
    loadAllPrices()
    loadLatestNews()

    const priceInterval = setInterval(loadAllPrices, 30000) // Every 30 seconds
    const newsInterval = setInterval(loadLatestNews, 300000) // Every 5 minutes

    return () => {
      clearInterval(priceInterval)
      clearInterval(newsInterval)
    }
  }, [])

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
                loadLatestNews()
              }}
              disabled={isLoadingPrices || isLoadingNews}
            >
              {(isLoadingPrices || isLoadingNews) ? (
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
                <div className="text-2xl font-bold">{portfolioStats.topHolding}</div>
                <p className="text-xs text-muted-foreground">
                  {tokenBalances['ethereum'] 
                    ? formatValue(tokenBalances['ethereum'].value)
                    : "Loading..."}
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
                      
                      return (
                        <div key={token.symbol} className="flex items-center justify-between p-3 rounded-lg border">
                          <div className="flex items-center gap-3">
                            <div className={`w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs font-bold ${token.color}`}>
                              {token.ticker.slice(0, 2)}
                            </div>
                            <div>
                              <p className="font-medium">{token.ticker}</p>
                              <p className="text-xs text-muted-foreground">{token.name}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="font-medium">
                              {priceData ? formatPrice(priceData.price) : 'Loading...'}
                            </p>
                            {priceData && (
                              <p className={`text-xs flex items-center ${priceData.change24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {priceData.change24h >= 0 ? (
                                  <TrendingUp className="h-3 w-3 mr-1" />
                                ) : (
                                  <TrendingDown className="h-3 w-3 mr-1" />
                                )}
                                {Math.abs(priceData.change24h).toFixed(2)}%
                              </p>
                            )}
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
                              {token.ticker.slice(0, 2)}
                            </div>
                            <div>
                              <p className="font-medium">{token.ticker}</p>
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
                      <div key={index} className="p-3 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors"
                           onClick={() => window.open(news.url, '_blank')}>
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