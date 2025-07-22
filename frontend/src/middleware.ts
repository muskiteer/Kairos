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

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // Check if the route is public
  const isPublicRoute = publicRoutes.includes(pathname)
  
  // Check if the route is protected
  const isProtectedRoute = protectedRoutes.some(route => 
    pathname.startsWith(route)
  ) || (pathname.startsWith('/_next') === false && !pathname.match(/\.(svg|png|jpg|jpeg|gif|webp)$/))

  // Get the wallet token from cookies
  const walletToken = request.cookies.get('kairos_wallet')?.value
  
  // Parse wallet data if available
  let isAuthenticated = false
  if (walletToken) {
    try {
      const walletData = safeJsonParse(walletToken)
      isAuthenticated = Boolean(walletData?.isConnected && walletData?.address)
    } catch (error) {
      // Invalid wallet data
      isAuthenticated = false
    }
  }

  // If accessing a protected route without authentication
  if (isProtectedRoute && !isAuthenticated && !isPublicRoute) {
    // Redirect to login page
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('from', pathname) // Save intended destination
    return NextResponse.redirect(loginUrl)
  }

  // If accessing login page while already authenticated
  if (pathname === '/login' && isAuthenticated) {
    // Check if there's a redirect destination
    const from = request.nextUrl.searchParams.get('from')
    const redirectUrl = new URL(from || '/dashboard', request.url)
    return NextResponse.redirect(redirectUrl)
  }

  // If accessing root while authenticated, redirect to dashboard
  if (pathname === '/' && isAuthenticated) {
    const dashboardUrl = new URL('/dashboard', request.url)
    return NextResponse.redirect(dashboardUrl)
  }

  // Allow the request to continue
  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (public folder)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}