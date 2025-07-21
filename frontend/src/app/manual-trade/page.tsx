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
import { 
  ArrowRightLeft, 
  Wallet, 
  TrendingUp, 
  DollarSign, 
  AlertTriangle,
  CheckCircle,
  Loader2,
  RefreshCw,
  BarChart3,
  LineChart,
  CandlestickChart,
  TrendingDown,
  Activity
} from "lucide-react"
import { getApiUrl } from '@/lib/config'
// Supported tokens based on portfolio API

const SUPPORTED_TOKENS = {
  "USDC": { name: "USD Coin", symbol: "USDC", decimals: 6 },
  "USDbC": { name: "USD Base Coin", symbol: "USDbC", decimals: 6 },
  "WETH": { name: "Wrapped Ether", symbol: "WETH", decimals: 18 },
  "WBTC": { name: "Wrapped Bitcoin", symbol: "WBTC", decimals: 8 },
  "DAI": { name: "Dai Stablecoin", symbol: "DAI", decimals: 18 },
  "USDT": { name: "Tether USD", symbol: "USDT", decimals: 6 },
  "UNI": { name: "Uniswap", symbol: "UNI", decimals: 18 },
  "LINK": { name: "Chainlink", symbol: "LINK", decimals: 18 },
  "ETH": { name: "Ethereum", symbol: "ETH", decimals: 18 },
  "AAVE": { name: "Aave", symbol: "AAVE", decimals: 18 },
  "MATIC": { name: "Polygon", symbol: "MATIC", decimals: 18 },
  "SOL": { name: "Solana", symbol: "SOL", decimals: 9 },
  "USDC_SOL": { name: "USDC (Solana)", symbol: "USDC_SOL", decimals: 6 }, // Added this!
  "PEPE": { name: "Pepe", symbol: "PEPE", decimals: 18 },
  "SHIB": { name: "Shiba Inu", symbol: "SHIB", decimals: 18 }
}

interface TokenBalance {
  token: string
  balance: number
  price: number
  usd_value: number
  chain?: string
  tokenAddress?: string
}

interface PortfolioData {
  balances: TokenBalance[]
  total_value: number
  real_total_value: number
  user_id: string
  timestamp: string
  agent_id?: string
}

interface TradeResult {
  success: boolean
  message: string
  txHash?: string
  toTokenAmount?: number
  gasUsed?: number
}

interface ChartOption {
  id: string
  name: string
  symbol: string
  icon: React.ReactNode
}

export default function ManualTradePage() {
  const [fromToken, setFromToken] = useState<string>("")
  const [toToken, setToToken] = useState<string>("")
  const [amount, setAmount] = useState<string>("")
  const [isLoading, setIsLoading] = useState(false)
  const [portfolioData, setPortfolioData] = useState<PortfolioData | null>(null)
  const [prices, setPrices] = useState<Record<string, number>>({})
  const [tradeResult, setTradeResult] = useState<TradeResult | null>(null)
  const [loadingPortfolio, setLoadingPortfolio] = useState(false)
  const [loadingPrices, setLoadingPrices] = useState(false)
  const [selectedChart, setSelectedChart] = useState<string>("WETH")
  const [chartDialogOpen, setChartDialogOpen] = useState(false)

  // Chart options for the modal
  const chartOptions: ChartOption[] = [
    { id: "WETH", name: "Ethereum", symbol: "WETH/USD", icon: <TrendingUp className="h-4 w-4" /> },
    { id: "WBTC", name: "Bitcoin", symbol: "WBTC/USD", icon: <BarChart3 className="h-4 w-4" /> },
    { id: "UNI", name: "Uniswap", symbol: "UNI/USD", icon: <LineChart className="h-4 w-4" /> },
    { id: "LINK", name: "Chainlink", symbol: "LINK/USD", icon: <Activity className="h-4 w-4" /> },
    { id: "AAVE", name: "Aave", symbol: "AAVE/USD", icon: <CandlestickChart className="h-4 w-4" /> },
    { id: "MATIC", name: "Polygon", symbol: "MATIC/USD", icon: <TrendingDown className="h-4 w-4" /> },
    { id: "SOL", name: "Solana", symbol: "SOL/USD", icon: <TrendingUp className="h-4 w-4" /> },
    { id: "PEPE", name: "Pepe", symbol: "PEPE/USD", icon: <BarChart3 className="h-4 w-4" /> }
  ]

  // Fetch portfolio data from API
  const fetchPortfolio = async () => {
    setLoadingPortfolio(true)
    try {
      const response = await fetch(getApiUrl('/api/portfolio'))
      if (response.ok) {
        const data = await response.json()
        setPortfolioData(data)
      } else {
        console.error('Failed to fetch portfolio')
      }
    } catch (error) {
      console.error('Error fetching portfolio:', error)
    } finally {
      setLoadingPortfolio(false)
    }
  }

  // Fetch token price
  const fetchPrice = async (token: string) => {
    try {
      // const response = await fetch(getApiUrl('/api/portfolio'))
      const response = await fetch(getApiUrl(`/api/price/${token}`))
      if (response.ok) {
        const data = await response.json()
        return data.price || 0
      }
    } catch (error) {
      console.error(`Failed to fetch ${token} price:`, error)
    }
    return 0
  }

  // Load all prices
  const loadPrices = async () => {
    setLoadingPrices(true)
    const newPrices: Record<string, number> = {}
    
    for (const token of Object.keys(SUPPORTED_TOKENS)) {
      newPrices[token] = await fetchPrice(token)
    }
    
    setPrices(newPrices)
    setLoadingPrices(false)
  }

  // Get balance for a specific token
  const getTokenBalance = (token: string): number => {
    if (!portfolioData) return 0
    const balance = portfolioData.balances.find(b => b.token === token)
    return balance ? balance.balance : 0
  }

  // Get token price
  const getTokenPrice = (token: string): number => {
    if (!portfolioData) return prices[token] || 0
    const balance = portfolioData.balances.find(b => b.token === token)
    return balance ? balance.price : (prices[token] || 0)
  }

  // Execute trade
  const executeTrade = async () => {
    if (!fromToken || !toToken || !amount) {
      setTradeResult({
        success: false,
        message: "Please fill in all fields"
      })
      return
    }

    const amountNum = parseFloat(amount)
    if (isNaN(amountNum) || amountNum <= 0) {
      setTradeResult({
        success: false,
        message: "Please enter a valid amount"
      })
      return
    }

    const currentBalance = getTokenBalance(fromToken)
    if (currentBalance < amountNum) {
      setTradeResult({
        success: false,
        message: `Insufficient balance. Available: ${currentBalance} ${fromToken}`
      })
      return
    }

    setIsLoading(true)
    setTradeResult(null)

    try {
      const response = await fetch(getApiUrl('/api/trade'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fromToken,
          toToken,
          amount: amountNum,
          timestamp: new Date().toISOString()
        }),
      })

      if (response.ok) {
        const data = await response.json()
        setTradeResult({
          success: true,
          message: `Trade executed successfully! ${amountNum} ${fromToken} → ${toToken}`,
          txHash: data.txHash,
          toTokenAmount: data.toTokenAmount,
          gasUsed: data.gasUsed
        })
        
        // Refresh portfolio after successful trade
        await fetchPortfolio()
      } else {
        const errorData = await response.json()
        setTradeResult({
          success: false,
          message: errorData.message || "Trade execution failed"
        })
      }
    } catch (error) {
      setTradeResult({
        success: false,
        message: "Failed to connect to trading service"
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Calculate estimated output
  const calculateEstimatedOutput = () => {
    if (!amount || !fromToken || !toToken) return 0
    const amountNum = parseFloat(amount)
    if (isNaN(amountNum)) return 0
    
    const fromPrice = getTokenPrice(fromToken)
    const toPrice = getTokenPrice(toToken)
    
    if (fromPrice === 0 || toPrice === 0) return 0
    
    return (amountNum * fromPrice) / toPrice
  }

  // Get tokens available for trading (with non-zero balances)
  const getAvailableTokens = () => {
    if (!portfolioData) return Object.keys(SUPPORTED_TOKENS)
    return portfolioData.balances
      .filter(b => b.balance > 0)
      .map(b => b.token)
      .filter(token => token in SUPPORTED_TOKENS)
  }

  // Load initial data
  useEffect(() => {
    fetchPortfolio()
    loadPrices()
  }, [])

  return (
    <SidebarProvider>
      <AppSidebar activePage="manual-trade" />
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
                  <BreadcrumbPage>Manual Trading</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>

        <div className="flex flex-1 gap-4 p-4 pt-0">
          {/* Trading Panel */}
          <div className="w-1/2 space-y-4">
            {/* Quick Stats Cards */}
            <div className="grid grid-cols-3 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Portfolio Value</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    ${portfolioData?.total_value?.toLocaleString(undefined, { maximumFractionDigits: 2 }) || '0.00'}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Real: ${portfolioData?.real_total_value?.toLocaleString(undefined, { maximumFractionDigits: 2 }) || '0.00'}
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Tokens</CardTitle>
                  <Wallet className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {portfolioData?.balances?.filter(b => b.balance > 0).length || 0}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Non-zero balances
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Status</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">Live</div>
                  <p className="text-xs text-muted-foreground">
                    Trading enabled
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Trading Form */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ArrowRightLeft className="h-5 w-5" />
                  Manual Trade Execution
                  <Badge variant="outline" className="ml-auto">
                    🔥 Real Trading
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>From Token</Label>
                  <div className="flex gap-2">
                    <Select value={fromToken} onValueChange={setFromToken}>
                      <SelectTrigger className="flex-1">
                        <SelectValue placeholder="Select token to sell" />
                      </SelectTrigger>
                      <SelectContent>
                        {getAvailableTokens().map((symbol) => {
                          const token = SUPPORTED_TOKENS[symbol as keyof typeof SUPPORTED_TOKENS]
                          const balance = getTokenBalance(symbol)
                          return (
                            <SelectItem key={symbol} value={symbol}>
                              {symbol} - {token?.name} ({balance.toFixed(6)})
                            </SelectItem>
                          )
                        })}
                      </SelectContent>
                    </Select>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={fetchPortfolio}
                      disabled={loadingPortfolio}
                    >
                      {loadingPortfolio ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <RefreshCw className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  {fromToken && (
                    <p className="text-sm text-muted-foreground">
                      Available: {getTokenBalance(fromToken).toFixed(6)} {fromToken}
                      {getTokenPrice(fromToken) > 0 && (
                        <span className="ml-2">
                          (${getTokenPrice(fromToken).toFixed(4)})
                        </span>
                      )}
                    </p>
                  )}
                </div>

                {/* Amount */}
                <div className="space-y-2">
                  <Label>Amount</Label>
                  <div className="flex gap-2">
                    <Input
                      type="number"
                      step="any"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      placeholder="0.00"
                      className="flex-1"
                    />
                    {fromToken && (
                      <Button
                        variant="outline"
                        onClick={() => setAmount(getTokenBalance(fromToken).toString())}
                      >
                        Max
                      </Button>
                    )}
                  </div>
                </div>

                {/* To Token */}
                <div className="space-y-2">
                  <Label>To Token</Label>
                  <Select value={toToken} onValueChange={setToToken}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select token to buy" />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(SUPPORTED_TOKENS)
                        .filter(([symbol]) => symbol !== fromToken)
                        .map(([symbol, token]) => (
                        <SelectItem key={symbol} value={symbol}>
                          {symbol} - {token.name} (${getTokenPrice(symbol).toFixed(4)})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Estimated Output */}
                {amount && fromToken && toToken && (
                  <div className="p-3 bg-muted rounded-lg">
                    <p className="text-sm font-medium">Estimated Output</p>
                    <p className="text-lg font-bold">
                      ≈ {calculateEstimatedOutput().toFixed(6)} {toToken}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Estimate only • Actual amount may vary due to slippage
                    </p>
                  </div>
                )}

                {/* Execute Button */}
                <Button 
                  onClick={executeTrade}
                  disabled={!fromToken || !toToken || !amount || isLoading}
                  className="w-full"
                  size="lg"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Executing Trade...
                    </>
                  ) : (
                    <>
                      <ArrowRightLeft className="mr-2 h-4 w-4" />
                      Execute Trade
                    </>
                  )}
                </Button>

                {/* Trade Result */}
                {tradeResult && (
                  <Alert className={tradeResult.success ? "border-green-200 bg-green-50 dark:bg-green-950" : "border-red-200 bg-red-50 dark:bg-red-950"}>
                    {tradeResult.success ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-red-600" />
                    )}
                    <AlertDescription>
                      {tradeResult.message}
                      {tradeResult.txHash && (
                        <div className="mt-2 text-xs">
                          <p>Transaction Hash: {tradeResult.txHash}</p>
                          {tradeResult.toTokenAmount && (
                            <p>Received: {tradeResult.toTokenAmount} {toToken}</p>
                          )}
                          {tradeResult.gasUsed && (
                            <p>Gas Used: {tradeResult.gasUsed}</p>
                          )}
                        </div>
                      )}
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>

            {/* Token Balances */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Wallet className="h-5 w-5" />
                  Token Balances
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={loadPrices}
                    disabled={loadingPrices}
                    className="ml-auto"
                  >
                    {loadingPrices ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <RefreshCw className="h-4 w-4" />
                    )}
                    Refresh Prices
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {portfolioData?.balances?.map((balanceItem) => {
                    const token = SUPPORTED_TOKENS[balanceItem.token as keyof typeof SUPPORTED_TOKENS]
                    
                    return (
                      <div key={balanceItem.token} className="flex items-center justify-between p-2 rounded-lg border">
                        <div>
                          <p className="font-medium">{balanceItem.token}</p>
                          <p className="text-sm text-muted-foreground">
                            {token?.name || balanceItem.token} • {balanceItem.chain}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">{balanceItem.balance.toFixed(6)}</p>
                          <p className="text-sm text-muted-foreground">
                            ${balanceItem.usd_value.toFixed(2)} (${balanceItem.price.toFixed(4)})
                          </p>
                        </div>
                      </div>
                    )
                  })}
                  
                  {/* Show supported tokens with zero balance */}
                  {Object.entries(SUPPORTED_TOKENS)
                    .filter(([symbol]) => !portfolioData?.balances?.some(b => b.token === symbol))
                    .map(([symbol, token]) => (
                      <div key={symbol} className="flex items-center justify-between p-2 rounded-lg border opacity-50">
                        <div>
                          <p className="font-medium">{symbol}</p>
                          <p className="text-sm text-muted-foreground">{token.name}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">0.000000</p>
                          <p className="text-sm text-muted-foreground">
                            $0.00 (${getTokenPrice(symbol).toFixed(4)})
                          </p>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* TradingView Chart Panel */}
          <div className="w-1/2">
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  TradingView Chart
                  <Dialog open={chartDialogOpen} onOpenChange={setChartDialogOpen}>
                    <DialogTrigger asChild>
                      <Button variant="outline" size="sm" className="ml-auto">
                        Select Chart
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-md">
                      <DialogHeader>
                        <DialogTitle>Select Trading Chart</DialogTitle>
                        <DialogDescription>
                          Choose a cryptocurrency pair to display on the chart
                        </DialogDescription>
                      </DialogHeader>
                      <div className="grid grid-cols-2 gap-3">
                        {chartOptions.map((option) => (
                          <Button
                            key={option.id}
                            variant={selectedChart === option.id ? "default" : "outline"}
                            className="h-auto p-3 flex flex-col items-center gap-2"
                            onClick={() => {
                              setSelectedChart(option.id)
                              setChartDialogOpen(false)
                            }}
                          >
                            {option.icon}
                            <div className="text-center">
                              <div className="font-medium">{option.name}</div>
                              <div className="text-xs text-muted-foreground">{option.symbol}</div>
                            </div>
                          </Button>
                        ))}
                      </div>
                    </DialogContent>
                  </Dialog>
                </CardTitle>
                <div className="text-sm text-muted-foreground">
                  Currently showing: <span className="font-medium">{selectedChart}/USD</span>
                </div>
              </CardHeader>
              <CardContent className="flex-1 p-0">
                <div className="h-full min-h-[600px] w-full">
                  <iframe
                    src={`https://s.tradingview.com/widgetembed/?frameElementId=tradingview_widget&symbol=${selectedChart}USD&interval=15&hidesidetoolbar=1&hidetoptoolbar=1&symboledit=1&saveimage=1&toolbarbg=F1F3F6&studies=[]&hideideas=1&theme=light&style=1&timezone=Etc%2FUTC&studies_overrides={}&overrides={}&enabled_features=[]&disabled_features=[]&locale=en&utm_source=localhost&utm_medium=widget&utm_campaign=chart&utm_term=${selectedChart}USD`}
                    width="100%"
                    height="100%"
                    frameBorder="0"
                    allowTransparency={true}
                    scrolling="no"
                    allowFullScreen={true}
                    style={{ display: 'block', width: '100%', height: '100%', minHeight: '600px' }}
                  ></iframe>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}