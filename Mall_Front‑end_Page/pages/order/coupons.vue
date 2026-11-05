<template>
	<view class="order-coupons-page">
		<nav-header title="使用优惠券" />
		<view class="order-coupons-tabs" role="tablist" aria-label="优惠券可用状态">
			<view class="order-coupons-tab" :class="{ 'order-coupons-tab--active': activeTab === 'available' }" role="tab" :aria-selected="activeTab === 'available'" @click="activeTab = 'available'">可用优惠券（{{ availableCoupons.length }}）</view>
			<view class="order-coupons-tab" :class="{ 'order-coupons-tab--active': activeTab === 'unavailable' }" role="tab" :aria-selected="activeTab === 'unavailable'" @click="activeTab = 'unavailable'">不可用优惠券（{{ unavailableCoupons.length }}）</view>
		</view>
		<view v-if="loading" class="order-coupons-state">正在核对优惠券…</view>
		<view v-else-if="loadFailed || invalidQuote" class="order-coupons-state">
			<text>{{ invalidQuote ? '订单报价信息无效，请返回重新确认' : '优惠券暂时未能加载，请重试或返回重新确认订单' }}</text>
			<button v-if="!invalidQuote" class="order-coupons-retry" @click="loadCoupons">重新加载</button>
		</view>
		<view v-else class="order-coupons-list">
			<view v-if="!visibleCoupons.length" class="order-coupons-state">{{ activeTab === 'available' ? '暂无可用优惠券' : '暂无不可用优惠券' }}</view>
			<view
				v-for="item in visibleCoupons"
				:key="item.id"
				class="order-coupon"
				:class="{ 'order-coupon--unavailable': !item.available, 'order-coupon--selected': selectedId === item.id && item.available }"
				role="radio"
				:aria-label="item.name"
				:aria-disabled="!item.available"
				:aria-checked="selectedId === item.id && item.available"
				@click="selectCoupon(item)"
			>
				<view class="order-coupon-main">
					<view class="order-coupon-face"><text>{{ faceText(item) }}</text><text class="order-coupon-min">{{ item.min_text }}</text></view>
					<view class="order-coupon-info"><text class="order-coupon-name">{{ item.name }}</text><text v-if="item.tag" class="order-coupon-tag">{{ item.tag }}</text><text class="order-coupon-time">{{ item.time_text }}</text></view>
					<view v-if="item.available" class="order-coupon-radio" :class="{ 'order-coupon-radio--selected': selectedId === item.id }"><text v-if="selectedId === item.id">✓</text></view>
				</view>
				<text v-if="item.description" class="order-coupon-description">{{ item.description }}</text>
				<text v-if="!item.available" class="order-coupon-reason">不可用：{{ item.reason || '当前订单不满足使用条件' }}</text>
				<text v-else-if="item.discount_amount_text" class="order-coupon-saving">本订单可抵扣 ¥{{ item.discount_amount_text }}</text>
			</view>
		</view>
		<view class="order-coupons-footer"><button class="order-coupons-none" @click="useNone">不使用优惠券</button></view>
	</view>
</template>

<script setup>
	import { computed, ref } from 'vue'
	import { onLoad, onUnload } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { orderCouponList } from '@/api/order.js'

	const coupons = ref([])
	const activeTab = ref('available')
	const loading = ref(false)
	const loadFailed = ref(false)
	const invalidQuote = ref(false)
	const selectedId = ref(0)
	const availableCoupons = computed(() => coupons.value.filter((item) => item.available))
	const unavailableCoupons = computed(() => coupons.value.filter((item) => !item.available))
	const visibleCoupons = computed(() => activeTab.value === 'available' ? availableCoupons.value : unavailableCoupons.value)
	let quoteToken = ''
	let disposed = false
	let returning = false
	let version = 0

	const faceText = (item) => {
		const value = item.discount ?? item.discount_text
		return value !== '' && value != null && Number.isFinite(Number(value)) ? `¥${Number(value).toFixed(2)}` : String(value || '优惠券')
	}
	const loadCoupons = async () => {
		if (disposed || loading.value || !quoteToken) return
		const requestVersion = ++version
		const token = uni.getStorageSync('member_token')
		loading.value = true
		loadFailed.value = false
		try {
			const res = await orderCouponList({ quote_token: quoteToken })
			if (disposed || requestVersion !== version || token !== uni.getStorageSync('member_token')) return
			coupons.value = Array.isArray(res.data && res.data.rows) ? res.data.rows : []
		} catch (error) {
			if (!disposed && requestVersion === version) loadFailed.value = true
		} finally { if (!disposed && requestVersion === version) loading.value = false }
	}
	const returnCoupon = (id) => {
		if (returning || disposed) return
		returning = true
		uni.$emit('checkout:coupon:selected', { id })
		uni.navigateBack({ complete: () => { returning = false } })
	}
	const selectCoupon = (item) => {
		if (loading.value || loadFailed.value || !item.available || !Number.isSafeInteger(Number(item.id)) || Number(item.id) <= 0) return
		returnCoupon(Number(item.id))
	}
	const useNone = () => returnCoupon(0)
	onLoad((options = {}) => {
		quoteToken = String(options.quote_token || '')
		selectedId.value = Number(options.selected_id) || 0
		if (!quoteToken) { invalidQuote.value = true; return }
		loadCoupons()
	})
	onUnload(() => { disposed = true; version += 1 })
</script>

<style scoped>
	.order-coupons-page { max-width: 700px; min-height: 100vh; margin: 0 auto; padding-bottom: calc(84px + env(safe-area-inset-bottom)); background: #f4f4f4; color: #333333; }
	.order-coupons-tabs { display: flex; background: #ffffff; }
	.order-coupons-tab { flex: 1; padding: 16px 6px 14px; border-bottom: 2px solid transparent; text-align: center; font-size: 13px; line-height: 20px; color: #999999; }
	.order-coupons-tab--active { border-bottom-color: #ee4442; color: #ee4442; }
	.order-coupons-state { padding: 65px 18px; font-size: 13px; color: #999999; text-align: center; line-height: 22px; }
	.order-coupons-state text { display: block; }
	.order-coupons-retry { display: inline-block; padding: 0 20px; margin-top: 16px; line-height: 32px; border: 1px solid #ee4442; border-radius: 18px; background: #ffffff; color: #ee4442; font-size: 12px; }
	.order-coupons-retry::after, .order-coupons-none::after { border: 0; }
	.order-coupons-list { padding: 12px; }
	.order-coupon { margin-bottom: 12px; padding: 15px 13px 12px; border: 1px solid transparent; border-radius: 8px; background: #ffffff; }
	.order-coupon--selected { border-color: #ee4442; }
	.order-coupon-main { display: flex; align-items: center; gap: 12px; }
	.order-coupon-face { width: 94px; flex-shrink: 0; color: #ee4442; font-size: 24px; }
	.order-coupon-min { display: block; margin-top: 8px; color: #999999; font-size: 11px; line-height: 17px; }
	.order-coupon-info { flex: 1; min-width: 0; }
	.order-coupon-name { display: block; font-size: 14px; line-height: 21px; word-break: break-word; }
	.order-coupon-tag { display: inline-block; margin-top: 5px; color: #ee4442; font-size: 11px; }
	.order-coupon-time { display: block; margin-top: 5px; color: #aaaaaa; font-size: 11px; line-height: 17px; word-break: break-word; }
	.order-coupon-radio { width: 20px; height: 20px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border: 1px solid #dddddd; border-radius: 50%; }
	.order-coupon-radio--selected { background: #ee4442; border-color: #ee4442; color: #ffffff; font-size: 13px; }
	.order-coupon-description, .order-coupon-reason, .order-coupon-saving { display: block; margin-top: 12px; padding-top: 10px; border-top: 1px dashed #eeeeee; color: #999999; font-size: 11px; line-height: 18px; word-break: break-word; }
	.order-coupon-reason { color: #a48e82; }
	.order-coupon-saving { color: #ee4442; }
	.order-coupon--unavailable .order-coupon-face, .order-coupon--unavailable .order-coupon-name, .order-coupon--unavailable .order-coupon-tag { color: #aaaaaa; }
	.order-coupons-footer { position: fixed; bottom: 0; left: 0; right: 0; max-width: 700px; margin: 0 auto; padding: 9px 16px calc(9px + env(safe-area-inset-bottom)); border-top: 1px solid #eeeeee; background: #ffffff; }
	.order-coupons-none { margin: 0; height: 42px; line-height: 42px; border: 1px solid #ee4442; border-radius: 22px; background: #ffffff; color: #ee4442; font-size: 14px; }
	@media (max-width: 360px) { .order-coupon-face { width: 80px; font-size: 21px; } .order-coupon-main { gap: 9px; } .order-coupon { padding-left: 10px; padding-right: 10px; } }
</style>
