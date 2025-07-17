import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  const cookie = request.cookies.get('kairos_auth')

  if (!cookie) {
    return NextResponse.json({ isAuthenticated: false, user: null }, { status: 401 })
  }

  try {
    const authInfo = JSON.parse(cookie.value)
    // You might want to add more validation here, e.g., check a session token against a database
    if (authInfo.isAuthenticated) {
      return NextResponse.json({ 
        isAuthenticated: true, 
        user: { 
          address: authInfo.address,
          authMethod: authInfo.authMethod
        } 
      }, { status: 200 })
    } else {
      return NextResponse.json({ isAuthenticated: false, user: null }, { status: 401 })
    }
  } catch (error) {
    console.error('Error parsing auth cookie:', error)
    // Clear the invalid cookie
    const response = NextResponse.json({ isAuthenticated: false, user: null }, { status: 401 })
    response.cookies.set('kairos_auth', '', { maxAge: -1, path: '/' })
    return response
  }
}
