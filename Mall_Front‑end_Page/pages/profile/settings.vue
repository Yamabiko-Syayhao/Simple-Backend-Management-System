<template>
	<view class="settings-page">
		<nav-header title="个人信息" />
		<view v-if="loading" class="settings-state">正在加载个人信息…</view>
		<view v-else-if="failed" class="settings-state"><text>个人信息加载失败</text><button @click="load">重新加载</button></view>
		<view v-else class="settings-fields">
			<button class="settings-row settings-avatar-row" :disabled="busy" @click="chooseAvatar"><text>头像</text><view class="settings-avatar-wrap"><image :src="avatar" class="settings-avatar" mode="aspectFill" /><text class="settings-camera">{{ uploading ? '上传中' : '更换' }}</text></view></button>
			<button class="settings-row" :disabled="busy" @click="open('nickname')"><text>昵称</text><text class="settings-value">{{ member.nickname || member.username }}</text><text class="settings-arrow">›</text></button>
			<button class="settings-row" :disabled="busy" @click="openGender"><text>性别</text><text class="settings-value">{{ genders[Number(member.gender)] || '保密' }}</text><text class="settings-arrow">›</text></button>
			<button class="settings-row" :disabled="busy" @click="open('password')"><text>密码设置</text><text class="settings-value">暂未开放</text><text class="settings-arrow">›</text></button>
			<button class="settings-row" :disabled="busy" @click="open('mobile')"><text>手机号</text><text class="settings-value">{{ member.mobile || '未设置' }}</text><text class="settings-arrow">›</text></button>
		</view>
		<text class="settings-tip">头像支持 JPG、PNG、GIF、BMP、WebP，大小不超过 3MB。</text>
		<button class="settings-logout" :disabled="busy || loggingOut" @click="logout">退出当前账户</button>
		<view v-if="genderVisible" class="gender-popup">
			<view class="gender-mask" @click="genderVisible = false" @touchmove.stop.prevent />
			<view class="gender-panel"><view class="gender-toolbar"><button @click="genderVisible = false">取消</button><text>选择性别</text><button class="gender-confirm" :disabled="saving" @click="saveGender">确认</button></view><picker-view class="gender-picker" :value="[genderIndex]" indicator-style="height:44px" @change="genderIndex = $event.detail.value[0]"><picker-view-column><view v-for="(name,index) in genders" :key="index" class="gender-item">{{ name }}</view></picker-view-column></picker-view></view>
		</view>
	</view>
</template>

<script setup>
	import { computed, reactive, ref } from 'vue'
	import { onShow, onUnload } from '@dcloudio/uni-app'
	import { memberProfile, memberUpdateProfile, memberUploadAvatar, memberLogout } from '@/api/member.js'
	import { imageUrl } from '@/api/url.js'
	const member = reactive({ username: '', nickname: '', avatar: '', mobile: '', gender: 0 })
	const loading = ref(false), failed = ref(false), uploading = ref(false), saving = ref(false), loggingOut = ref(false)
	const genderVisible = ref(false), genderIndex = ref(0), genders = ['保密', '男', '女']
	const busy = computed(() => loading.value || uploading.value || saving.value)
	const avatar = computed(() => imageUrl(member.avatar) || '/static/avatar-default.svg')
	let disposed = false, version = 0, owner = ''
	const applyProfile = (data, token) => {
		if (disposed || token !== uni.getStorageSync('member_token')) return false
		Object.assign(member, data)
		uni.setStorageSync('member_info', data)
		uni.$emit('member:change', data)
		return true
	}
	const load = async () => {
		const token = uni.getStorageSync('member_token') || ''
		if (!token) { uni.reLaunch({ url: '/pages/login/login' }); return }
		if (owner !== token) { Object.assign(member, { username: '', nickname: '', avatar: '', mobile: '', gender: 0 }); owner = token }
		const current = ++version
		loading.value = true; failed.value = false
		try { const res = await memberProfile(); if (!disposed && current === version) applyProfile(res.data || {}, token) }
		catch (error) { if (!disposed && current === version && token === uni.getStorageSync('member_token')) failed.value = true }
		finally { if (!disposed && current === version) loading.value = false }
	}
	const open = (page) => { if (!busy.value) uni.navigateTo({ url: '/pages/profile/' + page }) }
	const chooseAvatar = () => {
		if (busy.value) return
		const token = uni.getStorageSync('member_token')
		uni.chooseImage({ count: 1, sizeType: ['original'], sourceType: ['album', 'camera'], success: async (result) => {
			if (disposed || token !== uni.getStorageSync('member_token')) return
			const file = (result.tempFiles || [])[0]
			if (file && file.size > 3 * 1024 * 1024) { uni.showToast({ title: '头像不能超过3MB', icon: 'none' }); return }
			const path = (result.tempFilePaths || [])[0]
			if (!path) return
			uploading.value = true
			try { const res = await memberUploadAvatar(path); if (applyProfile(res.data.profile, token)) uni.showToast({ title: '头像已更新', icon: 'success' }) }
			catch (error) { /* 上传层统一提示 */ }
			finally { if (!disposed) uploading.value = false }
		} })
	}
	const openGender = () => { if (!busy.value) { genderIndex.value = Number(member.gender) || 0; genderVisible.value = true } }
	const saveGender = async () => {
		if (busy.value) return
		const token = uni.getStorageSync('member_token'); saving.value = true
		try { const res = await memberUpdateProfile({ gender: genderIndex.value }); if (applyProfile(res.data, token)) { genderVisible.value = false; uni.showToast({ title: '性别已更新', icon: 'success' }) } }
		catch (error) { /* 请求层统一提示 */ }
		finally { if (!disposed) saving.value = false }
	}
	const logout = async () => {
		if (busy.value || loggingOut.value) return
		const token = uni.getStorageSync('member_token')
		const confirmed = await new Promise((resolve) => uni.showModal({ title: '退出账户', content: '确定退出当前账户吗？', success: (res) => resolve(res.confirm), fail: () => resolve(false) }))
		if (!confirmed || disposed || token !== uni.getStorageSync('member_token')) return
		loggingOut.value = true
		try { await memberLogout() } catch (error) { /* 本地退出仍继续 */ }
		if (disposed || token !== uni.getStorageSync('member_token')) return
		uni.removeStorageSync('member_token'); uni.removeStorageSync('member_info')
		uni.reLaunch({ url: '/pages/login/login' })
	}
	onShow(load)
	onUnload(() => { disposed = true; version += 1 })
</script>

<style scoped>
	.settings-page { min-height:100vh; max-width:700px; margin:0 auto; padding-bottom:env(safe-area-inset-bottom); background:#f3f3f3; }
	.settings-fields { padding:0 16px; background:#fff; }
	.settings-row { display:flex; align-items:center; gap:10px; margin:0; padding:0; min-height:46px; text-align:left; border-radius:0; border-bottom:1px solid #f3f3f3; background:#fff; font-size:14px; color:#333; line-height:22px; }
	.settings-row::after,.settings-logout::after,.gender-toolbar button::after { border:0; }
	.settings-row:last-child { border-bottom:0; }
	.settings-avatar-row { min-height:80px; }
	.settings-avatar-wrap { position:relative; margin:10px 0 10px auto; width:54px; height:54px; border:1px solid #eee; }
	.settings-avatar { display:block; width:52px; height:52px; }
	.settings-camera { position:absolute; bottom:0; left:0; right:0; background:rgba(0,0,0,.35); text-align:center; color:#fff; font-size:10px; line-height:18px; }
	.settings-value { flex:1; min-width:0; text-align:right; color:#999; overflow-wrap:anywhere; }
	.settings-arrow { color:#aaa; font-size:22px; }
	.settings-tip { display:block; padding:12px 16px; color:#999; font-size:11px; line-height:18px; }
	.settings-logout { height:50px; margin:6px 0 0; border-radius:0; background:#fff; color:#444; font-size:15px; line-height:50px; }
	.settings-state { padding:90px 16px; text-align:center; color:#999; font-size:13px; }
	.settings-state button { width:120px; margin-top:20px; font-size:13px; }
	.gender-popup { position:fixed; inset:0; z-index:1000; }
	.gender-mask { position:absolute; inset:0; background:rgba(0,0,0,.6); }
	.gender-panel { position:absolute; bottom:0; left:0; right:0; max-width:700px; margin:auto; padding-bottom:env(safe-area-inset-bottom); background:#fff; border-radius:16px 16px 0 0; overflow:hidden; }
	.gender-toolbar { display:flex; justify-content:space-between; align-items:center; min-height:54px; padding:0 6px; font-size:14px; }
	.gender-toolbar button { margin:0; color:#999; background:transparent; font-size:13px; }
	.gender-toolbar .gender-confirm { color:#4a90e2; }
	.gender-picker { height:244px; width:100%; }
	.gender-item { height:44px; display:flex; align-items:center; justify-content:center; font-size:15px; }
</style>
