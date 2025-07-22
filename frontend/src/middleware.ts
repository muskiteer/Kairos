import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Public routes that don't require authentication
const publicRoutes = ['/', '/login']

// Protected routes that require authentication
const protectedRoutes = [
  '/dashboard',
  '/manual-trade',
  '/kairos-ai',
  '/vincent',
  '/trade-history',
  '/profile'
]

// Helper function to safely parse JSON
function safeJsonParse(jsonString: string | undefined) {
  if (!jsonString) return null

  try {
    return JSON.parse(jsonString)
  } catch (error) {
    console.error('Error parsing JSON:', error)
    return null
  }
}

// Helper function to validate wallet data
function isValidWalletData(walletData: any): boolean {
  return Boolean(
    walletData &&
    typeof walletData === 'object' &&
    walletData.isConnected === true &&
    walletData.address &&
    typeof walletData.address === 'string' &&
    walletData.address.length > 0 &&
    walletData.chainId &&
    typeof walletData.chainId === 'string'
  )
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Skip middleware for static files and API routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.match(/\.(svg|png|jpg|jpeg|gif|webp|ico|css|js)$/)
  ) {
    return NextResponse.next()
  }

  // Check if the route is public
  const isPublicRoute = publicRoutes.includes(pathname)

  // Check if the route is protected
  const isProtectedRoute = protectedRoutes.some(route =>
    pathname.startsWith(route)
  )

  // Get the wallet token from cookies
  const walletToken = request.cookies.get('kairos_wallet')?.value

  // Parse and validate wallet data
  let isAuthenticated = false
  if (walletToken) {
    const walletData = safeJsonParse(walletToken)
    isAuthenticated = isValidWalletData(walletData)
  }

  // ✅ Allow access to public routes
  if (isPublicRoute) {
    return NextResponse.next()
  }

  // ❌ Block unauthenticated users from protected routes
  if (isProtectedRoute && !isAuthenticated) {
    console.log(`Access denied to ${pathname} - not authenticated`)

    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('from', pathname)

    const response = NextResponse.redirect(loginUrl)
    if (walletToken) {
      response.cookies.delete('kairos_wallet')
    }

    return response
  }

  // 🚫 Prevent access to /login if already authenticated
  if (pathname === '/login' && isAuthenticated) {
    const from = request.nextUrl.searchParams.get('from')
    const redirectPath = from && protectedRoutes.some(route => from.startsWith(route))
      ? from
      : '/dashboard'

    return NextResponse.redirect(new URL(redirectPath, request.url))
  }

  // 🧹 Clean up invalid cookies if any
  const response = NextResponse.next()
  if (walletToken && !isAuthenticated) {
    response.cookies.delete('kairos_wallet')
  }

  return response
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico|css|js)$).*)',
  ],
}
