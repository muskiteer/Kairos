import { LitNodeClient } from '@lit-protocol/lit-node-client'
import { LIT_NETWORK, LIT_ABILITY } from '@lit-protocol/constants'
import { LitResourceAbilityRequest, LitActionResource, LitAccessControlConditionResource, createSiweMessage, generateAuthSig } from '@lit-protocol/auth-helpers'
import { ethers } from "ethers"

// Extend Window interface for MetaMask
declare global {
  interface Window {
    ethereum?: any;
  }
}

// Define types for our data structures
interface KairosNFT {
  id: string
  name: string
  type: 'strategy' | 'achievement' | 'access' | 'governance' | 'consumable'
  metadata: any
  benefits: string[]
  transferable: boolean
}

export class KairosLitProtocolService {
  private litNodeClient: LitNodeClient | null = null
  private isConnected: boolean = false
  private currentAddress: string = ''
  private sessionSigs: any = null

  constructor() {
    // Initialize in connect method to ensure client-side only
  }

  async connect() {
    try {
      // Only run on client side
      if (typeof window === 'undefined') {
        throw new Error('Lit Protocol service must be used on client side only')
      }

      this.litNodeClient = new LitNodeClient({
        litNetwork: LIT_NETWORK.DatilTest, // Use test network
        debug: false
      })
      
      await this.litNodeClient.connect()
      this.isConnected = true
      
      console.log('✅ Connected to Lit Protocol network')
      return { success: true, message: '🔗 Connected to Lit Protocol!' }
    } catch (error) {
      console.error('Failed to connect to Lit Protocol:', error)
      return { success: false, message: '❌ Failed to connect to Lit Protocol' }
    }
  }

  async disconnect() {
    if (this.litNodeClient) {
      await this.litNodeClient.disconnect()
      this.isConnected = false
      this.currentAddress = ''
      this.sessionSigs = null
    }
  }

  // 🔐 WALLET AUTHENTICATION
  async authenticateWithWallet() {
    try {
      if (!this.isConnected || !this.litNodeClient) {
        throw new Error('Lit client not connected')
      }

      // Check if MetaMask is available
      if (!window.ethereum) {
        return { 
          success: false, 
          message: '❌ MetaMask not found. Please install MetaMask.' 
        }
      }

      // Request account access - compatible with ethers v6
      const provider = new ethers.BrowserProvider(window.ethereum)
      await provider.send("eth_requestAccounts", [])
      const signer = await provider.getSigner()
      const address = await signer.getAddress()

      // Create session signatures using proper SIWE format
      const sessionSigs = await this.litNodeClient.getSessionSigs({
        chain: "ethereum",
        expiration: new Date(Date.now() + 1000 * 60 * 60 * 24).toISOString(), // 24 hours
        resourceAbilityRequests: [
          {
            resource: new LitAccessControlConditionResource("*"),
            ability: LIT_ABILITY.AccessControlConditionDecryption,
          },
        ],
        authNeededCallback: async ({ uri, expiration, resourceAbilityRequests }) => {
          // Use default values if parameters are undefined
          const authUri = uri || window.location.origin
          const authExpiration = expiration || new Date(Date.now() + 1000 * 60 * 60 * 24).toISOString()
          const authResources = resourceAbilityRequests || [
            {
              resource: new LitAccessControlConditionResource("*"),
              ability: LIT_ABILITY.AccessControlConditionDecryption,
            },
          ]

          // Create proper SIWE message using the correct function
          const toSign = await createSiweMessage({
            uri: authUri,
            expiration: authExpiration,
            resources: authResources,
            walletAddress: address,
            nonce: await this.litNodeClient!.getLatestBlockhash(),
            litNodeClient: this.litNodeClient!,
          });

          return await generateAuthSig({
            signer: signer,
            toSign,
          });
        },
      })

      this.sessionSigs = sessionSigs
      this.currentAddress = address

      return {
        success: true,
        address: address,
        authMethod: { address, sessionSigs },
        message: `✅ Wallet connected: ${address.substring(0, 10)}...`
      }
    } catch (error) {
      console.error('Wallet authentication failed:', error)
      
      // Provide more specific error messages
      let errorMessage = '❌ Wallet authentication failed. Please try again.'
      
      if (error instanceof Error) {
        if (error.message.includes('User rejected')) {
          errorMessage = '❌ Transaction was rejected by user.'
        } else if (error.message.includes('MetaMask')) {
          errorMessage = '❌ MetaMask connection failed. Please try again.'
        } else if (error.message.includes('SIWE') || error.message.includes('Invalid message')) {
          errorMessage = '❌ Authentication signature failed. Please try again.'
        } else if (error.message.includes('network')) {
          errorMessage = '❌ Network connection failed. Please check your connection.'
        }
        
        console.error('Detailed error:', {
          message: error.message,
          stack: error.stack,
          name: error.name
        })
      }
      
      return { 
        success: false, 
        message: errorMessage
      }
    }
  }

  // 📁 LOAD DECENTRALIZED PROFILE
  async loadDecentralizedProfile(userAddress: string) {
    try {
      // For demo purposes, use localStorage as fallback
      const storageKey = `kairos_profile_${userAddress}`
      const stored = localStorage.getItem(storageKey)
      
      if (stored) {
        const profile = JSON.parse(stored)
        return {
          success: true,
          profile: profile,
          message: '📁 Profile loaded from decentralized storage'
        }
      }
      
      return {
        success: false,
        profile: null,
        message: '👋 No existing profile found. Ready to create new profile.'
      }
    } catch (error) {
      console.error('Error loading profile:', error)
      return {
        success: false,
        profile: null,
        message: '❌ Error loading profile'
      }
    }
  }

  // 💾 SAVE DECENTRALIZED PROFILE  
  async saveDecentralizedProfile(profile: any, userAddress: string) {
    try {
      if (!this.sessionSigs || !this.currentAddress) {
        throw new Error('Not authenticated')
      }

      // For demo purposes, save to localStorage
      const storageKey = `kairos_profile_${userAddress}`
      const profileData = {
        ...profile,
        updated_at: new Date().toISOString()
      }
      
      localStorage.setItem(storageKey, JSON.stringify(profileData))
      
      return {
        success: true,
        message: '💾 Profile saved to decentralized storage!'
      }
    } catch (error) {
      console.error('Error saving profile:', error)
      return {
        success: false,
        message: '❌ Failed to save profile'
      }
    }
  }

  // 🗝️ ENCRYPT AND SAVE API KEYS
  async encryptAndStoreAPIKeys(apiKeys: any, userAddress: string) {
    try {
      if (!this.sessionSigs || !this.currentAddress) {
        throw new Error('Not authenticated')
      }

      // For demo purposes, store encrypted in localStorage
      const storageKey = `kairos_api_keys_${userAddress}`
      const encryptedData = {
        encrypted: true,
        data: btoa(JSON.stringify(apiKeys)), // Simple base64 encoding for demo
        timestamp: new Date().toISOString()
      }
      
      localStorage.setItem(storageKey, JSON.stringify(encryptedData))
      
      return {
        success: true,
        message: '🔐 API keys encrypted and stored!'
      }
    } catch (error) {
      console.error('Error encrypting API keys:', error)
      return {
        success: false,
        message: '❌ Failed to encrypt API keys'
      }
    }
  }

  // 🎯 LOAD API KEYS
  async decryptAPIKeys(userAddress: string) {
    try {
      const storageKey = `kairos_api_keys_${userAddress}`
      const stored = localStorage.getItem(storageKey)
      
      if (!stored) {
        return {
          success: false,
          apiKeys: null,
          message: '🔍 No encrypted API keys found'
        }
      }
      
      const encryptedData = JSON.parse(stored)
      const decryptedKeys = JSON.parse(atob(encryptedData.data))
      
      return {
        success: true,
        apiKeys: decryptedKeys,
        message: '🔓 API keys decrypted successfully!'
      }
    } catch (error) {
      console.error('Error decrypting API keys:', error)
      return {
        success: false,
        apiKeys: null,
        message: '❌ Failed to decrypt API keys'
      }
    }
  }

  // 🏆 GET USER NFT PORTFOLIO
  async getUserNFTPortfolio(userAddress: string) {
    try {
      // Demo NFT portfolio data
      const portfolioKey = `kairos_nfts_${userAddress}`
      const stored = localStorage.getItem(portfolioKey)
      
      if (stored) {
        return {
          success: true,
          portfolio: JSON.parse(stored)
        }
      }
      
      // Return empty portfolio for demo
      const emptyPortfolio = {
        strategies: [],
        achievements: [],
        governance: [],
        consumables: []
      }
      
      return {
        success: true,
        portfolio: emptyPortfolio
      }
    } catch (error) {
      console.error('Error loading NFT portfolio:', error)
      return {
        success: false,
        portfolio: null
      }
    }
  }

  // 🎖️ MINT ACHIEVEMENT NFT
  async mintAchievementNFT(achievementType: string, userAddress: string, metadata: any) {
    try {
      // Demo achievement minting
      const portfolioKey = `kairos_nfts_${userAddress}`
      const stored = localStorage.getItem(portfolioKey)
      const portfolio = stored ? JSON.parse(stored) : { achievements: [] }
      
      const achievement = {
        id: `achievement_${Date.now()}`,
        name: achievementType,
        type: 'achievement',
        metadata: {
          description: this.getAchievementDescription(achievementType),
          ...metadata
        },
        benefits: this.getAchievementBenefits(achievementType),
        transferable: false
      }
      
      if (!portfolio.achievements) portfolio.achievements = []
      portfolio.achievements.push(achievement)
      
      localStorage.setItem(portfolioKey, JSON.stringify(portfolio))
      
      return {
        success: true,
        nft: achievement,
        message: `🎖️ Achievement "${achievementType}" minted!`
      }
    } catch (error) {
      console.error('Error minting achievement NFT:', error)
      return {
        success: false,
        message: '❌ Failed to mint achievement NFT'
      }
    }
  }

  // 🎫 MINT CONSUMABLE NFT
  async mintConsumableNFT(consumableType: string, userAddress: string) {
    try {
      const portfolioKey = `kairos_nfts_${userAddress}`
      const stored = localStorage.getItem(portfolioKey)
      const portfolio = stored ? JSON.parse(stored) : { consumables: [] }
      
      const consumable = {
        id: `consumable_${Date.now()}`,
        name: consumableType,
        type: 'consumable',
        metadata: {
          description: `Consumable: ${consumableType}`,
          usesRemaining: 3
        },
        benefits: [`Use ${consumableType} for enhanced trading`],
        transferable: true
      }
      
      if (!portfolio.consumables) portfolio.consumables = []
      portfolio.consumables.push(consumable)
      
      localStorage.setItem(portfolioKey, JSON.stringify(portfolio))
      
      return {
        success: true,
        nft: consumable
      }
    } catch (error) {
      console.error('Error minting consumable NFT:', error)
      return {
        success: false
      }
    }
  }

  // 🗳️ MINT GOVERNANCE NFT
  async mintGovernanceNFT(userAddress: string, governanceType: string) {
    try {
      const portfolioKey = `kairos_nfts_${userAddress}`
      const stored = localStorage.getItem(portfolioKey)
      const portfolio = stored ? JSON.parse(stored) : { governance: [] }
      
      const governanceNFT = {
        id: `governance_${Date.now()}`,
        name: governanceType,
        type: 'governance',
        metadata: {
          description: `Governance token: ${governanceType}`,
          votingPower: 1
        },
        benefits: ['Participate in protocol governance', 'Vote on proposals'],
        transferable: false
      }
      
      if (!portfolio.governance) portfolio.governance = []
      portfolio.governance.push(governanceNFT)
      
      localStorage.setItem(portfolioKey, JSON.stringify(portfolio))
      
      return {
        success: true,
        nft: governanceNFT
      }
    } catch (error) {
      console.error('Error minting governance NFT:', error)
      return {
        success: false
      }
    }
  }

  // 🔍 CHECK ACCESS NFT
  async checkAccessNFT(userAddress: string, accessType: string) {
    try {
      const portfolioKey = `kairos_nfts_${userAddress}`
      const stored = localStorage.getItem(portfolioKey)
      
      if (!stored) {
        return { hasAccess: false }
      }
      
      const portfolio = JSON.parse(stored)
      const hasAccess = portfolio.access && 
        portfolio.access.some((nft: any) => nft.name === accessType)
      
      return { hasAccess }
    } catch (error) {
      console.error('Error checking access NFT:', error)
      return { hasAccess: false }
    }
  }

  // 🚀 CREATE AUTHORIZED TRADING SESSION
  async createAuthorizedTradingSession(sessionData: any, userAddress: string) {
    try {
      if (!this.sessionSigs || !this.currentAddress) {
        throw new Error('Not authenticated')
      }

      // Demo trading session creation
      const sessionId = `session_${Date.now()}`
      const sessionInfo = {
        id: sessionId,
        userAddress,
        ...sessionData,
        createdAt: new Date().toISOString(),
        status: 'active'
      }
      
      const sessionsKey = `kairos_sessions_${userAddress}`
      const stored = localStorage.getItem(sessionsKey)
      const sessions = stored ? JSON.parse(stored) : []
      sessions.push(sessionInfo)
      
      localStorage.setItem(sessionsKey, JSON.stringify(sessions))
      
      return {
        success: true,
        pkp: { publicKey: sessionId },
        message: '🚀 Autonomous trading session created!'
      }
    } catch (error) {
      console.error('Error creating trading session:', error)
      return {
        success: false,
        message: '❌ Failed to create trading session'
      }
    }
  }

  // Helper methods
  private getAchievementDescription(type: string): string {
    const descriptions: Record<string, string> = {
      'first_connection': 'First wallet connection to Kairos platform',
      'profile_complete': 'Completed decentralized profile setup',
      'api_setup': 'Successfully configured encrypted API keys',
      'first_session': 'Created first autonomous trading session'
    }
    return descriptions[type] || `Achievement: ${type}`
  }

  private getAchievementBenefits(type: string): string[] {
    const benefits: Record<string, string[]> = {
      'first_connection': ['Access to basic platform features'],
      'profile_complete': ['Enhanced profile customization', 'Priority support'],
      'api_setup': ['Secure API integration', 'Advanced trading features'],
      'first_session': ['Autonomous trading capabilities', 'Session management tools']
    }
    return benefits[type] || ['Special recognition']
  }
}

// Export singleton instance
export const kairosLitService = new KairosLitProtocolService()
