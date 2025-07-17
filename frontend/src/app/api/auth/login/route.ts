import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { authMethod, address } = body

    if (!authMethod || !address) {
      return NextResponse.json({ success: false, message: 'Missing authentication data' }, { status: 400 })
    }

    const authInfo = {
      isAuthenticated: true,
      address,
      authMethod,
      timestamp: new Date().toISOString()
    }

    const response = NextResponse.json({ success: true })

    // Set a secure, httpOnly cookie
    response.cookies.set('kairos_auth', JSON.stringify(authInfo), {
      httpOnly: true,
      secure: process.env.NODE_ENV !== 'development',
      maxAge: 60 * 60 * 24, // 24 hours
      path: '/',
      sameSite: 'strict',
    })

    return response
  } catch (error) {
    console.error('Login API error:', error)
    return NextResponse.json({ success: false, message: 'Internal server error' }, { status: 500 })
  }
}
