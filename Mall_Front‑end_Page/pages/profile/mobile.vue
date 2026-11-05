<template>
	<view class="mobile-page"><nav-header title="修改手机号" /><view class="mobile-form"><view class="mobile-field"><text>登录密码</text><input v-model="password" aria-label="登录密码" password placeholder="请输入当前登录密码" maxlength="72" :disabled="saving" /></view><view class="mobile-field"><text>新手机号</text><input v-model="mobile" aria-label="新手机号" type="number" maxlength="11" placeholder="请输入新手机号" :disabled="saving" /></view></view><text class="mobile-tip">通过当前登录密码确认身份。手机号须为11位中国大陆手机号码。</text><button class="mobile-save" :loading="saving" :disabled="saving" @click="save">保存</button></view>
</template>
<script setup>
	import { ref } from 'vue'
	import { onLoad, onHide, onUnload } from '@dcloudio/uni-app'
	import { memberChangeMobile } from '@/api/member.js'
	const password = ref(''), mobile = ref(''), saving = ref(false)
	let owner = '', disposed = false
	onLoad(() => { owner = uni.getStorageSync('member_token') || ''; if (!owner) uni.reLaunch({ url: '/pages/login/login' }) })
	const save = async () => {
		if (saving.value || owner !== uni.getStorageSync('member_token')) return
		if (!password.value) { uni.showToast({ title: '请输入当前登录密码', icon: 'none' }); return }
		if (!/^1[3-9]\d{9}$/.test(mobile.value.trim())) { uni.showToast({ title: '请输入正确的11位手机号码', icon: 'none' }); return }
		saving.value = true
		try {
			const res = await memberChangeMobile({ password: password.value, mobile: mobile.value.trim() })
			if (disposed || owner !== uni.getStorageSync('member_token')) return
			password.value = ''; uni.setStorageSync('member_info', res.data); uni.$emit('member:change', res.data)
			uni.showToast({ title: '手机号已更新', icon: 'success' })
			if (getCurrentPages().length > 1) uni.navigateBack(); else uni.redirectTo({ url: '/pages/profile/settings' })
		} catch (error) { /* 请求层统一提示 */ }
		finally { if (!disposed) { saving.value = false; password.value = '' } }
	}
	onHide(() => { password.value = '' })
	onUnload(() => { disposed = true; password.value = '' })
</script>
<style scoped>
	.mobile-page { min-height:100vh; max-width:700px; margin:auto; background:#f3f3f3; }
	.mobile-form { padding:0 16px; background:#fff; }
	.mobile-field { display:flex; align-items:center; gap:16px; min-height:48px; border-bottom:1px solid #f4f4f4; font-size:14px; }
	.mobile-field:last-child { border:0; }
	.mobile-field text { flex:0 0 82px; }
	.mobile-field input { flex:1; min-width:0; font-size:14px; }
	.mobile-tip { display:block; padding:16px; color:#999; font-size:12px; line-height:20px; }
	.mobile-save { margin:14px 16px; height:48px; line-height:48px; border-radius:3px; background:#e43d3d; color:#fff; font-size:15px; }
	.mobile-save::after { border:0; }
	.mobile-save[disabled] { background:#eaa5a5; color:#fff; }
</style>
