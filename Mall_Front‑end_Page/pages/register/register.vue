<template>
	<view class="register-page">
		<nav-header title="注册账号"></nav-header>

		<view class="register-main">
			<view class="register-title">创建商城账号</view>
			<view class="register-subtitle">只需填写账号和密码，手机号等资料登录后到「我的 → 设置」补充</view>

			<!-- 账号 -->
			<view class="field">
				<image class="field-icon" src="/static/icon-user.svg" mode="aspectFit"></image>
				<input
					v-model="form.username"
					class="field-input"
					type="text"
					placeholder="请输入账号（4-20 位字母/数字）"
					placeholder-class="field-placeholder"
					maxlength="20"
					confirm-type="next"
				/>
			</view>

			<!-- 密码 -->
			<view class="field">
				<image class="field-icon" src="/static/icon-lock.svg" mode="aspectFit"></image>
				<input
					v-model="form.password"
					class="field-input"
					:password="true"
					placeholder="请输入密码（至少 6 位）"
					placeholder-class="field-placeholder"
					maxlength="32"
					confirm-type="next"
				/>
			</view>

			<!-- 确认密码 -->
			<view class="field">
				<image class="field-icon" src="/static/icon-lock.svg" mode="aspectFit"></image>
				<input
					v-model="form.confirmPassword"
					class="field-input"
					:password="true"
					placeholder="请再次输入密码"
					placeholder-class="field-placeholder"
					maxlength="32"
					confirm-type="done"
					@confirm="onRegister"
				/>
			</view>

			<button class="register-submit" :loading="loading" :disabled="loading" @click="onRegister">注册</button>

			<view class="register-login" @click="goLogin">
				<text>已有账号？</text>
				<text class="register-login-link">去登录</text>
			</view>
		</view>

		<view class="register-footer">技术支持: bs-mail</view>
	</view>
</template>

<script setup>
	import { reactive, ref } from 'vue'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { memberRegister } from '@/api/member.js'

	const form = reactive({
		username: '',
		password: '',
		confirmPassword: ''
	})
	const loading = ref(false)

	const USERNAME_RE = /^[A-Za-z0-9_]{4,20}$/

	const goLogin = () => {
		const pages = getCurrentPages()
		if (pages.length > 1) uni.navigateBack()
		else uni.reLaunch({ url: '/pages/login/login' })
	}

	const onRegister = async () => {
		if (loading.value) return

		const username = (form.username || '').trim()
		const password = form.password || ''
		const confirmPassword = form.confirmPassword || ''

		if (!username) {
			uni.showToast({ title: '请输入账号', icon: 'none' })
			return
		}
		if (!USERNAME_RE.test(username)) {
			uni.showToast({ title: '账号需 4-20 位字母、数字或下划线', icon: 'none' })
			return
		}
		if (!password) {
			uni.showToast({ title: '请输入密码', icon: 'none' })
			return
		}
		if (password.length < 6) {
			uni.showToast({ title: '密码至少 6 位', icon: 'none' })
			return
		}
		if (password !== confirmPassword) {
			uni.showToast({ title: '两次输入的密码不一致', icon: 'none' })
			return
		}

		loading.value = true
		try {
			await memberRegister({ username, password })
			// 把账号带到登录页，省得再输一遍
			uni.setStorageSync('register_username', username)
			uni.showToast({ title: '注册成功', icon: 'success' })
			setTimeout(() => {
				goLogin()
			}, 600)
		} catch (e) {
			// 业务错误（如账号已被注册）由 request.js 统一 toast
		} finally {
			loading.value = false
		}
	}
</script>

<style scoped>
	.register-page {
		min-height: 100vh;
		background-color: #ffffff;
		display: flex;
		flex-direction: column;
	}

	.register-main {
		width: 100%;
		max-width: 660px;
		margin: 0 auto;
		padding: 28px 24px 0;
		box-sizing: border-box;
	}

	.register-title {
		text-align: center;
		font-size: 18px;
		font-weight: 600;
		color: #2b3a4a;
	}

	.register-subtitle {
		margin: 10px 0 26px;
		text-align: center;
		font-size: 12px;
		line-height: 18px;
		color: #9aa0a6;
	}

	.field {
		display: flex;
		align-items: center;
		height: 44px;
		padding: 0 12px;
		margin-bottom: 14px;
		border: 1px solid #dcdfe6;
		border-radius: 4px;
		background-color: #ffffff;
	}

	.field-icon {
		width: 18px;
		height: 18px;
		margin-right: 10px;
		flex-shrink: 0;
	}

	.field-input {
		flex: 1;
		height: 42px;
		font-size: 14px;
		color: #333333;
		background-color: transparent;
		border: none;
		outline: none;
	}

	.field-placeholder {
		color: #b2b8c2;
		font-size: 14px;
	}

	.register-submit {
		width: 100%;
		height: 46px;
		line-height: 46px;
		margin-top: 8px;
		padding: 0;
		border: none;
		border-radius: 4px;
		background-color: #d9534f;
		color: #ffffff;
		font-size: 18px;
		letter-spacing: 2px;
	}

	.register-submit::after {
		border: none;
	}

	.register-submit:active {
		background-color: #c9433f;
	}

	.register-login {
		margin-top: 18px;
		text-align: center;
		font-size: 13px;
		color: #9aa0a6;
	}

	.register-login-link {
		margin-left: 4px;
		color: #d9534f;
	}

	.register-footer {
		margin-top: auto;
		padding: 24px 0 28px;
		text-align: center;
		font-size: 12px;
		color: #9aa0a6;
	}
</style>
