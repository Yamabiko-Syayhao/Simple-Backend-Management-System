<template>
	<view class="member-service-page">
		<nav-header title="服务中心" />
		<view class="member-service-menu"><view class="member-service-menu-item" role="button" aria-label="联系客服" @click="openContact"><text>联系客服</text><text class="member-service-arrow">›</text></view><view class="member-service-menu-item" role="button" aria-label="意见反馈" @click="openFeedback"><text>意见反馈</text><text class="member-service-arrow">›</text></view><view class="member-service-menu-item" role="button" aria-label="常见问题" @click="openFaq"><text>常见问题</text><text class="member-service-arrow">›</text></view></view>
		<view v-if="contactVisible" class="member-service-popup"><view class="member-service-mask" @click="contactVisible = false" @touchmove.stop.prevent></view><view class="member-service-dialog" role="dialog" aria-label="联系客服">
			<view class="member-service-dialog-head"><text>联系客服</text><button class="member-service-close" aria-label="关闭客服信息" @click="contactVisible = false">×</button></view>
			<view v-if="loading" class="member-service-state">正在加载客服信息…</view>
			<view v-else-if="failed" class="member-service-state"><text>客服信息暂时无法加载</text><button class="member-service-retry" @click="loadContact">重新加载</button></view>
			<scroll-view v-else class="member-service-contact-scroll" scroll-y><view class="member-service-contact-title">{{ contact.name }}</view><view class="member-service-row"><text>联系电话</text><text>{{ contact.phone || '暂未配置' }}</text></view><view class="member-service-row"><text>客服 QQ</text><text>{{ contact.qq || '暂未配置' }}</text></view><view class="member-service-row"><text>当前版本</text><text>{{ contact.version || '暂无版本信息' }}</text></view><view class="member-service-row"><text>用户协议</text><button v-if="contact.agreement" class="member-service-agreement-button" @click="agreementVisible = !agreementVisible">{{ agreementVisible ? '收起协议' : '查看协议' }}</button><text v-else>暂未配置</text></view><text v-if="agreementVisible && contact.agreement" class="member-service-agreement">{{ contact.agreement }}</text></scroll-view>
			<button class="member-service-confirm" @click="contactVisible = false">知道了</button>
		</view></view>
	</view>
</template>

<script setup>
	import { ref } from 'vue'
	import { onUnload } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { feedbackContact } from '@/api/feedback.js'
	const contact = ref({}), contactVisible = ref(false), agreementVisible = ref(false), loading = ref(false), failed = ref(false)
	let disposed = false, version = 0, ownerToken = ''
	const loadContact = async () => {
		if (disposed) return
		const token = uni.getStorageSync('member_token') || ''
		if (ownerToken !== token) { version += 1; loading.value = false; contact.value = {}; ownerToken = token }
		if (!token) { uni.navigateTo({ url: '/pages/login/login' }); return }
		if (loading.value) return
		const requestId = ++version
		loading.value = true; failed.value = false
		try { const res = await feedbackContact(); if (!disposed && requestId === version && token === uni.getStorageSync('member_token')) contact.value = res.data || {} }
		catch (error) { if (!disposed && requestId === version && token === uni.getStorageSync('member_token')) failed.value = true }
		finally { if (!disposed && requestId === version) loading.value = false }
	}
	const openContact = () => { if (!uni.getStorageSync('member_token')) { uni.navigateTo({ url: '/pages/login/login' }); return }; contactVisible.value = true; contact.value = {}; agreementVisible.value = false; loadContact() }
	const openFeedback = () => uni.navigateTo({ url: '/pages/profile/feedback' })
	const openFaq = () => uni.navigateTo({ url: '/pages/profile/faq' })
	onUnload(() => { disposed = true; version += 1 })
</script>

<style scoped>
	.member-service-page { max-width: 700px; min-height: 100vh; margin: 0 auto; padding-bottom: env(safe-area-inset-bottom); background: #f3f3f3; }
	.member-service-menu { margin-top: 12px; padding: 0 16px; background: #ffffff; }
	.member-service-menu-item { display: flex; align-items: center; justify-content: space-between; min-height: 56px; padding: 15px 0; border-bottom: 1px solid #f2f2f2; font-size: 14px; }
	.member-service-menu-item:last-child { border: 0; }
	.member-service-arrow { color: #aaaaaa; font-size: 24px; }
	.member-service-popup { position: fixed; inset: 0; z-index: 1000; display: flex; justify-content: center; align-items: center; padding: 24px; }
	.member-service-mask { position: absolute; inset: 0; background: rgba(0, 0, 0, 0.55); }
	.member-service-dialog { position: relative; width: 100%; max-width: 420px; border-radius: 12px; overflow: hidden; background: #ffffff; }
	.member-service-dialog-head { display: flex; align-items: center; justify-content: space-between; padding: 15px 18px; border-bottom: 1px solid #f3f3f3; font-size: 16px; }
	.member-service-close { margin: 0; padding: 0 0 0 14px; color: #aaaaaa; background: transparent; font-size: 25px; line-height: 28px; }
	.member-service-contact-scroll { max-height: 55vh; }
	.member-service-contact-title { padding: 20px 18px 12px; text-align: center; font-size: 17px; overflow-wrap: anywhere; }
	.member-service-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 14px 18px; color: #777777; font-size: 13px; line-height: 21px; }
	.member-service-row > text:last-child { text-align: right; overflow-wrap: anywhere; }
	.member-service-agreement-button { margin: 0; padding: 0; background: transparent; color: #ee4442; font-size: 13px; line-height: 22px; }
	.member-service-agreement { display: block; padding: 12px 18px 20px; white-space: pre-wrap; overflow-wrap: anywhere; font-size: 12px; line-height: 22px; color: #777777; }
	.member-service-confirm { margin: 10px 0 0; padding: 0; border-top: 1px solid #eeeeee; border-radius: 0; color: #ee4442; background: #ffffff; font-size: 15px; line-height: 50px; }
	.member-service-state { padding: 35px 18px; text-align: center; color: #999999; font-size: 13px; line-height: 22px; }
	.member-service-state text { display: block; }
	.member-service-retry { display: inline-block; margin-top: 15px; padding: 0 18px; border-radius: 18px; color: #ee4442; background: #f8f8f8; font-size: 12px; line-height: 32px; }
	.member-service-close::after, .member-service-agreement-button::after, .member-service-confirm::after, .member-service-retry::after { border: 0; }
	@media (max-width: 360px) { .member-service-popup { padding: 16px; } .member-service-row { padding: 12px 14px; } }
</style>
