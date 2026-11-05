<template>
	<view class="nickname-page"><nav-header title="修改昵称" /><view class="nickname-field"><text>昵称</text><input v-model="nickname" aria-label="昵称" placeholder="请输入昵称" maxlength="64" :disabled="loading || saving" /></view><text v-if="failed" class="nickname-tip">加载失败，请返回重试</text><button class="nickname-save" :loading="saving" :disabled="loading || saving || failed" @click="save">保存</button></view>
</template>
<script setup>
	import { ref } from 'vue'
	import { onLoad, onUnload } from '@dcloudio/uni-app'
	import { memberProfile, memberUpdateProfile } from '@/api/member.js'
	const nickname = ref(''), loading = ref(true), saving = ref(false), failed = ref(false)
	let disposed = false, owner = ''
	onLoad(async () => {
		owner = uni.getStorageSync('member_token') || ''
		if (!owner) { uni.reLaunch({ url: '/pages/login/login' }); return }
		try { const res = await memberProfile(); if (!disposed && owner === uni.getStorageSync('member_token')) nickname.value = res.data.nickname || res.data.username || '' }
		catch (error) { if (!disposed) failed.value = true }
		finally { if (!disposed) loading.value = false }
	})
	const save = async () => {
		if (loading.value || saving.value || failed.value || owner !== uni.getStorageSync('member_token')) return
		if (!nickname.value.trim()) { uni.showToast({ title: '昵称不能为空', icon: 'none' }); return }
		saving.value = true
		try {
			const res = await memberUpdateProfile({ nickname: nickname.value.trim() })
			if (disposed || owner !== uni.getStorageSync('member_token')) return
			uni.setStorageSync('member_info', res.data); uni.$emit('member:change', res.data)
			uni.showToast({ title: '昵称已更新', icon: 'success' })
			if (getCurrentPages().length > 1) uni.navigateBack(); else uni.redirectTo({ url: '/pages/profile/settings' })
		} catch (error) { /* 请求层统一提示 */ }
		finally { if (!disposed) saving.value = false }
	}
	onUnload(() => { disposed = true })
</script>
<style scoped>
	.nickname-page { min-height:100vh; max-width:700px; margin:auto; background:#f3f3f3; }
	.nickname-field { display:flex; align-items:center; gap:16px; min-height:50px; padding:0 16px; background:#fff; font-size:14px; }
	.nickname-field input { flex:1; min-width:0; text-align:right; font-size:14px; }
	.nickname-save { margin:30px 16px; height:48px; line-height:48px; border-radius:3px; background:#e43d3d; color:#fff; font-size:15px; }
	.nickname-save[disabled] { background:#eaa5a5; color:#fff; }
	.nickname-save::after { border:0; }
	.nickname-tip { display:block; padding:16px; font-size:12px; color:#999; }
</style>
