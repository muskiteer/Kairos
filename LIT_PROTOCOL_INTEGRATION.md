# Kairos Lit Protocol Integration

## Overview

Kairos has been fully integrated with Lit Protocol to create a completely decentralized trading platform. This integration removes all database dependencies and provides wallet-based authentication, encrypted API key storage, NFT features, and decentralized report generation.

## 🌟 Key Features Implemented

### 1. Wallet Authentication System
- **MetaMask Integration**: Direct wallet connection for user authentication
- **PKP (Programmable Key Pairs)**: Generated for advanced encryption capabilities
- **Session Management**: Wallet-based user sessions without traditional backends

### 2. Encrypted API Key Storage
- **Lit Protocol Encryption**: All API keys encrypted using user's wallet signature
- **IPFS Storage**: Encrypted data stored on IPFS for decentralization
- **Dynamic Access**: API keys retrieved and decrypted only when needed
- **Supported APIs**: Recall API, CoinPanic API, custom trading APIs

### 3. NFT Ecosystem
- **Strategy NFTs**: Trade strategies minted as NFTs for sharing/selling
- **Achievement NFTs**: Milestone achievements in trading performance
- **Governance NFTs**: Voting rights for platform decisions
- **Access NFTs**: Gated access to premium features
- **Consumable NFTs**: One-time use items and boosts

### 4. Decentralized Profile Management
- **IPFS Profile Storage**: User profiles stored on IPFS
- **Wallet-Based Identity**: No traditional user accounts required
- **Consent Management**: Granular permissions using Lit Actions
- **Cross-Chain Support**: Works across multiple blockchain networks

### 5. Trading Session Authorization
- **Signature-Based Auth**: Trading sessions authorized via wallet signatures
- **Time-Bound Access**: Sessions with configurable expiration
- **Multi-Wallet Support**: Support for multiple wallet types
- **Risk Management**: Built-in risk controls via smart contracts

### 6. Decentralized Report Generation
- **Browser Downloads**: Reports generated and downloaded directly in browser
- **IPFS Storage**: Reports stored permanently on IPFS
- **Encrypted Sharing**: Secure sharing via Lit Protocol encryption
- **No Email Dependency**: Eliminated email-based report delivery

## 🛠️ Technical Implementation

### Frontend Components

#### 1. KairosLitProtocolService (`frontend/src/lib/kairos-lit-service.ts`)
```typescript
class KairosLitProtocolService {
  // Core authentication and encryption
  async connectWallet(): Promise<WalletConnection>
  async encryptData(data: any): Promise<EncryptedData>
  async decryptData(encryptedData: EncryptedData): Promise<any>
  
  // API key management
  async storeAPIKey(keyName: string, keyValue: string): Promise<boolean>
  async getAPIKey(keyName: string): Promise<string>
  async listAPIKeys(): Promise<string[]>
  
  // NFT operations
  async mintNFT(type: NFTType, metadata: any): Promise<string>
  async getNFTCollection(address: string): Promise<NFT[]>
  async transferNFT(tokenId: string, toAddress: string): Promise<boolean>
  
  // Profile management
  async saveProfile(profileData: any): Promise<string>
  async loadProfile(address: string): Promise<any>
  async updateConsent(permissions: ConsentData): Promise<boolean>
}
```

#### 2. Profile Interface (`frontend/src/app/profile/page.tsx`)
- **6-Tab Layout**: Connect, Personal, API Keys, NFTs, Trading, Consent
- **Real-time Updates**: Live wallet balance and NFT updates
- **Drag-and-Drop**: File uploads for profile images
- **Interactive NFT Gallery**: View and manage NFT collection

### Backend Services

#### 1. LitProtocolAPIService (`backend/api/lit_protocol_service.py`)
```python
class LitProtocolAPIService:
    async def store_encrypted_api_key(wallet_address: str, api_key_name: str, encrypted_data: dict) -> bool
    async def get_user_api_keys(wallet_address: str) -> List[str]
    async def decrypt_api_key(wallet_address: str, api_key_name: str) -> str
    
class DecentralizedReportGenerator:
    async def generate_and_store_report(wallet_address: str, report_data: dict, report_type: str) -> dict
    async def get_user_reports(wallet_address: str) -> List[dict]
```

#### 2. Dynamic API Manager (`backend/utils/api_manager.py`)
```python
class DynamicAPIManager:
    async def get_user_api_key(user_id: str, api_name: str) -> str
    async def refresh_session_keys() -> None
    def get_cached_key(user_id: str, api_name: str) -> str
```

## 🗂️ File Structure Changes

### New Files Created
```
frontend/src/lib/kairos-lit-service.ts     # Core Lit Protocol service
backend/api/lit_protocol_service.py        # Backend decentralized services
LIT_PROTOCOL_INTEGRATION.md               # This documentation
```

### Files Modified
```
frontend/package.json                      # Added Lit Protocol dependencies
frontend/src/app/profile/page.tsx         # Complete rewrite for decentralization
backend/utils/api_manager.py              # Updated for wallet-based API management
backend/agent/gemini_agent.py             # Updated initialization messaging
backend/api_server.py                     # Added Lit Protocol endpoints
backend/agent/kairos_copilot.py           # Removed database dependencies
backend/agent/autonomous_agent.py         # Removed database dependencies
backend/utils/report_generator.py         # Updated for decentralized reports
```

### Files Removed
```
backend/database/                         # Entire database directory
backend/api/profile.py                    # Old profile API
backend/add_test_profile.py              # Test profile script
```

## 📦 Dependencies Added

### Frontend
```json
{
  "@lit-protocol/lit-node-client": "^7.2.0",
  "@lit-protocol/lit-auth-client": "^7.2.0",
  "@lit-protocol/pkp-ethers": "^7.2.0",
  "@lit-protocol/access-control-conditions": "^7.2.0",
  "@lit-protocol/auth-helpers": "^7.2.0",
  "ethers": "^6.13.1",
  "ipfs-http-client": "^60.0.1"
}
```

### Backend
```python
# No new dependencies required
# Existing FastAPI, Python standard library sufficient
```

## 🔧 Environment Variables Removed

The following environment variables are **no longer needed**:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `DATABASE_URL`
- Email-related variables (for report delivery)

## 🚀 Usage Examples

### 1. Connect Wallet and Store API Key
```typescript
const litService = new KairosLitProtocolService();

// Connect wallet
const wallet = await litService.connectWallet();

// Store encrypted API key
await litService.storeAPIKey('recall_api', 'your-recall-api-key');
```

### 2. Mint Achievement NFT
```typescript
// Mint achievement for successful trade
await litService.mintNFT('achievement', {
  name: 'First Profitable Trade',
  description: 'Achieved first profitable trade on Kairos',
  image: 'https://ipfs.io/ipfs/...',
  attributes: [
    { trait_type: 'Category', value: 'Trading' },
    { trait_type: 'Difficulty', value: 'Beginner' }
  ]
});
```

### 3. Generate Decentralized Report
```python
# Backend report generation
report_result = await report_generator.generate_and_store_report(
    wallet_address="0x123...",
    report_data=trading_session_data,
    report_type="trading_session"
)

# Returns IPFS hash and download URL
```

## 🔒 Security Features

### 1. Access Control Conditions
- Time-based access (sessions expire automatically)
- Wallet signature verification
- Role-based permissions via NFT ownership
- IP-based restrictions (optional)

### 2. Encryption Standards
- AES-256-GCM for data encryption
- ECDSA signatures for authentication
- BLS threshold signatures for PKPs
- IPFS content addressing for integrity

### 3. Privacy Controls
- Granular consent management
- Data minimization principles
- User-controlled data deletion
- Transparent data usage tracking

## 🌐 IPFS Integration

### Storage Strategy
- **Profiles**: User profile data and preferences
- **Reports**: Trading session reports and analytics
- **NFT Metadata**: All NFT metadata and images
- **Encrypted Keys**: Encrypted API key storage

### Content Addressing
- All data addressed by content hash
- Immutable storage ensures data integrity
- Distributed storage prevents single points of failure
- Pin service integration for persistence

## 🔄 Migration from Database

### Data Migration Strategy
1. **User Profiles**: Exported to IPFS with wallet-based access
2. **API Keys**: Re-encrypted with Lit Protocol
3. **Trading History**: Maintained in existing APIs (Recall, etc.)
4. **Session Data**: Moved to local storage with IPFS backup

### Backward Compatibility
- Legacy API endpoints maintained during transition
- Graceful fallbacks for missing decentralized data
- Migration tools for existing users

## 🧪 Testing

### Unit Tests
- Wallet connection and disconnection
- Encryption/decryption cycles
- NFT minting and transfers
- API key storage and retrieval

### Integration Tests
- Full trading session with decentralized auth
- Report generation and IPFS storage
- Cross-chain NFT operations
- Multi-wallet user scenarios

### Performance Tests
- Encryption/decryption speed
- IPFS upload/download times
- Concurrent user sessions
- Large dataset handling

## 📈 Future Enhancements

### 1. Advanced NFT Features
- **Staking**: Stake NFTs for platform rewards
- **Governance**: Vote on platform improvements
- **Marketplace**: Buy/sell strategy NFTs
- **Composability**: Combine NFTs for enhanced features

### 2. Cross-Chain Expansion
- **Multi-Chain NFTs**: Deploy on multiple networks
- **Bridge Integration**: Cross-chain asset movement
- **Universal Profiles**: Single identity across chains

### 3. Enhanced Privacy
- **Zero-Knowledge Proofs**: Private trading verification
- **Anonymous Analytics**: Privacy-preserving insights
- **Selective Disclosure**: Choose what data to share

### 4. AI Integration
- **AI-Powered NFTs**: NFTs that learn and evolve
- **Personalized Strategies**: AI-generated trading strategies
- **Predictive Analytics**: AI-powered market predictions

## 🆘 Troubleshooting

### Common Issues

#### 1. Wallet Connection Failed
```typescript
// Check if MetaMask is installed
if (typeof window.ethereum === 'undefined') {
  console.error('MetaMask not detected');
}

// Verify network compatibility
const chainId = await window.ethereum.request({ method: 'eth_chainId' });
```

#### 2. Encryption/Decryption Errors
```typescript
// Verify Lit Protocol node connectivity
const litNodeClient = new LitNodeClient();
await litNodeClient.connect();
console.log('Lit nodes connected:', litNodeClient.ready);
```

#### 3. IPFS Upload Failures
```typescript
// Check IPFS node connectivity
const ipfs = create({ url: 'https://ipfs.infura.io:5001' });
const version = await ipfs.version();
console.log('IPFS version:', version);
```

### Debug Mode
Set `DEBUG_LIT_PROTOCOL=true` in environment for detailed logging:
```typescript
if (process.env.DEBUG_LIT_PROTOCOL) {
  console.log('Lit Protocol operation:', operation, data);
}
```

## 📞 Support

For issues or questions regarding the Lit Protocol integration:

1. **Documentation**: Check this file and inline code comments
2. **Logs**: Enable debug mode for detailed operation logs
3. **Community**: Lit Protocol Discord and documentation
4. **Code**: Review the implementation in `kairos-lit-service.ts`

---

*This integration represents a complete shift to decentralized architecture, removing traditional database dependencies while maintaining all functionality and adding powerful new features through Lit Protocol and IPFS.*
