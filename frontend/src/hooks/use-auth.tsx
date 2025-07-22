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
    document.cookie = `${name}=${value}; path=/; expires=${expires}; SameSite=Strict`
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
          } else {
            // Clear invalid wallet data
            localStorage.removeItem('kairos_wallet')
            cookies.delete('kairos_wallet')
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
  }, []) // Only run on mount

  // Separate effect for event listeners to avoid dependency issues
  useEffect(() => {
    // Listen for storage changes (logout in another tab)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'kairos_wallet') {
        if (e.newValue) {
          try {
            const walletData = JSON.parse(e.newValue)
            if (walletData?.isConnected && walletData?.address) {
              setWallet(walletData)
            } else {
              setWallet(null)
              cookies.delete('kairos_wallet')
            }
          } catch (error) {
            setWallet(null)
            cookies.delete('kairos_wallet')
          }
        } else {
          setWallet(null)
          cookies.delete('kairos_wallet')
        }
      }
    }

    window.addEventListener('storage', handleStorageChange)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
    }
  }, [])

  // Separate effect for MetaMask event listeners
  useEffect(() => {
    if (typeof window === 'undefined' || !window.ethereum) {
      return
    }

    // Listen for MetaMask account changes
    const handleAccountsChanged = (accounts: string[]) => {
      if (accounts.length === 0) {
        // User disconnected all accounts from MetaMask
        console.log('MetaMask: All accounts disconnected')
        setWallet(null)
        localStorage.removeItem('kairos_wallet')
        localStorage.removeItem('kairos_user_profile')
        cookies.delete('kairos_wallet')
        window.location.href = '/login'
      } else {
        // Account changed in MetaMask - update current wallet
        setWallet(prev => {
          if (prev && accounts[0] !== prev.address) {
            console.log('MetaMask: Account changed')
            const updatedWallet = { ...prev, address: accounts[0] }
            localStorage.setItem('kairos_wallet', JSON.stringify(updatedWallet))
            cookies.set('kairos_wallet', JSON.stringify(updatedWallet))
            return updatedWallet
          }
          return prev
        })
      }
    }

    // Listen for MetaMask chain changes
    const handleChainChanged = (chainId: string) => {
      console.log('MetaMask: Chain changed to', chainId)
      setWallet(prev => {
        if (prev) {
          const updatedWallet = { ...prev, chainId }
          localStorage.setItem('kairos_wallet', JSON.stringify(updatedWallet))
          cookies.set('kairos_wallet', JSON.stringify(updatedWallet))
          return updatedWallet
        }
        return prev
      })
    }

    // Listen for MetaMask disconnect
    const handleDisconnect = () => {
      console.log('MetaMask: Disconnected')
      setWallet(null)
      localStorage.removeItem('kairos_wallet')
      localStorage.removeItem('kairos_user_profile')
      cookies.delete('kairos_wallet')
      window.location.href = '/login'
    }

    // Set up MetaMask event listeners
    window.ethereum.on('accountsChanged', handleAccountsChanged)
    window.ethereum.on('chainChanged', handleChainChanged)
    window.ethereum.on('disconnect', handleDisconnect)

    return () => {
      // Clean up MetaMask event listeners
      window.ethereum.removeListener('accountsChanged', handleAccountsChanged)
      window.ethereum.removeListener('chainChanged', handleChainChanged)
      window.ethereum.removeListener('disconnect', handleDisconnect)
    }
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
      
      console.log('User logged in successfully')
    } catch (error) {
      console.error('Error saving wallet data:', error)
    }
  }

  const logout = () => {
    try {
      console.log('Logging out user...')
      
      // Clear state
      setWallet(null)
      
      // Clear localStorage
      localStorage.removeItem('kairos_wallet')
      localStorage.removeItem('kairos_user_profile') // Also clear user profile
      
      // Clear cookie
      cookies.delete('kairos_wallet')
      
      // Force reload to clear any cached state
      window.location.href = '/login'
    } catch (error) {
      console.error('Error during logout:', error)
      // Fallback: force reload to login page
      window.location.href = '/login'
    }
  }

  const updateWallet = (walletData: Partial<WalletInfo>) => {
    if (wallet) {
      const updatedWallet = { ...wallet, ...walletData }
      
      // Ensure we still have required fields
      if (!updatedWallet.address || !updatedWallet.isConnected) {
        logout()
        return
      }
      
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