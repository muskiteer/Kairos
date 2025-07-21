import React, { useState, useEffect, createContext, useContext } from 'react';

// In a real Next.js app, you would get this from process.env.NEXT_PUBLIC_VINCENT_APP_ID
// For this example, replace 'YOUR_APP_ID' with the ID from your Vincent Dashboard.
const VINCENT_APP_ID = 'YOUR_APP_ID'; 

// Mock Vincent SDK for demonstration purposes.
// In your project, you would install and import from '@lit-protocol/vincent-app-sdk'
const mockVincentSdk = {
  getVincentWebAppClient: ({ appId }) => {
    console.log(`Vincent client initialized for App ID: ${appId}`);
    return {
      isLoginUri: () => window.location.search.includes('jwt='),
      decodeVincentLoginJWT: (origin) => {
        const urlParams = new URLSearchParams(window.location.search);
        const jwtStr = urlParams.get('jwt');
        if (!jwtStr) throw new Error('No JWT found in URL');
        
        // In a real scenario, the SDK would perform cryptographic verification.
        // Here, we'll just decode a mock JWT.
        const decodedPayload = {
          pkp: {
            ethAddress: '0x1234...5678',
            publicKey: '0x04abc...'
          },
          app: { id: appId, version: '1' },
          aud: origin,
          exp: Math.floor(Date.now() / 1000) + 3600, // Expires in 1 hour
        };
        console.log('Mock JWT Decoded:', decodedPayload);
        return { decodedJWT: decodedPayload, jwtStr };
      },
      redirectToConsentPage: ({ redirectUri }) => {
        console.log(`Redirecting to Vincent Consent Page...`);
        console.log(`Redirect URI: ${redirectUri}`);
        // This simulates the redirect. A mock JWT is added for the callback.
        const mockJwt = `header.${btoa(JSON.stringify({pkp: {ethAddress: '0x1234...5678'}, aud: new URL(redirectUri).origin}))}.signature`;
        setTimeout(() => {
            window.location.href = `${redirectUri}?jwt=${mockJwt}`;
        }, 1500);
      },
      removeLoginJWTFromURI: () => {
        const url = new URL(window.location.href);
        url.searchParams.delete('jwt');
        window.history.replaceState({}, document.title, url.toString());
        console.log('JWT removed from URL.');
      },
    };
  },
  jwt: {
      isExpired: (jwtStr) => {
          // Mock check for expiration
          return false; 
      }
  }
};


// 1. Authentication Context
// =================================================================================
// It's best practice to manage auth state globally using React Context.

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState({
    jwt: null,
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });
  
  // This should be the actual Vincent SDK in a real app
  const vincentAppClient = mockVincentSdk.getVincentWebAppClient({ appId: VINCENT_APP_ID });

  useEffect(() => {
    // This effect runs once on mount to handle the auth state
    if (vincentAppClient.isLoginUri()) {
      try {
        const { decodedJWT, jwtStr } = vincentAppClient.decodeVincentLoginJWT(window.location.origin);
        
        localStorage.setItem('vincent_jwt', jwtStr);
        setAuth({
          jwt: jwtStr,
          user: decodedJWT.pkp,
          isAuthenticated: true,
          isLoading: false,
        });
        
        vincentAppClient.removeLoginJWTFromURI();
      } catch (error) {
        console.error("Vincent JWT handling failed:", error);
        setAuth({ jwt: null, user: null, isAuthenticated: false, isLoading: false });
      }
    } else {
      const storedJwt = localStorage.getItem('vincent_jwt');
      if (storedJwt && !mockVincentSdk.jwt.isExpired(storedJwt)) {
         const { decodedJWT } = vincentAppClient.decodeVincentLoginJWT(window.location.origin);
         setAuth({
            jwt: storedJwt,
            user: decodedJWT.pkp,
            isAuthenticated: true,
            isLoading: false
         });
      } else {
        setAuth({ jwt: null, user: null, isAuthenticated: false, isLoading: false });
      }
    }
  }, []);

  const login = () => {
    // The redirect URI must be one of the URLs you authorized in the Vincent Dashboard
    const redirectUri = window.location.origin;
    vincentAppClient.redirectToConsentPage({ redirectUri });
  };

  const logout = () => {
    localStorage.removeItem('vincent_jwt');
    setAuth({ jwt: null, user: null, isAuthenticated: false, isLoading: false });
  };

  return (
    <AuthContext.Provider value={{ ...auth, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);


// 2. UI Components
// =================================================================================
// These components consume the authentication context to render the UI.

function Header() {
  const { isAuthenticated, user, login, logout, isLoading } = useAuth();

  return (
    <header className="bg-gray-800 text-white p-4 flex justify-between items-center shadow-md">
      <h1 className="text-xl font-bold">Kairos Trading Agent</h1>
      <div>
        {isLoading ? (
          <div className="text-gray-400">Loading...</div>
        ) : isAuthenticated ? (
          <div className="flex items-center space-x-4">
            <span className="text-sm hidden sm:block">{user.ethAddress}</span>
            <button
              onClick={logout}
              className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        ) : (
          <button
            onClick={login}
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition-colors"
          >
            Connect with Vincent
          </button>
        )}
      </div>
    </header>
  );
}

function Dashboard() {
    const { isAuthenticated, jwt, user } = useAuth();

    if (!isAuthenticated) {
        return (
            <div className="text-center p-10 bg-white rounded-lg shadow-xl">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Welcome to Kairos</h2>
                <p className="text-gray-600 mb-6">Please connect your wallet with Vincent to manage your autonomous trading agent.</p>
                {/* The login button is in the header */}
            </div>
        )
    }

    return (
        <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-2xl">
            <h2 className="text-3xl font-bold text-gray-800 mb-4 border-b pb-2">Agent Dashboard</h2>
            <p className="text-green-600 font-semibold mb-6">Successfully authenticated!</p>
            
            <div className="space-y-4">
                <div>
                    <h3 className="font-semibold text-gray-700">Your Wallet Address:</h3>
                    <p className="text-gray-600 text-sm break-all">{user.ethAddress}</p>
                </div>
                 <div>
                    <h3 className="font-semibold text-gray-700">Your Public Key:</h3>
                    <p className="text-gray-600 text-sm break-all">{user.publicKey}</p>
                </div>
                <div>
                    <h3 className="font-semibold text-gray-700">Your Auth Token (JWT):</h3>
                    <p className="text-gray-500 text-xs break-all bg-gray-100 p-2 rounded-md">{jwt}</p>
                    <p className="text-xs text-gray-400 mt-1">This token should be sent to your backend to authorize actions.</p>
                </div>
            </div>

            <div className="mt-8">
                <button className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-4 rounded-lg transition-colors text-lg">
                    Activate Trading Agent
                </button>
            </div>
        </div>
    )
}


// 3. Main App Component
// =================================================================================
// This is the root of our application.

export default function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-100 font-sans">
        <Header />
        <main className="p-4 sm:p-8 flex items-center justify-center">
          <Dashboard />
        </main>
      </div>
    </AuthProvider>
  );
}
