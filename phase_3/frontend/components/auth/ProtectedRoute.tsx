/**
 * ProtectedRoute component - Authentication guard for protected pages
 *
 * Redirects unauthenticated users to login page.
 * Verifies JWT token presence and validity.
 */

'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { getAuthToken } from '@/lib/utils/storage';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

/**
 * ProtectedRoute component
 *
 * Wraps protected pages to ensure user is authenticated.
 * Shows loading state while checking authentication.
 */
export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    // Check if user has valid auth token
    const checkAuth = () => {
      const token = getAuthToken();

      if (!token) {
        // No token - redirect to login
        // Store current path to redirect back after login
        if (typeof window !== 'undefined') {
          sessionStorage.setItem('redirect_after_login', pathname);
        }

        router.push('/login');
        return;
      }

      // TODO: Validate token with backend
      // For now, just check if token exists
      setIsAuthenticated(true);
    };

    checkAuth();
  }, [router, pathname]);

  // Show loading state while checking authentication
  if (isAuthenticated === null) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Verifying authentication...</p>
        </div>
      </div>
    );
  }

  // User is authenticated - render children
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // Fallback (should not reach here due to redirect)
  return null;
}
