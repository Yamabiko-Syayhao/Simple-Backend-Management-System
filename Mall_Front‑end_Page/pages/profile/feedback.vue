<template>
	<view class="member-feedback-page">
		<nav-header title="意见反馈" />
		<view v-if="!loggedIn" class="member-feedback-state"><text>请登录后提交意见反馈</text><button class="member-feedback-retry" @click="goLogin">去登录</button></view>
		<view v-else-if="submitted" class="member-feedback-success"><text class="member-feedback-success-mark">✓</text><text>反馈已提交</text><text class="member-feedback-success-note">感谢你的建议，我们会认真查看。</text><button class="member-feedback-save" @click="back">返回服务中心</button></view>
		<view v-else-if="loading" class="member-feedback-state">正在加载反馈类型…</view>
		<view v-else-if="failed || !types.length" class="member-feedback-state"><text>反馈类型暂时无法加载</text><button class="member-feedback-retry" @click="loadOptions">重新加载</button></view>
		<view v-else class="member-feedback-form">
			<picker :range="types" :value="typeIndex" :disabled="saving" @change="typeIndex = Number($event.detail.value)"><view class="member-feedback-field" role="button" aria-label="选择反馈类型"><text>反馈类型</text><view class="member-feedback-picker-value"><text>{{ types[typeIndex] }}</text><text class="member-feedback-arrow">›</text></view></view></picker>
			<view class="member-feedback-content-field"><text class="member-feedback-label">反馈内容</text><textarea v-model="content" class="member-feedback-content" maxlength="2000" placeholder="请详细描述你的问题或建议" :disabled="saving" /><text class="member-feedback-counter">{{ content.length }}/2000</text></view>
			<view class="member-feedback-field"><text>联系手机号</text><input v-model="mobile" class="member-feedback-mobile" type="number" maxlength="11" placeholder="选填，便于联系你" :disabled="saving" /></view>
			<view class="member-feedback-actions"><button class="member-feedback-save" :loading="saving" :disabled="saving" @click="submit">提交反馈</button></view>
		</view>
	</view>
</template>

<script setup>
	import { ref } from 'vue'
	import { onShow, onUnload } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { feedbackContact, feedbackMySubmit } from '@/api/feedback.js'
	const loggedIn = ref(false), loading = ref(false), failed = ref(false), saving = ref(false), submitted = ref(false)
	const types = ref([]), typeIndex = ref(0), content = ref(''), mobile = ref('')
	let disposed = false, version = 0, ownerToken = ''
	const goLogin = () => uni.navigateTo({ url: '/pages/login/login' })
	const back = () => { if (getCurrentPages().length > 1) uni.navigateBack(); else uni.redirectTo({ url: '/pages/profile/service' }) }
	const loadOptions = async () => {
		if (disposed || loading.value) return
		const requestId = ++version
		loading.value = true; failed.value = false
		try {
			const res = await feedbackContact()
			if (disposed || requestId !== version) return
			types.value = Array.isArray(res.data && res.data.feedback_types) ? res.data.feedback_types.filter((value) => typeof value === 'string' && value) : []
			typeIndex.value = 0
		} catch (error) { if (!disposed && requestId === version) failed.value = true }
		finally { if (!disposed && requestId === version) loading.value = false }
	}
	const submit = async () => {
		const token = uni.getStorageSync('member_token') || ''
		if (disposed || saving.value || submitted.value) return
		if (!token || token !== ownerToken) { syncSession(); return }
		const text = content.value.trim(), phone = mobile.value.trim(), type = types.value[typeIndex.value]
		let message = ''
		if (!type) message = '请选择反馈类型'
		else if (!text) message = '请填写反馈内容'
		else if (text.length > 2000) message = '反馈内容不能超过2000字'
		else if (phone && !/^1[3-9]\d{9}$/.test(phone)) message = '请输入正确的11位手机号码'
		if (message) { uni.showToast({ title: message, icon: 'none' }); return }
		saving.value = true
		try {
			await feedbackMySubmit({ feedback_type: type, content: text, ...(phone ? { mobile: phone } : {}) })
			if (disposed || token !== uni.getStorageSync('member_token')) return
			submitted.value = true; content.value = ''; mobile.value = ''; uni.$emit('feedback:change')
		} catch (error) { /* 请求层统一提示，保留未提交的内容供重试 */ }
		finally { if (!disposed && token === ownerToken) saving.value = false }
	}
	const syncSession = () => {
		const token = uni.getStorageSync('member_token') || ''
		if (ownerToken !== token) { ownerToken = token; content.value = ''; mobile.value = ''; submitted.value = false; saving.value = false }
		loggedIn.value = Boolean(token)
		if (token && !types.value.length) loadOptions()
	}
	onShow(syncSession)
	onUnload(() => { disposed = true; version += 1 })
</script>

<style scoped>
	.member-feedback-page { max-width: 700px; min-height: 100vh; margin: 0 auto; padding-bottom: calc(30px + env(safe-area-inset-bottom)); background: #f3f3f3; }
	.member-feedback-form { margin-top: 12px; background: #ffffff; }
	.member-feedback-field { display: flex; align-items: center; justify-content: space-between; gap: 14px; min-height: 54px; padding: 14px 16px; border-bottom: 1px solid #f3f3f3; font-size: 14px; }
	.member-feedback-picker-value { display: flex; align-items: center; gap: 12px; color: #777777; }
	.member-feedback-arrow { color: #aaaaaa; font-size: 24px; }
	.member-feedback-content-field { padding: 18px 16px 12px; border-bottom: 1px solid #f3f3f3; }
	.member-feedback-label { display: block; margin-bottom: 16px; font-size: 14px; }
	.member-feedback-content { width: 100%; min-height: 180px; color: #555555; font-size: 14px; line-height: 23px; }
	.member-feedback-counter { display: block; text-align: right; color: #aaaaaa; font-size: 11px; }
	.member-feedback-mobile { flex: 1; min-width: 0; text-align: right; font-size: 14px; height: 26px; }
	.member-feedback-actions { padding: 28px 16px; background: #f3f3f3; }
	.member-feedback-save { margin: 0; border-radius: 3px; background: #df3b3b; color: #ffffff; line-height: 46px; font-size: 15px; }
	.member-feedback-save[disabled] { color: #ffffff; background: #eaa3a3; }
	.member-feedback-state { padding: 85px 20px; color: #999999; text-align: center; font-size: 13px; line-height: 22px; }
	.member-feedback-state text { display: block; }
	.member-feedback-retry { display: inline-block; margin-top: 18px; padding: 0 22px; border-radius: 18px; color: #ee4442; background: #ffffff; font-size: 12px; line-height: 34px; }
	.member-feedback-success { padding: 75px 24px; text-align: center; font-size: 18px; }
	.member-feedback-success-mark { display: block; width: 56px; height: 56px; margin: 0 auto 22px; border-radius: 50%; color: #ffffff; background: #4dbb76; font-size: 34px; line-height: 56px; }
	.member-feedback-success-note { display: block; margin: 14px 0 32px; color: #999999; font-size: 13px; line-height: 21px; }
	.member-feedback-save::after, .member-feedback-retry::after { border: 0; }
	@media (max-width: 360px) { .member-feedback-field { gap: 10px; font-size: 13px; } .member-feedback-mobile { font-size: 13px; } }
</style>
