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
  ArrowRightLeft, 
  Wallet, 
  TrendingUp, 
  DollarSign, 
  AlertTriangle,
  CheckCircle,
  Loader2,
  RefreshCw,
  BarChart3
} from "lucide-react"

// Supported tokens based on execute.py
const SUPPORTED_TOKENS = {
  "USDC": { name: "USD Coin", symbol: "USDC", decimals: 6 },
  "WETH": { name: "Wrapped Ether", symbol: "WETH", decimals: 18 },
  "WBTC": { name: "Wrapped Bitcoin", symbol: "WBTC", decimals: 8 },
  "DAI": { name: "Dai Stablecoin", symbol: "DAI", decimals: 18 },
  "USDT": { name: "Tether USD", symbol: "USDT", decimals: 6 },
  "UNI": { name: "Uniswap", symbol: "UNI", decimals: 18 },
  "LINK": { name: "Chainlink", symbol: "LINK", decimals: 18 },
  "ETH": { name: "Ethereum", symbol: "ETH", decimals: 18 }
}

interface TokenBalance {
  amount: number
  token: string
}

interface TokenPrice {
  price: number
  symbol: string
}

interface TradeResult {
  success: boolean
  message: string
  txHash?: string
  toTokenAmount?: number
  gasUsed?: number
}

export default function ManualTradePage() {
  const [fromToken, setFromToken] = useState<string>("")
  const [toToken, setToToken] = useState<string>("")
  const [amount, setAmount] = useState<string>("")
  const [isLoading, setIsLoading] = useState(false)
  const [balances, setBalances] = useState<Record<string, number>>({})
  const [prices, setPrices] = useState<Record<string, number>>({})
  const [tradeResult, setTradeResult] = useState<TradeResult | null>(null)
  const [loadingBalances, setLoadingBalances] = useState(false)
  const [loadingPrices, setLoadingPrices] = useState(false)
  const [selectedPair, setSelectedPair] = useState<string>("WETH")

  // Fetch token balances
  const fetchBalance = async (token: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/balance/${token}`)
      if (response.ok) {
        const data = await response.json()
        return data.amount || 0
      }
    } catch (error) {
      console.error(`Failed to fetch ${token} balance:`, error)
    }
    return 0
  }

  // Fetch token price
  const fetchPrice = async (token: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/price/${token}`)
      if (response.ok) {
        const data = await response.json()
        return data.price || 0
      }
    } catch (error) {
      console.error(`Failed to fetch ${token} price:`, error)
    }
    return 0
  }

  // Load all balances
  const loadBalances = async () => {
    setLoadingBalances(true)
    const newBalances: Record<string, number> = {}
    
    for (const token of Object.keys(SUPPORTED_TOKENS)) {
      newBalances[token] = await fetchBalance(token)
    }
    
    setBalances(newBalances)
    setLoadingBalances(false)
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

    if (balances[fromToken] < amountNum) {
      setTradeResult({
        success: false,
        message: `Insufficient balance. Available: ${balances[fromToken]} ${fromToken}`
      })
      return
    }

    setIsLoading(true)
    setTradeResult(null)

    try {
      const response = await fetch('http://localhost:8000/api/trade', {
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
        
        // Refresh balances after successful trade
        await loadBalances()
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
    
    const fromPrice = prices[fromToken] || 0
    const toPrice = prices[toToken] || 0
    
    if (fromPrice === 0 || toPrice === 0) return 0
    
    return (amountNum * fromPrice) / toPrice
  }

  // Load initial data
  useEffect(() => {
    loadBalances()
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
                    ${Object.entries(balances).reduce((total, [token, balance]) => {
                      return total + (balance * (prices[token] || 0))
                    }, 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Total holdings
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
                    {Object.values(balances).filter(balance => balance > 0).length}
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
                    <select
                      value={fromToken}
                      onChange={(e) => setFromToken(e.target.value)}
                      className="flex-1 h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                    >
                      <option value="">Select token to sell</option>
                      {Object.entries(SUPPORTED_TOKENS).map(([symbol, token]) => (
                        <option key={symbol} value={symbol}>
                          {symbol} - {token.name} ({balances[symbol]?.toFixed(6) || '0.000000'})
                        </option>
                      ))}
                    </select>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={loadBalances}
                      disabled={loadingBalances}
                    >
                      {loadingBalances ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <RefreshCw className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  {fromToken && (
                    <p className="text-sm text-muted-foreground">
                      Available: {balances[fromToken]?.toFixed(6) || '0.000000'} {fromToken}
                      {prices[fromToken] && (
                        <span className="ml-2">
                          (${prices[fromToken].toFixed(4)})
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
                        onClick={() => setAmount(balances[fromToken]?.toString() || "0")}
                      >
                        Max
                      </Button>
                    )}
                  </div>
                </div>

                {/* To Token */}
                <div className="space-y-2">
                  <Label>To Token</Label>
                  <select
                    value={toToken}
                    onChange={(e) => setToToken(e.target.value)}
                    className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option value="">Select token to buy</option>
                    {Object.entries(SUPPORTED_TOKENS)
                      .filter(([symbol]) => symbol !== fromToken)
                      .map(([symbol, token]) => (
                      <option key={symbol} value={symbol}>
                        {symbol} - {token.name} (${prices[symbol]?.toFixed(4) || '0.0000'})
                      </option>
                    ))}
                  </select>
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
                  {Object.entries(SUPPORTED_TOKENS).map(([symbol, token]) => {
                    const balance = balances[symbol] || 0
                    const price = prices[symbol] || 0
                    const value = balance * price
                    
                    return (
                      <div key={symbol} className="flex items-center justify-between p-2 rounded-lg border">
                        <div>
                          <p className="font-medium">{symbol}</p>
                          <p className="text-sm text-muted-foreground">{token.name}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">{balance.toFixed(6)}</p>
                          <p className="text-sm text-muted-foreground">
                            ${value.toFixed(2)} ({price > 0 ? `$${price.toFixed(4)}` : 'N/A'})
                          </p>
                        </div>
                      </div>
                    )
                  })}
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
                </CardTitle>
                <div className="grid grid-cols-4 gap-2 w-full">
                  {["WETH", "WBTC", "UNI", "LINK"].map((pair) => (
                    <Button
                      key={pair}
                      variant={selectedPair === pair ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedPair(pair)}
                    >
                      {pair}/USD
                    </Button>
                  ))}
                </div>
              </CardHeader>
              <CardContent className="flex-1 p-0">
                <div className="h-full min-h-[600px] w-full">
                  <iframe
                    src={`https://s.tradingview.com/widgetembed/?frameElementId=tradingview_widget&symbol=${selectedPair}USD&interval=15&hidesidetoolbar=1&hidetoptoolbar=1&symboledit=1&saveimage=1&toolbarbg=F1F3F6&studies=[]&hideideas=1&theme=light&style=1&timezone=Etc%2FUTC&studies_overrides={}&overrides={}&enabled_features=[]&disabled_features=[]&locale=en&utm_source=localhost&utm_medium=widget&utm_campaign=chart&utm_term=${selectedPair}USD`}
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