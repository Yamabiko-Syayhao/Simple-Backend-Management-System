<template>
	<view class="login-page">
		<view class="login-main">
			<!-- 头像 -->
			<view class="avatar-wrap">
				<image class="avatar" src="/static/avatar-default.svg" mode="aspectFit"></image>
			</view>

			<!-- 标题 -->
			<view class="login-title">bs-mail-vue</view>

			<!-- 账号 -->
			<view class="field">
				<image class="field-icon" src="/static/icon-user.svg" mode="aspectFit"></image>
				<input
					v-model="form.username"
					class="field-input"
					type="text"
					placeholder="请输入测试账号 user123"
					placeholder-class="field-placeholder"
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
					placeholder="请输入测试密码 user123"
					placeholder-class="field-placeholder"
					confirm-type="done"
					@confirm="onLogin"
				/>
			</view>

			<!-- 注册 / 忘记密码 -->
			<view class="login-links">
				<text class="login-link" @click="onRegister">免费注册</text>
				<text class="login-link" @click="onForget">忘记密码</text>
			</view>

			<!-- 登录按钮 -->
			<button class="login-submit" :loading="loading" :disabled="loading" @click="onLogin">登录</button>
		</view>

		<view class="login-footer">技术支持: bs-mail</view>
	</view>
</template>

<script setup>
	import { ref } from 'vue'
	import { onShow } from '@dcloudio/uni-app'
	import { memberLogin } from '@/api/member.js'

	const form = ref({
		username: '',
		password: ''
	})
	const loading = ref(false)

	// 从注册页返回时自动带上刚注册的账号
	onShow(() => {
		const registered = uni.getStorageSync('register_username')
		if (registered) {
			form.value.username = registered
			form.value.password = ''
			uni.removeStorageSync('register_username')
		}
	})

	const onLogin = async () => {
		if (loading.value) return
		const username = (form.value.username || '').trim()
		const password = form.value.password || ''

		if (!username) {
			uni.showToast({ title: '请输入账号', icon: 'none' })
			return
		}
		if (!password) {
			uni.showToast({ title: '请输入密码', icon: 'none' })
			return
		}

		loading.value = true
		try {
			const res = await memberLogin({ username, password })
			uni.setStorageSync('member_token', res.data.token)
			uni.setStorageSync('member_info', res.data)
			uni.showToast({ title: '登录成功', icon: 'success' })
			setTimeout(() => {
				uni.reLaunch({ url: '/pages/index/index' })
			}, 300)
		} catch (e) {
			// 错误提示已在 request.js 统一处理
		} finally {
			loading.value = false
		}
	}

	const onRegister = () => {
		uni.navigateTo({ url: '/pages/register/register' })
	}

	const onForget = () => {
		uni.showToast({ title: '请联系客服重置密码', icon: 'none' })
	}
</script>

<style scoped>
	.login-page {
		min-height: 100vh;
		background-color: #ffffff;
		display: flex;
		flex-direction: column;
	}

	.login-main {
		width: 100%;
		max-width: 660px;
		margin: 0 auto;
		padding: 40px 24px 0;
		box-sizing: border-box;
	}

	.avatar-wrap {
		display: flex;
		justify-content: center;
	}

	.avatar {
		width: 72px;
		height: 72px;
		display: block;
	}

	.login-title {
		margin-top: 12px;
		margin-bottom: 26px;
		text-align: center;
		font-size: 18px;
		font-weight: 600;
		color: #2b3a4a;
		letter-spacing: 0.5px;
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

	.login-links {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin: 6px 0 18px;
	}

	.login-link {
		font-size: 14px;
		color: #2b3a4a;
	}

	.login-submit {
		width: 100%;
		height: 46px;
		line-height: 46px;
		padding: 0;
		border: none;
		border-radius: 4px;
		background-color: #d9534f;
		color: #ffffff;
		font-size: 18px;
		letter-spacing: 2px;
	}

	.login-submit::after {
		border: none;
	}

	.login-submit:active {
		background-color: #c9433f;
	}

	.login-footer {
		margin-top: auto;
		padding: 24px 0 28px;
		text-align: center;
		font-size: 12px;
		color: #9aa0a6;
	}
</style>
