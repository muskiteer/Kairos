"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import {
  BadgeCheck,
  Bell,
  ChevronsUpDown,
  CreditCard,
  LogOut,
  Sparkles,
  Wallet,
  Copy,
  ExternalLink,
  CheckCircle
} from "lucide-react"

import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface WalletInfo {
  address: string
  chainId: string
  isConnected: boolean
}

export function NavUser() {
  const { isMobile } = useSidebar()
  const router = useRouter()
  const [wallet, setWallet] = useState<WalletInfo | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    // Load wallet info from localStorage
    const loadWalletInfo = () => {
      try {
        const savedWallet = localStorage.getItem('kairos_wallet')
        if (savedWallet) {
          const walletInfo = JSON.parse(savedWallet)
          setWallet(walletInfo)
        }
      } catch (error) {
        console.error('Error loading wallet info:', error)
      }
    }

    loadWalletInfo()

    // Listen for storage changes (if user disconnects in another tab)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'kairos_wallet') {
        loadWalletInfo()
      }
    }

    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [])

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`
  }

  const getChainName = (chainId: string) => {
    const chains: { [key: string]: string } = {
      '0x1': 'Ethereum',
      '0x89': 'Polygon',
      '0x38': 'BSC',
      '0xa4b1': 'Arbitrum',
      '0x2105': 'Base'
    }
    return chains[chainId] || 'Unknown'
  }

  const getChainColor = (chainId: string) => {
    const chainColors: { [key: string]: string } = {
      '0x1': 'bg-blue-500',
      '0x89': 'bg-purple-500',
      '0x38': 'bg-yellow-500',
      '0xa4b1': 'bg-cyan-500',
      '0x2105': 'bg-blue-600'
    }
    return chainColors[chainId] || 'bg-gray-500'
  }

  const copyAddress = async () => {
    if (wallet?.address) {
      try {
        await navigator.clipboard.writeText(wallet.address)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch (error) {
        console.error('Failed to copy address:', error)
      }
    }
  }

  const openEtherscan = () => {
    if (wallet?.address) {
      const baseUrl = wallet.chainId === '0x1' 
        ? 'https://etherscan.io' 
        : wallet.chainId === '0x89'
        ? 'https://polygonscan.com'
        : 'https://etherscan.io'
      
      window.open(`${baseUrl}/address/${wallet.address}`, '_blank')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('kairos_wallet')
    setWallet(null)
    router.push('/')
  }

  // If no wallet is connected, show connect prompt
  if (!wallet?.isConnected) {
    return (
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton
            size="lg"
            className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
            onClick={() => router.push('/')}
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-muted">
              <Wallet className="h-4 w-4" />
            </div>
            <div className="grid flex-1 text-left text-sm leading-tight">
              <span className="truncate font-medium">Connect Wallet</span>
              <span className="truncate text-xs text-muted-foreground">Not connected</span>
            </div>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    )
  }

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
            >
              <div className="relative">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 text-white">
                  <Wallet className="h-4 w-4" />
                </div>
                <div className={`absolute -bottom-1 -right-1 h-3 w-3 rounded-full ${getChainColor(wallet.chainId)} border-2 border-background`}></div>
              </div>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-medium">
                  {formatAddress(wallet.address)}
                </span>
                <span className="truncate text-xs text-muted-foreground">
                  {getChainName(wallet.chainId)}
                </span>
              </div>
              <ChevronsUpDown className="ml-auto size-4" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
            side={isMobile ? "bottom" : "right"}
            align="end"
            sideOffset={4}
          >
            <DropdownMenuLabel className="p-0 font-normal">
              <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                <div className="relative">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 text-white">
                    <Wallet className="h-4 w-4" />
                  </div>
                  <div className={`absolute -bottom-1 -right-1 h-3 w-3 rounded-full ${getChainColor(wallet.chainId)} border-2 border-background`}></div>
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-medium">
                    {formatAddress(wallet.address)}
                  </span>
                  <div className="flex items-center gap-1">
                    <Badge variant="secondary" className="text-xs px-1.5 py-0">
                      {getChainName(wallet.chainId)}
                    </Badge>
                    <div className="flex h-2 w-2 rounded-full bg-green-500"></div>
                  </div>
                </div>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            
            {/* Wallet Actions */}
            <DropdownMenuGroup>
              <DropdownMenuItem onClick={copyAddress}>
                {copied ? <CheckCircle className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                {copied ? 'Address Copied!' : 'Copy Address'}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={openEtherscan}>
                <ExternalLink className="h-4 w-4" />
                View on Explorer
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            
            {/* Account Actions */}
            <DropdownMenuGroup>
              <DropdownMenuItem onClick={() => router.push('/profile')}>
                <BadgeCheck className="h-4 w-4" />
                Profile Settings
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Bell className="h-4 w-4" />
                Notifications
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Sparkles className="h-4 w-4" />
                Upgrade to Pro
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            
            {/* Logout */}
            <DropdownMenuItem onClick={handleLogout} className="text-red-600 focus:text-red-600">
              <LogOut className="h-4 w-4" />
              Disconnect Wallet
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}