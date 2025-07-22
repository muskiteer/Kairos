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

  // If accessing a protected route without valid authentication
  if (isProtectedRoute && !isAuthenticated) {
    console.log(`Access denied to ${pathname} - not authenticated`)
    
    // Clear invalid cookie if it exists
    const response = NextResponse.redirect(new URL('/login', request.url))
    if (walletToken) {
      response.cookies.delete('kairos_wallet')
    }
    
    // Save intended destination
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('from', pathname)
    return NextResponse.redirect(loginUrl)
  }

  // If accessing login page while already authenticated
  if (pathname === '/login' && isAuthenticated) {
    // Check if there's a redirect destination
    const from = request.nextUrl.searchParams.get('from')
    
    // Validate the redirect destination
    const redirectPath = from && protectedRoutes.some(route => from.startsWith(route)) 
      ? from 
      : '/dashboard'
    
    const redirectUrl = new URL(redirectPath, request.url)
    return NextResponse.redirect(redirectUrl)
  }

  // If accessing root while authenticated, redirect to dashboard
  if (pathname === '/' && isAuthenticated) {
    const dashboardUrl = new URL('/dashboard', request.url)
    return NextResponse.redirect(dashboardUrl)
  }

  // If accessing root without authentication, redirect to login
  if (pathname === '/' && !isAuthenticated) {
    const loginUrl = new URL('/login', request.url)
    return NextResponse.redirect(loginUrl)
  }

  // For all other cases, ensure the cookie is properly set or cleared
  const response = NextResponse.next()
  
  // If we have invalid wallet data in cookie, clear it
  if (walletToken && !isAuthenticated) {
    response.cookies.delete('kairos_wallet')
  }

  return response
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (files with extensions)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico|css|js)$).*)',
  ],
}