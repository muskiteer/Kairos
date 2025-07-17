"use client"

import { useState, useEffect, createContext, useContext, ReactNode } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { kairosLitService } from '@/lib/kairos-lit-service'

interface AuthContextType {
  isAuthenticated: boolean;
  userAddress: string | null;
  authMethod: any;
  isLoading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userAddress, setUserAddress] = useState<string | null>(null);
  const [authMethod, setAuthMethod] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // On initial load, check the authentication status from the server
    checkAuth().then(isAuth => {
      if (!isAuth && pathname !== '/login') {
        // This logic might be redundant if middleware is working perfectly,
        // but it's a good fallback.
        router.push('/login');
      }
    });
  }, []);

  const checkAuth = async (): Promise<boolean> => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/auth/me');
      if (response.ok) {
        const { isAuthenticated: serverIsAuthenticated, user } = await response.json();
        if (serverIsAuthenticated) {
          setIsAuthenticated(true);
          setUserAddress(user.address);
          setAuthMethod(user.authMethod);
          return true;
        }
      }
      // If response is not ok or not authenticated, clear client state
      setIsAuthenticated(false);
      setUserAddress(null);
      setAuthMethod(null);
      return false;
    } catch (error) {
      console.error('Auth check failed:', error);
      setIsAuthenticated(false);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const login = async () => {
    setIsLoading(true);
    try {
      await kairosLitService.connect();
      const authData = await kairosLitService.authenticateWithWallet();
      
      console.log('🔐 Auth context: Wallet authentication successful:', authData);

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          address: authData.address,
          authMethod: authData.authMethod,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to set authentication cookie');
      }

      const result = await response.json();
      if (result.success) {
        console.log('✅ Login API call successful, cookie set.');
        // After successful login, update the auth state
        await checkAuth();
        // Redirect to the page the user was trying to access, or dashboard
        const redirectUrl = new URLSearchParams(window.location.search).get('redirect') || '/dashboard';
        router.push(redirectUrl);
      } else {
        throw new Error('Login API call failed');
      }
    } catch (error) {
      console.error('Login failed:', error);
      setIsAuthenticated(false);
      setUserAddress(null);
      setAuthMethod(null);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/auth/logout', { method: 'POST' });
      if (!response.ok) {
        throw new Error('Logout failed');
      }
      
      console.log('✅ Logout successful, cookie cleared.');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear client-side state regardless of API call success
      setIsAuthenticated(false);
      setUserAddress(null);
      setAuthMethod(null);
      setIsLoading(false);
      router.push('/login');
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, userAddress, authMethod, isLoading, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Auth guard component for protecting routes
export function AuthGuard({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // Redirect to login with return URL
      router.push(`/login?redirect=${pathname}`)
    }
  }, [isAuthenticated, isLoading, router, pathname])

  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  // Show nothing if not authenticated (redirect will happen)
  if (!isAuthenticated) {
    return null
  }

  // Show children if authenticated
  return <>{children}</>
}
