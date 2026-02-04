<script setup lang="ts">
import { ref, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { login, register, getOAuthUrl } from '@/api/auth'
import type { OAuthProvider } from '@/types/user'

const userStore = useUserStore()

// 表单数据
const loginForm = ref({
  username: '',
  password: '',
})

const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
  email: '',
})

const loading = ref(false)
const errorMsg = ref('')

// 重置表单
watch(
  () => userStore.showAuthModal,
  (show) => {
    if (!show) {
      loginForm.value = { username: '', password: '' }
      registerForm.value = { username: '', password: '', confirmPassword: '', email: '' }
      errorMsg.value = ''
    }
  },
)

// 登录处理
async function handleLogin() {
  if (!loginForm.value.username || !loginForm.value.password) {
    errorMsg.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const res = await login(loginForm.value)
    if (res.code === 0 && res.data) {
      userStore.setAuth(res.data.token, res.data.user)
      userStore.closeAuthModal()
    } else {
      errorMsg.value = res.message || '登录失败'
    }
  } catch {
    errorMsg.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 注册处理
async function handleRegister() {
  const { username, password, confirmPassword, email } = registerForm.value

  if (!username || !password) {
    errorMsg.value = '请填写完整信息'
    return
  }

  if (password !== confirmPassword) {
    errorMsg.value = '两次密码输入不一致'
    return
  }

  if (password.length < 6) {
    errorMsg.value = '密码长度至少6位'
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const res = await register({ username, password, confirmPassword, email })
    if (res.code === 0 && res.data) {
      userStore.setAuth(res.data.token, res.data.user)
      userStore.closeAuthModal()
    } else {
      errorMsg.value = res.message || '注册失败'
    }
  } catch {
    errorMsg.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// OAuth登录
async function handleOAuthLogin(provider: OAuthProvider) {
  loading.value = true
  errorMsg.value = ''

  try {
    const res = await getOAuthUrl(provider)
    if (res.code === 0 && res.data?.url) {
      // 跳转到授权页面
      window.location.href = res.data.url
    } else {
      errorMsg.value = res.message || '获取授权链接失败'
    }
  } catch {
    errorMsg.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 关闭弹窗
function closeModal() {
  userStore.closeAuthModal()
}

// 阻止冒泡
function stopPropagation(e: Event) {
  e.stopPropagation()
}
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="userStore.showAuthModal"
        class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm"
        @click="closeModal"
      >
        <Transition name="scale">
          <div
            v-if="userStore.showAuthModal"
            class="relative w-full max-w-md mx-4 bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden"
            @click="stopPropagation"
          >
            <!-- 关闭按钮 -->
            <button
              @click="closeModal"
              class="absolute top-4 right-4 p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors z-10"
            >
              <span class="material-symbols-outlined">close</span>
            </button>

            <!-- 头部 -->
            <div class="pt-8 pb-4 px-8 text-center">
              <div class="size-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                <span class="material-symbols-outlined text-primary text-3xl">receipt_long</span>
              </div>
              <h2 class="text-2xl font-bold text-slate-900 dark:text-white">发票智慧管理</h2>
              <p class="mt-2 text-sm text-slate-500">{{ userStore.authModalTab === 'login' ? '登录您的账户' : '创建新账户' }}</p>
            </div>

            <!-- Tab切换 -->
            <div class="flex mx-8 mb-6 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
              <button
                @click="userStore.switchTab('login')"
                :class="[
                  'flex-1 py-2 text-sm font-medium rounded-md transition-all',
                  userStore.authModalTab === 'login'
                    ? 'bg-white dark:bg-slate-700 text-primary shadow-sm'
                    : 'text-slate-500 hover:text-slate-700',
                ]"
              >
                登录
              </button>
              <button
                @click="userStore.switchTab('register')"
                :class="[
                  'flex-1 py-2 text-sm font-medium rounded-md transition-all',
                  userStore.authModalTab === 'register'
                    ? 'bg-white dark:bg-slate-700 text-primary shadow-sm'
                    : 'text-slate-500 hover:text-slate-700',
                ]"
              >
                注册
              </button>
            </div>

            <!-- 错误提示 -->
            <div v-if="errorMsg" class="mx-8 mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm rounded-lg flex items-center gap-2">
              <span class="material-symbols-outlined text-lg">error</span>
              {{ errorMsg }}
            </div>

            <!-- 登录表单 -->
            <div v-if="userStore.authModalTab === 'login'" class="px-8 pb-6">
              <form @submit.prevent="handleLogin" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">用户名</label>
                  <div class="relative">
                    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 material-symbols-outlined text-xl">person</span>
                    <input
                      v-model="loginForm.username"
                      type="text"
                      placeholder="请输入用户名"
                      class="w-full pl-10 pr-4 py-3 bg-slate-100 dark:bg-slate-800 border-none rounded-lg text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">密码</label>
                  <div class="relative">
                    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 material-symbols-outlined text-xl">lock</span>
                    <input
                      v-model="loginForm.password"
                      type="password"
                      placeholder="请输入密码"
                      class="w-full pl-10 pr-4 py-3 bg-slate-100 dark:bg-slate-800 border-none rounded-lg text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                  </div>
                </div>

                <div class="flex justify-between items-center text-sm">
                  <label class="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                    <input type="checkbox" class="rounded border-slate-300" />
                    记住我
                  </label>
                  <a href="#" class="text-primary hover:underline">忘记密码?</a>
                </div>

                <button
                  type="submit"
                  :disabled="loading"
                  class="w-full py-3 bg-primary text-white font-medium rounded-lg hover:bg-primary/90 transition-colors disabled:bg-slate-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <span v-if="loading" class="material-symbols-outlined animate-spin">progress_activity</span>
                  {{ loading ? '登录中...' : '登录' }}
                </button>
              </form>

              <!-- 分隔线 -->
              <div class="flex items-center gap-4 my-6">
                <div class="flex-1 h-px bg-slate-200 dark:bg-slate-700"></div>
                <span class="text-sm text-slate-400">或使用以下方式登录</span>
                <div class="flex-1 h-px bg-slate-200 dark:bg-slate-700"></div>
              </div>

              <!-- 第三方登录 -->
              <div class="flex gap-3">
                <button
                  @click="handleOAuthLogin('wechat')"
                  :disabled="loading"
                  class="flex-1 flex items-center justify-center gap-2 py-3 bg-[#07C160] hover:bg-[#06AD56] text-white rounded-lg transition-colors disabled:opacity-50"
                >
                  <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89h-.006l-.4-.032zm-2.083 3.166c.504 0 .913.415.913.927 0 .513-.409.927-.913.927a.92.92 0 0 1-.914-.927c0-.512.41-.927.914-.927zm4.556 0c.504 0 .913.415.913.927 0 .513-.409.927-.913.927a.92.92 0 0 1-.914-.927c0-.512.41-.927.914-.927z"/>
                  </svg>
                  微信登录
                </button>
              </div>
            </div>

            <!-- 注册表单 -->
            <div v-else class="px-8 pb-6">
              <form @submit.prevent="handleRegister" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">用户名</label>
                  <div class="relative">
                    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 material-symbols-outlined text-xl">person</span>
                    <input
                      v-model="registerForm.username"
                      type="text"
                      placeholder="请输入用户名"
                      class="w-full pl-10 pr-4 py-3 bg-slate-100 dark:bg-slate-800 border-none rounded-lg text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">邮箱 (可选)</label>
                  <div class="relative">
                    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 material-symbols-outlined text-xl">mail</span>
                    <input
                      v-model="registerForm.email"
                      type="email"
                      placeholder="请输入邮箱"
                      class="w-full pl-10 pr-4 py-3 bg-slate-100 dark:bg-slate-800 border-none rounded-lg text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">密码</label>
                  <div class="relative">
                    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 material-symbols-outlined text-xl">lock</span>
                    <input
                      v-model="registerForm.password"
                      type="password"
                      placeholder="请输入密码 (至少6位)"
                      class="w-full pl-10 pr-4 py-3 bg-slate-100 dark:bg-slate-800 border-none rounded-lg text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">确认密码</label>
                  <div class="relative">
                    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 material-symbols-outlined text-xl">lock</span>
                    <input
                      v-model="registerForm.confirmPassword"
                      type="password"
                      placeholder="请再次输入密码"
                      class="w-full pl-10 pr-4 py-3 bg-slate-100 dark:bg-slate-800 border-none rounded-lg text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                  </div>
                </div>

                <div class="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                  <input type="checkbox" class="mt-1 rounded border-slate-300" />
                  <span>我已阅读并同意 <a href="#" class="text-primary hover:underline">服务条款</a> 和 <a href="#" class="text-primary hover:underline">隐私政策</a></span>
                </div>

                <button
                  type="submit"
                  :disabled="loading"
                  class="w-full py-3 bg-primary text-white font-medium rounded-lg hover:bg-primary/90 transition-colors disabled:bg-slate-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <span v-if="loading" class="material-symbols-outlined animate-spin">progress_activity</span>
                  {{ loading ? '注册中...' : '注册' }}
                </button>
              </form>

              <!-- 分隔线 -->
              <div class="flex items-center gap-4 my-6">
                <div class="flex-1 h-px bg-slate-200 dark:bg-slate-700"></div>
                <span class="text-sm text-slate-400">或使用以下方式注册</span>
                <div class="flex-1 h-px bg-slate-200 dark:bg-slate-700"></div>
              </div>

              <!-- 第三方登录 -->
              <div class="flex gap-3">
                <button
                  @click="handleOAuthLogin('wechat')"
                  :disabled="loading"
                  class="flex-1 flex items-center justify-center gap-2 py-3 bg-[#07C160] hover:bg-[#06AD56] text-white rounded-lg transition-colors disabled:opacity-50"
                >
                  <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89h-.006l-.4-.032zm-2.083 3.166c.504 0 .913.415.913.927 0 .513-.409.927-.913.927a.92.92 0 0 1-.914-.927c0-.512.41-.927.914-.927zm4.556 0c.504 0 .913.415.913.927 0 .513-.409.927-.913.927a.92.92 0 0 1-.914-.927c0-.512.41-.927.914-.927z"/>
                  </svg>
                  微信快速注册
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
  transition: all 0.2s ease;
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
