<template>
	<view class="profile-page">
		<!-- 顶部红色个人信息区 -->
		<view class="header">
			<view class="header-bg">
				<view class="bg-shape bg-shape--1"></view>
				<view class="bg-shape bg-shape--2"></view>
			</view>
			<button class="profile-settings" aria-label="个人信息设置" @click="openSettings"><image src="/static/icons/ic-settings.svg" mode="aspectFit" /></button>
			<view class="header-inner">
				<view class="avatar-wrap">
					<image class="avatar" :src="imageUrl(member.avatar) || '/static/avatar-default.svg'" mode="aspectFill"></image>
				</view>
				<text class="username">{{ loading ? '正在加载…' : displayName }}</text>
			</view>
		</view>

		<view v-if="failed" class="profile-error"><text>部分信息加载失败</text><button @click="load">重新加载</button></view>
		<!-- 我的订单 -->
		<view class="panel">
			<view class="panel-head" @click="openOrders('all')">
				<text class="panel-title">我的订单</text>
				<view class="panel-more">
					<text class="panel-more-text">全部订单</text>
					<text class="chevron">›</text>
				</view>
			</view>
			<view class="grid grid--4">
				<view
					v-for="(item, index) in orderEntries"
					:key="item.key"
					class="grid-item"
					@click="openOrders(item.key)"
				>
					<image class="grid-icon" :src="item.icon" mode="aspectFit"></image>
					<text v-if="counts[item.key]" class="profile-badge">{{ badge(counts[item.key]) }}</text>
					<text class="grid-label">{{ item.label }}</text>
					<view v-if="index < orderEntries.length - 1" class="grid-divider"></view>
				</view>
			</view>
		</view>

		<view class="gap"></view>

		<!-- 我的优惠券 -->
		<view class="panel">
			<view class="panel-head" @click="openCoupons(0)">
				<text class="panel-title">我的优惠券</text>
				<view class="panel-more">
					<text class="panel-more-text">全部优惠券</text>
					<text class="chevron">›</text>
				</view>
			</view>
			<view class="grid grid--3">
				<view
					v-for="(item, index) in couponEntries"
					:key="item.key"
					class="grid-item"
					@click="openCoupons(item.status)"
				>
					<image class="grid-icon" :src="item.icon" mode="aspectFit"></image>
					<text v-if="couponCounts[item.key]" class="profile-badge">{{ badge(couponCounts[item.key]) }}</text>
					<text class="grid-label">{{ item.label }}</text>
					<view v-if="index < couponEntries.length - 1" class="grid-divider"></view>
				</view>
			</view>
		</view>

		<view class="gap"></view>

		<!-- 列表入口 -->
		<view class="menu">
			<view
				v-for="item in menuEntries"
				:key="item.key"
				class="menu-item"
				@click="onMenu(item)"
			>
				<image class="menu-icon" :src="item.icon" mode="aspectFit"></image>
				<text class="menu-label">{{ item.label }}</text>
				<text class="chevron chevron--menu">›</text>
			</view>
		</view>

		<tab-bar current="profile" />
	</view>
</template>

<script setup>
	import { computed, reactive, ref } from 'vue'
	import { onShow, onHide, onUnload } from '@dcloudio/uni-app'
	import { memberProfile } from '@/api/member.js'
	import { orderMySummary } from '@/api/order.js'
	import { imageUrl } from '@/api/url.js'
	import TabBar from '@/components/tab-bar/tab-bar.vue'

	// 状态映射由后端统一处理，首页与订单列表共用 tab。
	const orderEntries = [
		{ key: 'pay', label: '待付款', icon: '/static/icons/ic-order-pay.svg' },
		{ key: 'send', label: '待发货', icon: '/static/icons/ic-order-send.svg' },
		{ key: 'receive', label: '待收货', icon: '/static/icons/ic-order-receive.svg' },
		{ key: 'done', label: '已完成', icon: '/static/icons/ic-order-done.svg' }
	]

	// 优惠券入口
	const couponEntries = [
		{ key: 'unused', status: 0, label: '待使用', icon: '/static/icons/ic-coupon-unused.svg' },
		{ key: 'used', status: 1, label: '已使用', icon: '/static/icons/ic-coupon-used.svg' },
		{ key: 'expired', status: 2, label: '过期关闭', icon: '/static/icons/ic-coupon-expired.svg' }
	]

	// 常用入口
	const menuEntries = [
		{ key: 'favorite', label: '我的收藏', icon: '/static/icons/ic-star.svg' },
		{ key: 'address', label: '收货地址', icon: '/static/icons/ic-pin.svg' },
		{ key: 'service', label: '服务中心', icon: '/static/icons/ic-service.svg' }
	]

	const member = reactive({
		username: '',
		nickname: '',
		avatar: ''
	})

	const displayName = computed(() => member.nickname || member.username || '会员')

	const counts = reactive({ all: 0, pay: 0, send: 0, receive: 0, done: 0 })
	const couponCounts = reactive({ unused: 0, used: 0, expired: 0 })
	const loading = ref(false), failed = ref(false)
	let disposed = false, version = 0, owner = ''
	const badge = (value) => Number(value) > 99 ? '99+' : value
	const load = async () => {
		const token = uni.getStorageSync('member_token') || ''
		if (!token) { uni.reLaunch({ url: '/pages/login/login' }); return }
		if (owner !== token) {
			Object.assign(member, { username: '', nickname: '', avatar: '' })
			Object.keys(counts).forEach((key) => { counts[key] = 0 })
			Object.keys(couponCounts).forEach((key) => { couponCounts[key] = 0 })
			owner = token
		}
		const current = ++version
		loading.value = true; failed.value = false
		const results = await Promise.allSettled([memberProfile(), orderMySummary()])
		if (disposed || current !== version || token !== uni.getStorageSync('member_token')) return
		if (results[0].status === 'fulfilled') { Object.assign(member, results[0].value.data || {}); uni.setStorageSync('member_info', results[0].value.data || {}) }
		if (results[1].status === 'fulfilled') {
			const data = results[1].value.data || {}
			Object.keys(counts).forEach((key) => { counts[key] = Number(data.counts && data.counts[key]) || 0 })
			Object.keys(couponCounts).forEach((key) => { couponCounts[key] = Number(data.coupon_counts && data.coupon_counts[key]) || 0 })
		}
		failed.value = results.some((result) => result.status === 'rejected'); loading.value = false
	}
	const navigate = (url) => { if (owner === uni.getStorageSync('member_token')) uni.navigateTo({ url }) }
	const openSettings = () => navigate('/pages/profile/settings')
	const openOrders = (tab) => navigate('/pages/order/list?tab=' + tab)
	const openCoupons = (status) => navigate('/pages/profile/coupons?status=' + status)
	const onMenu = (item) => {
		const paths = { address: '/pages/address/index', favorite: '/pages/profile/favorites', service: '/pages/profile/service' }
		navigate(paths[item.key])
	}
	onShow(load)
	onHide(() => { version += 1 })
	onUnload(() => { disposed = true; version += 1 })
</script>

<style scoped>
	.profile-page {
		min-height: 100vh;
		max-width: 700px;
		margin: 0 auto;
		padding-bottom: calc(76px + env(safe-area-inset-bottom));
		background-color: #f3f3f3;
		box-sizing: border-box;
	}

	/* ---------------- 头部 ---------------- */
	.header {
		position: relative;
		height: 142px;
		overflow: hidden;
	}

	.header-bg {
		position: absolute;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		background-image: linear-gradient(135deg, #ee4442 0%, #e03333 100%);
	}

	.bg-shape {
		position: absolute;
		border: 2px solid rgba(255, 255, 255, 0.12);
		border-radius: 6px;
	}

	.bg-shape--1 {
		width: 120px;
		height: 120px;
		left: -30px;
		top: -40px;
		transform: rotate(45deg);
	}

	.bg-shape--2 {
		width: 160px;
		height: 160px;
		right: -50px;
		bottom: -80px;
		transform: rotate(45deg);
	}

	.header-inner {
		position: relative;
		z-index: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding-top: 34px;
	}

	.avatar-wrap {
		width: 60px;
		height: 60px;
		border-radius: 50%;
		overflow: hidden;
		background-color: #ffffff;
	}

	.avatar {
		width: 60px;
		height: 60px;
		display: block;
	}

	.username {
		margin-top: 9px;
		font-size: 15px;
		color: #ffffff;
		letter-spacing: 0.5px;
	}

	/* ---------------- 订单 / 优惠券卡片 ---------------- */
	.panel {
		padding: 0 16px;
		background-color: #ffffff;
	}

	.panel-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		height: 46px;
	}

	.panel-title {
		font-size: 15px;
		font-weight: 600;
		color: #333333;
	}

	.panel-more {
		display: flex;
		align-items: center;
	}

	.panel-more-text {
		font-size: 12px;
		color: #9aa0a6;
	}

	.grid {
		display: flex;
		align-items: center;
		padding-bottom: 16px;
	}

	.grid-item {
		position: relative;
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding-top: 4px;
	}

	.grid-icon {
		width: 27px;
		height: 27px;
		display: block;
	}

	.grid-label {
		margin-top: 8px;
		font-size: 12px;
		color: #4a4f57;
	}

	.grid-divider {
		position: absolute;
		right: 0;
		top: 8px;
		width: 1px;
		height: 38px;
		background-color: #f0f0f0;
	}

	.gap {
		height: 8px;
		background-color: #f6f6f6;
	}

	/* ---------------- 列表入口 ---------------- */
	.menu {
		padding: 0 16px;
		background-color: #ffffff;
	}

	.menu-item {
		display: flex;
		align-items: center;
		height: 48px;
		border-bottom: 1px solid #f5f5f5;
	}

	.menu-item:last-child {
		border-bottom: none;
	}

	.menu-icon {
		width: 17px;
		height: 17px;
		margin-right: 8px;
		display: block;
	}

	.menu-label {
		flex: 1;
		font-size: 14px;
		color: #333333;
	}

	.chevron {
		font-size: 18px;
		line-height: 18px;
		color: #c8ccd4;
		margin-left: 4px;
	}

	.chevron--menu {
		font-size: 18px;
	}

	.profile-settings { position:absolute; z-index:2; top:8px; right:10px; display:flex; align-items:center; justify-content:center; width:36px; height:36px; padding:6px; border-radius:50%; background:transparent; }
	.profile-settings::after { border:0; }
	.profile-settings image { width:24px; height:24px; }
	.profile-badge { position:absolute; top:0; left:calc(50% + 5px); min-width:16px; padding:0 4px; border-radius:10px; background:#ef273c; color:#fff; font-size:10px; line-height:16px; text-align:center; }
	.profile-error { display:flex; align-items:center; justify-content:center; gap:12px; background:#fff8f0; color:#a9793a; font-size:12px; padding:6px 12px; }
	.profile-error button { margin:0; padding:0 10px; line-height:28px; font-size:12px; color:#a9793a; background:transparent; }
	.profile-error button::after { border:0; }
</style>
