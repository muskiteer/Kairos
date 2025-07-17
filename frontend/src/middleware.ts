import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Define protected routes that require authentication
const protectedRoutes = [
  '/dashboard',
  '/profile',
  '/ai-agent',
  '/autonomous-agent',
  '/manual-trade',
  '/trade-history',
  '/vincent'
]

// Define public routes that don't require authentication
const publicRoutes = [
  '/',
  '/login',
  '/api'
]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  console.log(`🛡️  Middleware: Processing request for ${pathname}`)
  
  // Allow API routes and static files
  if (
    pathname.startsWith('/api') ||
    pathname.startsWith('/_next') ||
    pathname.startsWith('/favicon.ico') ||
    pathname.includes('.')
  ) {
    console.log(`✅ Middleware: Allowing static/API route ${pathname}`)
    return NextResponse.next()
  }

  // Check if current path is protected
  const isProtectedRoute = protectedRoutes.some(route => 
    pathname.startsWith(route)
  )
  
  // Check if current path is public
  const isPublicRoute = publicRoutes.includes(pathname) || pathname === '/'
  
  console.log(`🔍 Middleware: Route ${pathname} - Protected: ${isProtectedRoute}, Public: ${isPublicRoute}`)
  
  // If it's a public route, allow access
  if (isPublicRoute && !isProtectedRoute) {
    console.log(`✅ Middleware: Allowing public route ${pathname}`)
    return NextResponse.next()
  }

  // For protected routes, check authentication
  if (isProtectedRoute) {
    // Check for authentication in cookies or headers
    const authCookie = request.cookies.get('kairos_auth')
    console.log(`🍪 Middleware: Auth cookie present: ${!!authCookie}`)
    
    if (!authCookie) {
      // No authentication found, redirect to login
      console.log(`❌ Middleware: No auth cookie, redirecting to login`)
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('redirect', pathname)
      return NextResponse.redirect(loginUrl)
    }

    try {
      // Validate the auth cookie
      const authData = JSON.parse(authCookie.value)
      console.log(`🔍 Middleware: Validating auth data:`, { isAuthenticated: authData.isAuthenticated, hasAddress: !!authData.address })
      
      // Check if authentication is still valid (24 hours)
      const authTime = new Date(authData.timestamp)
      const now = new Date()
      const hoursDiff = (now.getTime() - authTime.getTime()) / (1000 * 60 * 60)
      
      console.log(`⏰ Middleware: Auth age: ${hoursDiff.toFixed(2)} hours`)
      
      if (hoursDiff > 24 || !authData.isAuthenticated || !authData.address) {
        // Authentication expired or invalid, redirect to login
        console.log(`❌ Middleware: Auth expired or invalid, redirecting to login`)
        const loginUrl = new URL('/login', request.url)
        loginUrl.searchParams.set('redirect', pathname)
        const response = NextResponse.redirect(loginUrl)
        response.cookies.delete('kairos_auth')
        return response
      }
      
      // Authentication is valid, allow access
      console.log(`✅ Middleware: Auth valid, allowing access to ${pathname}`)
      return NextResponse.next()
    } catch (error) {
      // Invalid auth cookie, redirect to login
      console.error(`❌ Middleware: Invalid auth cookie, redirecting to login:`, error)
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('redirect', pathname)
      const response = NextResponse.redirect(loginUrl)
      response.cookies.delete('kairos_auth')
      return response
    }
  }

  // For any other routes, allow access
  console.log(`✅ Middleware: Allowing other route ${pathname}`)
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
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
