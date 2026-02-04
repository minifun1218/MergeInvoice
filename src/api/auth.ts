// 认证API服务
import type { ApiResponse } from '@/types/invoice'
import type { LoginRequest, RegisterRequest, LoginResponse, User, OAuthProvider } from '@/types/user'

const API_BASE = '/api/v1'

/** 用户登录 */
export async function login(data: LoginRequest): Promise<ApiResponse<LoginResponse>> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return response.json()
}

/** 用户注册 */
export async function register(data: RegisterRequest): Promise<ApiResponse<LoginResponse>> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return response.json()
}

/** 获取当前用户信息 */
export async function getCurrentUser(token: string): Promise<ApiResponse<User>> {
  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return response.json()
}

/** 获取OAuth2授权URL */
export async function getOAuthUrl(provider: OAuthProvider): Promise<ApiResponse<{ url: string }>> {
  const response = await fetch(`${API_BASE}/auth/oauth/${provider}/url`)
  return response.json()
}

/** OAuth2回调处理 */
export async function oauthCallback(
  provider: OAuthProvider,
  code: string,
  state: string,
): Promise<ApiResponse<LoginResponse>> {
  const response = await fetch(`${API_BASE}/auth/oauth/${provider}/callback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, state }),
  })
  return response.json()
}

/** 退出登录 */
export async function logout(token: string): Promise<ApiResponse<null>> {
  const response = await fetch(`${API_BASE}/auth/logout`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  })
  return response.json()
}
