<template>
	<view class="my-coupons-page">
		<view class="my-coupons-header"><nav-header title="我的优惠券" /><view class="my-coupons-tabs" role="tablist" aria-label="我的优惠券状态"><view v-for="tab in tabs" :key="tab.status" class="my-coupons-tab" :class="{ 'my-coupons-tab--active': status === tab.status }" role="tab" :aria-selected="status === tab.status" @click="selectTab(tab.status)">{{ tab.label }}</view></view></view>
		<view v-if="!loggedIn" class="my-coupons-state"><text>请登录后查看本人优惠券</text><button class="my-coupons-retry" @click="goLogin">去登录</button></view>
		<view v-else-if="loading" class="my-coupons-state">正在加载优惠券…</view>
		<view v-else-if="failed" class="my-coupons-state"><text>优惠券加载失败</text><button class="my-coupons-retry" @click="load">重新加载</button></view>
		<template v-else>
			<view v-for="coupon in visibleRows" :key="coupon.id" class="my-coupons-card" :class="{ 'my-coupons-card--expired': status === 2 }">
				<view class="my-coupons-card-main"><view class="my-coupons-face"><text class="my-coupons-discount"><text class="my-coupons-currency">¥</text>{{ amount(coupon.discount) }}<text class="my-coupons-unit">元</text></text><text class="my-coupons-min">{{ coupon.min_text }}</text></view><view class="my-coupons-info"><text class="my-coupons-name">{{ coupon.name }}</text><text class="my-coupons-time">有效期至 {{ coupon.end_time || '未设置' }}</text><text class="my-coupons-scope">{{ coupon.goods_type_name }}</text></view></view>
				<view v-if="coupon.description || coupon.tag" class="my-coupons-description">{{ [coupon.description, coupon.tag].filter(Boolean).join(' · ') }}</view>
				<view v-if="status === 1" class="my-coupons-used"><text>使用时间：{{ coupon.use_time || '未记录' }}</text><button v-if="coupon.order_id" class="my-coupons-order" @click="openOrder(coupon)">查看使用订单</button></view>
			</view>
			<view v-if="loaded && !rows.length" class="my-coupons-state">暂无{{ tabs.find((tab) => tab.status === status).label }}优惠券</view>
			<button v-else-if="visibleCount < rows.length" class="my-coupons-more" @click="showMore">加载更多</button>
			<view v-else-if="loaded" class="my-coupons-end">没有更多了</view>
			<view v-if="status === 0 && rows.length" class="my-coupons-note">是否满足使用范围和满减条件，以确认订单页面的实际校验为准。</view>
		</template>
	</view>
</template>

<script setup>
	import { computed, ref } from 'vue'
	import { onLoad, onReachBottom, onShow, onUnload } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { couponMyList } from '@/api/marketing.js'
	const tabs = [{ status: 0, label: '未使用' }, { status: 1, label: '已使用' }, { status: 2, label: '已过期' }]
	const status = ref(0), rows = ref([]), visibleCount = ref(20), loading = ref(false), loaded = ref(false), failed = ref(false), loggedIn = ref(false)
	const visibleRows = computed(() => rows.value.slice(0, visibleCount.value))
	let disposed = false, version = 0, ownerToken = ''
	const amount = (value) => { const numeric = Number(value); return Number.isFinite(numeric) ? numeric.toFixed(2).replace(/\.00$/, '') : '0' }
	const goLogin = () => uni.navigateTo({ url: '/pages/login/login' })
	const load = async () => {
		if (disposed) return
		const token = uni.getStorageSync('member_token') || '', requestId = ++version
		ownerToken = token; loggedIn.value = Boolean(token); rows.value = []; visibleCount.value = 20; loaded.value = false; failed.value = false
		if (!token) { loading.value = false; return }
		loading.value = true
		try {
			const res = await couponMyList({ status: status.value })
			if (disposed || requestId !== version || token !== uni.getStorageSync('member_token')) return
			rows.value = Array.isArray(res.data && res.data.rows) ? res.data.rows : []; loaded.value = true
		} catch (error) { if (!disposed && requestId === version && token === uni.getStorageSync('member_token')) failed.value = true }
		finally { if (!disposed && requestId === version) loading.value = false }
	}
	const selectTab = (value) => { if (value !== status.value) { status.value = value; load() } }
	const showMore = () => { visibleCount.value += 20 }
	const openOrder = (coupon) => { if (ownerToken !== uni.getStorageSync('member_token')) { load(); return }; const id = Number(coupon.order_id); if (Number.isSafeInteger(id) && id > 0) uni.navigateTo({ url: `/pages/order/detail?id=${id}` }) }
	onLoad((options = {}) => { const initial = Number(options.status); if ([0, 1, 2].includes(initial)) status.value = initial })
	onShow(load)
	onReachBottom(showMore)
	onUnload(() => { disposed = true; version += 1 })
</script>

<style scoped>
	.my-coupons-page { max-width: 700px; min-height: 100vh; margin: 0 auto; padding-bottom: calc(24px + env(safe-area-inset-bottom)); background: #f3f3f3; }
	.my-coupons-header { position: sticky; top: 0; z-index: 10; background: #ffffff; }
	.my-coupons-tabs { display: flex; padding: 14px 16px; }
	.my-coupons-tab { flex: 1; padding: 7px 4px; border: 1px solid #f5223e; border-right: 0; color: #f5223e; text-align: center; font-size: 13px; line-height: 18px; }
	.my-coupons-tab:first-child { border-radius: 2px 0 0 2px; }
	.my-coupons-tab:last-child { border-right: 1px solid #f5223e; border-radius: 0 2px 2px 0; }
	.my-coupons-tab--active { color: #ffffff; background: #f5223e; }
	.my-coupons-card { margin: 16px; border: 1px solid #ff565b; border-radius: 3px; background: #ffffff; overflow: hidden; }
	.my-coupons-card-main { display: flex; align-items: center; gap: 18px; padding: 22px 14px; }
	.my-coupons-face { flex: 0 0 112px; min-width: 0; }
	.my-coupons-discount { display: block; color: #ff565b; font-size: 27px; line-height: 34px; white-space: nowrap; }
	.my-coupons-currency, .my-coupons-unit { font-size: 13px; margin-right: 3px; }
	.my-coupons-unit { margin-left: 3px; }
	.my-coupons-min { display: block; margin-top: 5px; color: #ff565b; font-size: 11px; line-height: 18px; overflow-wrap: anywhere; }
	.my-coupons-info { flex: 1; min-width: 0; }
	.my-coupons-name { display: block; font-size: 15px; line-height: 22px; overflow-wrap: anywhere; }
	.my-coupons-time, .my-coupons-scope { display: block; margin-top: 7px; color: #999999; font-size: 11px; line-height: 18px; }
	.my-coupons-description { padding: 10px 14px; border-top: 1px dashed #eeeeee; color: #999999; font-size: 12px; line-height: 20px; overflow-wrap: anywhere; }
	.my-coupons-used { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; padding: 10px 14px; border-top: 1px dashed #eeeeee; color: #999999; font-size: 11px; line-height: 20px; }
	.my-coupons-order { margin: 0; padding: 0 8px; border: 1px solid #eeeeee; border-radius: 3px; color: #666666; background: #ffffff; font-size: 11px; line-height: 26px; }
	.my-coupons-card--expired { border-color: #cccccc; }
	.my-coupons-card--expired .my-coupons-discount, .my-coupons-card--expired .my-coupons-min { color: #aaaaaa; }
	.my-coupons-state { padding: 65px 16px; color: #999999; text-align: center; font-size: 13px; line-height: 22px; }
	.my-coupons-state text { display: block; }
	.my-coupons-retry, .my-coupons-more { width: max-content; margin: 18px auto; padding: 0 22px; border-radius: 18px; background: #ffffff; color: #ee4442; font-size: 12px; line-height: 34px; }
	.my-coupons-end { padding: 20px 16px; color: #999999; text-align: center; font-size: 12px; }
	.my-coupons-note { padding: 0 24px 14px; color: #aaaaaa; text-align: center; font-size: 11px; line-height: 18px; }
	.my-coupons-retry::after, .my-coupons-more::after, .my-coupons-order::after { border: 0; }
	@media (max-width: 360px) { .my-coupons-card { margin: 12px; } .my-coupons-card-main { gap: 10px; padding: 18px 12px; } .my-coupons-face { flex-basis: 100px; } .my-coupons-discount { font-size: 24px; } }
</style>
