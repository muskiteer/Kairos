# Kairos AI Trading Frontend

## Overview

The Kairos AI Trading Frontend is a modern React-based web application that provides an intuitive interface for autonomous cryptocurrency trading powered by AI. Built with Next.js, TypeScript, and Tailwind CSS, it offers both manual trading capabilities and interactive AI assistant features.

## Features

### Dual AI Modes
- **Agent Mode**: Start and monitor autonomous trading sessions
- **Assistant Mode**: Interactive chat with AI for market analysis and insights

### Trading Interface
- **Manual Trading**: Execute trades with real-time validation
- **Portfolio Management**: Live portfolio tracking and analytics
- **Multi-Chain Support**: Trade across Ethereum, Polygon, Solana, and Base
- **Real-Time Data**: Live price feeds and balance updates

### Advanced Analytics
- **Trading Charts**: Interactive TradingView integration
- **Session Monitoring**: Real-time autonomous trading session tracking
- **Performance Metrics**: P&L, success rates, and trading statistics
- **PDF Reports**: Downloadable session reports

### User Experience
- **Responsive Design**: Mobile-first responsive interface
- **Dark/Light Mode**: Theme switching with system preference detection
- **Real-Time Updates**: Live data updates without page refresh
- **Intuitive Navigation**: Sidebar navigation with clear sections

## Architecture

```
frontend/
├── src/
│   ├── app/                 # Next.js 13+ app directory
│   │   ├── dashboard/       # Main dashboard page
│   │   ├── manual-trade/    # Manual trading interface
│   │   ├── ai-agent/        # AI agent and assistant interface
│   │   ├── layout.tsx       # Root layout component
│   │   └── page.tsx         # Home page
│   ├── components/          # Reusable React components
│   │   ├── ui/             # Shadcn UI components
│   │   ├── app-sidebar.tsx  # Main navigation sidebar
│   │   └── theme-provider.tsx  # Theme management
│   ├── lib/                # Utility functions and configurations
│   │   └── utils.ts        # Common utility functions
│   └── styles/             # Global styles and CSS
├── public/                 # Static assets
├── package.json           # Node.js dependencies
├── tailwind.config.js     # Tailwind CSS configuration
├── tsconfig.json          # TypeScript configuration
└── next.config.js         # Next.js configuration
```

## Quick Start

### Prerequisites

- **Node.js 18+**
- **npm or yarn package manager**
- **Backend API** running on `http://localhost:8000`

### Installation

1. **Install Dependencies**
```bash
cd frontend
npm install
# or
yarn install
```

2. **Environment Configuration**
Create a `.env.local` file in the frontend directory:
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development

# Optional: Analytics and monitoring
NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id
```

3. **Start Development Server**
```bash
npm run dev
# or
yarn dev
```

The application will start on `http://localhost:3000`

### Build for Production

```bash
npm run build
npm start
# or
yarn build
yarn start
```

## Components

### Core Pages

#### Dashboard (`app/dashboard/page.tsx`)
- **Portfolio Overview**: Real-time portfolio value and asset allocation
- **Recent Activity**: Latest trades and AI decisions
- **Quick Actions**: Fast access to trading and AI features
- **Performance Charts**: Visual representation of trading performance

#### Manual Trading (`app/manual-trade/page.tsx`)
- **Trade Execution**: Buy/sell interface with real-time validation
- **Token Selection**: Dropdown with supported cryptocurrencies
- **Balance Display**: Current holdings and available amounts
- **Price Charts**: Integrated TradingView charts for technical analysis
- **Trade History**: Recent manual trades and outcomes

#### AI Agent (`app/ai-agent/page.tsx`)
- **Mode Selection**: Toggle between Agent and Assistant modes
- **Chat Interface**: Interactive conversation with AI
- **Session Management**: Start/stop autonomous trading sessions
- **Real-Time Updates**: Live session progress and trade notifications
- **Report Downloads**: Access to PDF session reports

### UI Components

#### Sidebar Navigation (`components/app-sidebar.tsx`)
- **Route Navigation**: Links to all major sections
- **Active State**: Visual indication of current page
- **Responsive Design**: Collapsible on mobile devices
- **Theme Integration**: Consistent with overall design system

#### Theme Provider (`components/theme-provider.tsx`)
- **Dark/Light Mode**: System preference detection and manual toggle
- **Consistent Theming**: Applied across all components
- **Persistent Storage**: Theme preference saved in localStorage

### Utility Libraries

#### Shadcn/UI Components
The application uses Shadcn/UI for consistent, accessible components:
- **Button**: Various styles and sizes for actions
- **Card**: Content containers with consistent styling
- **Dialog**: Modal windows for forms and confirmations
- **Select**: Dropdown menus for options selection
- **Input**: Form inputs with validation styling
- **Badge**: Status indicators and labels
- **Alert**: Success/error message display

## Configuration

### API Integration

The frontend communicates with the backend API for all data operations:

```typescript
// API endpoints used by the frontend
const API_ENDPOINTS = {
  portfolio: '/api/portfolio',
  balance: '/api/balance/{token}',
  price: '/api/price/{token}',
  trade: '/api/trade',
  chat: '/api/chat',
  assistant: '/api/chat/assistant',
  sessionStatus: '/api/autonomous/status/{sessionId}',
  sessionReport: '/api/session/report/{sessionId}'
}
```

### Environment Variables

```env
# Required
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id
NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn
```

### Tailwind CSS Configuration

The application uses a custom Tailwind configuration for consistent theming:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Custom color palette for Kairos branding
        primary: 'hsl(var(--primary))',
        secondary: 'hsl(var(--secondary))',
        // ... additional colors
      }
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

## Development

### Project Structure

```
src/
├── app/                    # Next.js app directory (pages)
│   ├── dashboard/          # Portfolio and overview
│   ├── manual-trade/       # Manual trading interface
│   ├── ai-agent/          # AI chat and autonomous trading
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # Reusable components
│   ├── ui/               # Shadcn UI components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   └── ...
│   ├── app-sidebar.tsx   # Navigation sidebar
│   └── theme-provider.tsx # Theme management
├── lib/                  # Utilities and configurations
│   ├── utils.ts         # Common utility functions
│   └── types.ts         # TypeScript type definitions
└── hooks/               # Custom React hooks
    ├── use-portfolio.ts # Portfolio data management
    └── use-websocket.ts # Real-time updates
```

### State Management

The application uses React's built-in state management:
- **useState**: Component-level state
- **useEffect**: Side effects and API calls
- **Custom Hooks**: Shared state logic and API interactions

### API Communication

All API calls are handled through custom hooks and utility functions:

```typescript
// Example: Portfolio data fetching
const usePortfolio = () => {
  const [portfolio, setPortfolio] = useState(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchPortfolio()
  }, [])
  
  const fetchPortfolio = async () => {
    try {
      const response = await fetch(`${API_URL}/api/portfolio`)
      const data = await response.json()
      setPortfolio(data)
    } catch (error) {
      console.error('Portfolio fetch error:', error)
    } finally {
      setLoading(false)
    }
  }
  
  return { portfolio, loading, refetch: fetchPortfolio }
}
```

### Real-Time Updates

The application implements polling for real-time data updates:
- **Portfolio Balances**: Updated every 10 seconds
- **Price Data**: Updated every 30 seconds
- **Session Status**: Updated every 5 seconds during active sessions

## Styling

### Design System

The application follows a consistent design system:
- **Color Palette**: Primary blues, secondary greens, accent colors
- **Typography**: Inter font family with consistent sizing scale
- **Spacing**: 4px base unit with consistent spacing scale
- **Borders**: Consistent border radius and stroke weights

### Responsive Design

The interface is fully responsive with breakpoints:
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

### Component Styling

Components use Tailwind CSS classes with consistent patterns:
```tsx
// Example component styling
<Card className="border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
  <CardHeader className="pb-3">
    <CardTitle className="text-lg font-semibold">Portfolio</CardTitle>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
</Card>
```

## Testing

### Component Testing

```bash
# Run component tests
npm run test
# or
yarn test

# Run tests in watch mode
npm run test:watch
```

### End-to-End Testing

```bash
# Run E2E tests (if configured)
npm run test:e2e
```

## Deployment

### Vercel Deployment

The application is optimized for Vercel deployment:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to Vercel
vercel --prod
```

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Configuration

For production deployment, ensure environment variables are configured:
```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_ENVIRONMENT=production
```

## Performance

### Optimization Features

- **Static Generation**: Pages pre-generated at build time where possible
- **Image Optimization**: Next.js automatic image optimization
- **Code Splitting**: Automatic bundle splitting for optimal loading
- **Caching**: API responses cached for performance

### Bundle Analysis

```bash
# Analyze bundle size
npm run analyze
```

## Troubleshooting

### Common Issues

1. **API Connection Issues**
   - Verify backend is running on correct port
   - Check CORS configuration in backend
   - Verify API_URL environment variable

2. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check for conflicting CSS classes
   - Verify theme provider is wrapping the application

3. **Build Issues**
   - Clear `.next` directory: `rm -rf .next`
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check TypeScript errors: `npm run type-check`

### Development Tools

- **React Developer Tools**: Browser extension for component debugging
- **Next.js DevTools**: Built-in development features
- **Tailwind CSS IntelliSense**: VS Code extension for class suggestions

## Contributing

1. **Code Style**: Use Prettier and ESLint configurations
2. **Component Structure**: Follow established patterns
3. **TypeScript**: Maintain strict type checking
4. **Testing**: Add tests for new components
5. **Documentation**: Update README for new features

## Browser Support

- **Chrome**: Latest 2 versions
- **Firefox**: Latest 2 versions
- **Safari**: Latest 2 versions
- **Edge**: Latest 2 versions

## License

This project is proprietary software. All rights reserved.