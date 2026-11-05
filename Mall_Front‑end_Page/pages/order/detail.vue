<template>
	<view class="my-order-detail-page">
		<nav-header title="订单详情" />
		<view v-if="!loggedIn" class="my-order-detail-state"><text>请登录后查看本人订单</text><button class="my-order-detail-retry" @click="goLogin">去登录</button></view>
		<view v-else-if="loading" class="my-order-detail-state">正在加载订单…</view>
		<view v-else-if="failed || !order.id" class="my-order-detail-state"><text>{{ invalidId ? '订单参数无效' : '订单不存在或暂时无法加载' }}</text><button v-if="!invalidId" class="my-order-detail-retry" @click="load">重新加载</button></view>
		<template v-else>
			<view class="my-order-detail-status"><text>{{ order.status_name }}</text><text class="my-order-detail-date">{{ order.order_time }}</text></view>
			<view class="my-order-detail-section"><text class="my-order-detail-section-title">收货地址</text><text class="my-order-detail-address-name">{{ order.address && order.address.receiver_name }} {{ order.address && order.address.mobile }}</text><text class="my-order-detail-muted">{{ order.address && order.address.region }} {{ order.address && order.address.detail }}</text></view>
			<view class="my-order-detail-section">
				<view v-for="(item, index) in order.items || []" :key="index" class="my-order-detail-item">
					<image v-if="item.image" class="my-order-detail-image" :src="imageUrl(item.image)" mode="aspectFit" />
					<view v-else class="my-order-detail-image my-order-detail-image--empty">暂无图片</view>
					<view class="my-order-detail-info"><text class="my-order-detail-name">{{ item.name }}</text><text class="my-order-detail-muted">{{ item.specification }}</text><view class="my-order-detail-item-price"><text>¥{{ item.price_text }}</text><text>×{{ item.quantity }}</text></view></view>
				</view>
				<view v-if="!(order.items || []).length" class="my-order-detail-muted">暂无商品明细</view>
			</view>
			<view class="my-order-detail-section"><view class="my-order-detail-row"><text>商品金额</text><text>¥{{ order.goods_amount_text }}</text></view><view class="my-order-detail-row"><text>邮费</text><text>¥{{ order.freight_amount_text }}</text></view><view class="my-order-detail-row"><text>优惠券抵扣</text><text>-¥{{ order.discount_amount_text }}</text></view><view class="my-order-detail-row"><text>订单合计（含运费）</text><text class="my-order-detail-amount">¥{{ order.order_amount_text }}</text></view></view>
			<view class="my-order-detail-section"><view class="my-order-detail-row"><text>订单编号</text><text class="my-order-detail-value">{{ order.order_no }}</text></view><view class="my-order-detail-row"><text>订单备注</text><text class="my-order-detail-value">{{ order.user_message || '无' }}</text></view></view>
			<view v-if="Number(order.status) === 1" class="my-order-detail-footer"><button class="my-order-detail-pay" @click="goPayment">去支付</button></view>
		</template>
	</view>
</template>

<script setup>
	import { ref } from 'vue'
	import { onLoad, onShow, onUnload } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { orderMyDetail } from '@/api/order.js'
	import { imageUrl } from '@/api/url.js'
	const order = ref({}), loading = ref(false), failed = ref(false), invalidId = ref(false), loggedIn = ref(false)
	let orderId = 0, disposed = false, version = 0, ownerToken = ''
	const goLogin = () => uni.navigateTo({ url: '/pages/login/login' })
	const load = async () => {
		if (disposed || invalidId.value) return
		const token = uni.getStorageSync('member_token') || ''
		if (ownerToken !== token) { version += 1; loading.value = false; order.value = {}; ownerToken = token }
		loggedIn.value = Boolean(token)
		if (!token) { order.value = {}; return }
		if (loading.value) return
		const requestId = ++version
		loading.value = true; failed.value = false
		try {
			const res = await orderMyDetail({ id: orderId })
			if (disposed || requestId !== version || token !== uni.getStorageSync('member_token')) return
			order.value = res.data || {}
		} catch (error) { if (!disposed && requestId === version && token === uni.getStorageSync('member_token')) { failed.value = true; order.value = {} } }
		finally { if (!disposed && requestId === version) loading.value = false }
	}
	const goPayment = () => { if (ownerToken === uni.getStorageSync('member_token') && Number(order.value.status) === 1) uni.navigateTo({ url: `/pages/order/payment?id=${orderId}` }); else load() }
	onLoad((options = {}) => { const id = Number(options.id); if (!Number.isSafeInteger(id) || id <= 0) { invalidId.value = true; loggedIn.value = Boolean(uni.getStorageSync('member_token')); return }; orderId = id })
	onShow(load)
	onUnload(() => { disposed = true; version += 1 })
</script>

<style scoped>
	.my-order-detail-page { max-width: 700px; min-height: 100vh; margin: 0 auto; padding-bottom: calc(90px + env(safe-area-inset-bottom)); background: #f3f3f3; }
	.my-order-detail-status { display: flex; flex-direction: column; gap: 10px; padding: 24px 16px; color: #ffffff; background: #ee4442; font-size: 19px; }
	.my-order-detail-date { color: #ffe3e3; font-size: 12px; }
	.my-order-detail-section { margin-top: 10px; padding: 14px 16px; background: #ffffff; }
	.my-order-detail-section-title { display: block; margin-bottom: 12px; font-size: 13px; color: #999999; }
	.my-order-detail-address-name { display: block; margin-bottom: 8px; font-size: 14px; }
	.my-order-detail-muted { display: block; font-size: 12px; line-height: 20px; color: #999999; overflow-wrap: anywhere; }
	.my-order-detail-item { display: flex; align-items: center; gap: 14px; padding: 10px 0; }
	.my-order-detail-image { flex-shrink: 0; width: 78px; height: 78px; }
	.my-order-detail-image--empty { display: flex; align-items: center; justify-content: center; color: #aaaaaa; background: #f7f7f7; font-size: 11px; }
	.my-order-detail-info { flex: 1; min-width: 0; }
	.my-order-detail-name { display: block; margin-bottom: 5px; font-size: 14px; line-height: 20px; overflow-wrap: anywhere; }
	.my-order-detail-item-price { display: flex; justify-content: space-between; margin-top: 12px; font-size: 13px; }
	.my-order-detail-row { display: flex; justify-content: space-between; gap: 20px; padding: 13px 0; border-bottom: 1px solid #f5f5f5; font-size: 13px; line-height: 20px; }
	.my-order-detail-row:last-child { border: 0; }
	.my-order-detail-value { max-width: 70%; color: #999999; text-align: right; overflow-wrap: anywhere; }
	.my-order-detail-amount { color: #ee4442; font-size: 17px; }
	.my-order-detail-state { padding: 85px 20px; text-align: center; color: #999999; font-size: 13px; }
	.my-order-detail-state text { display: block; }
	.my-order-detail-retry { display: inline-block; margin-top: 18px; padding: 0 22px; border-radius: 18px; color: #ee4442; background: #ffffff; font-size: 12px; line-height: 34px; }
	.my-order-detail-footer { position: fixed; z-index: 20; bottom: 0; left: 0; right: 0; max-width: 700px; margin: auto; padding: 10px 16px calc(10px + env(safe-area-inset-bottom)); background: #ffffff; }
	.my-order-detail-pay { border-radius: 22px; color: #ffffff; background: #ee4442; font-size: 15px; line-height: 44px; }
	.my-order-detail-pay::after, .my-order-detail-retry::after { border: 0; }
	@media (max-width: 360px) { .my-order-detail-section { padding: 12px; } .my-order-detail-image { width: 64px; height: 64px; } .my-order-detail-row { gap: 10px; font-size: 12px; } }
</style>
