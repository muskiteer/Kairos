"use client"

import { useState, useEffect, createContext, useContext, ReactNode } from 'react'
import { useRouter } from 'next/navigation'

interface WalletInfo {
  address: string
  chainId: string
  isConnected: boolean
}

interface AuthContextType {
  wallet: WalletInfo | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (walletData: WalletInfo) => void
  logout: () => void
  updateWallet: (walletData: Partial<WalletInfo>) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Helper function to handle cookie operations
const cookies = {
  set: (name: string, value: string, days: number = 7) => {
    const expires = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toUTCString()
    document.cookie = `${name}=${value}; path=/; max-age=${days * 24 * 60 * 60}; SameSite=Strict`
  },
  delete: (name: string) => {
    document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict`
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [wallet, setWallet] = useState<WalletInfo | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  const isAuthenticated = Boolean(wallet?.isConnected && wallet?.address)

  // Load wallet data on mount
  useEffect(() => {
    const loadWalletData = () => {
      try {
        const savedWallet = localStorage.getItem('kairos_wallet')
        if (savedWallet) {
          const walletData = JSON.parse(savedWallet)
          if (walletData?.isConnected && walletData?.address) {
            setWallet(walletData)
            // Also set as cookie for middleware
            cookies.set('kairos_wallet', JSON.stringify(walletData))
          }
        }
      } catch (error) {
        console.error('Error loading wallet data:', error)
        // Clear corrupted data
        localStorage.removeItem('kairos_wallet')
        cookies.delete('kairos_wallet')
      } finally {
        setIsLoading(false)
      }
    }

    loadWalletData()

    // Listen for storage changes (logout in another tab)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'kairos_wallet') {
        if (e.newValue) {
          try {
            const walletData = JSON.parse(e.newValue)
            setWallet(walletData)
          } catch (error) {
            setWallet(null)
          }
        } else {
          setWallet(null)
          cookies.delete('kairos_wallet')
        }
      }
    }

    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [])

  const login = (walletData: WalletInfo) => {
    try {
      // Ensure isConnected is set to true
      const updatedWalletData = {
        ...walletData,
        isConnected: true
      }
      
      // Update state
      setWallet(updatedWalletData)
      
      // Save to localStorage
      localStorage.setItem('kairos_wallet', JSON.stringify(updatedWalletData))
      
      // Set cookie for middleware
      cookies.set('kairos_wallet', JSON.stringify(updatedWalletData))
    } catch (error) {
      console.error('Error saving wallet data:', error)
    }
  }

  const logout = () => {
    // Clear state
    setWallet(null)
    
    // Clear localStorage
    localStorage.removeItem('kairos_wallet')
    
    // Clear cookie
    cookies.delete('kairos_wallet')
    
    // Redirect to login
    router.push('/login')
  }

  const updateWallet = (walletData: Partial<WalletInfo>) => {
    if (wallet) {
      const updatedWallet = { ...wallet, ...walletData }
      
      // Update state
      setWallet(updatedWallet)
      
      // Update localStorage
      localStorage.setItem('kairos_wallet', JSON.stringify(updatedWallet))
      
      // Update cookie
      cookies.set('kairos_wallet', JSON.stringify(updatedWallet))
    }
  }

  return (
    <AuthContext.Provider
      value={{
        wallet,
        isLoading,
        isAuthenticated,
        login,
        logout,
        updateWallet,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}