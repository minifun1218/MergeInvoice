// 用户相关类型定义

/** 用户信息 */
export interface User {
  id: string
  username: string
  nickname: string
  avatar: string
  email: string
  phone: string
  createdAt: string
}

/** 登录请求 */
export interface LoginRequest {
  username: string
  password: string
}

/** 注册请求 */
export interface RegisterRequest {
  username: string
  password: string
  confirmPassword: string
  email?: string
  phone?: string
}

/** 登录响应 */
export interface LoginResponse {
  token: string
  user: User
}

/** OAuth2 登录类型 */
export type OAuthProvider = 'wechat' | 'github' | 'google'
