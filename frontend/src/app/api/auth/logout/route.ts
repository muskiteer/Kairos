import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    // Invalidate the cookie by setting its maxAge to a past date
    const response = NextResponse.json({ success: true, message: 'Logged out successfully' })
    response.cookies.set('kairos_auth', '', {
      httpOnly: true,
      secure: process.env.NODE_ENV !== 'development',
      path: '/',
      sameSite: 'strict',
      maxAge: -1, // Expire the cookie immediately
    })
    return response
  } catch (error) {
    console.error('Logout API error:', error)
    return NextResponse.json({ success: false, message: 'Internal server error' }, { status: 500 })
  }
}
