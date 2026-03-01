import { NextRequest, NextResponse } from 'next/server';

/**
 * OAuth Callback Handler
 * 
 * This route handles the OAuth callback from Google and GitHub.
 * It exchanges the authorization code for tokens and redirects to dashboard.
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ provider: string }> }
) {
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get('code');
  const state = searchParams.get('state');
  const error = searchParams.get('error');
  
  const { provider } = await params;
  
  // Check for OAuth error
  if (error) {
    console.error('OAuth error:', error);
    return NextResponse.redirect(
      new URL(`/login?error=${encodeURIComponent('OAuth failed: ' + error)}`, request.url)
    );
  }
  
  // Validate code and state
  if (!code || !state) {
    return NextResponse.redirect(
      new URL('/login?error=' + encodeURIComponent('Invalid OAuth response'), request.url)
    );
  }
  
  // Validate provider
  if (provider !== 'google' && provider !== 'github') {
    return NextResponse.redirect(
      new URL('/login?error=' + encodeURIComponent('Invalid OAuth provider'), request.url)
    );
  }
  
  try {
    // Exchange code for tokens
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(
      `${apiUrl}/api/v1/oauth/${provider}/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}`
    );
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'OAuth callback failed');
    }
    
    const data = await response.json();
    
    // Store tokens in cookies (httpOnly would be better, but this works for now)
    // In production, use httpOnly cookies set by the backend
    const redirectUrl = new URL('/dashboard', request.url);
    
    // Store tokens in URL hash (temporary, will be moved to cookies in production)
    redirectUrl.hash = `access_token=${data.access_token}&refresh_token=${data.refresh_token}`;
    
    return NextResponse.redirect(redirectUrl);
  } catch (error) {
    console.error('OAuth callback error:', error);
    const errorMessage = error instanceof Error ? error.message : 'OAuth failed';
    return NextResponse.redirect(
      new URL(`/login?error=${encodeURIComponent(errorMessage)}`, request.url)
    );
  }
}
