<template>
	<view class="payment-page">
		<nav-header title="支付订单" />
		<view v-if="loading && !order.id" class="payment-state">正在加载订单…</view>
		<view v-else-if="loadFailed || !order.id" class="payment-state">
			<text>{{ invalidId ? '订单信息无效' : '订单暂时未能加载' }}</text>
			<button v-if="!invalidId" class="payment-retry" :disabled="loading" @click="loadOrder">重新加载</button>
		</view>
		<template v-else>
			<view class="payment-notice">当前为支付演示，选择方式后仅弹窗提示，不会发起真实扣款。</view>
			<view class="payment-section">
				<view class="payment-summary-row"><text>订单编号</text><text class="payment-summary-value">{{ order.order_no }}</text></view>
				<view class="payment-summary-row"><text>订单状态</text><text class="payment-summary-value">{{ order.status_name }}</text></view>
				<view class="payment-summary-row"><text>应付金额</text><text class="payment-amount">¥{{ order.order_amount_text || '0.00' }}</text></view>
			</view>
			<view class="payment-section payment-methods">
				<text class="payment-heading">选择支付方式</text>
				<view
					v-for="method in methods"
					:key="method.code"
					class="payment-method"
					role="radio"
					:aria-label="method.name"
					:aria-checked="selectedCode === method.code"
					@click="selectedCode = method.code"
				>
					<view class="payment-method-icon" :style="{ backgroundColor: method.color || '#538acb' }">{{ method.short_name || method.name.slice(0, 1) }}</view>
					<text class="payment-method-name">{{ method.name }}</text>
					<view class="payment-radio" :class="{ 'payment-radio--selected': selectedCode === method.code }"><text v-if="selectedCode === method.code">✓</text></view>
				</view>
				<view v-if="!methods.length" class="payment-state">暂无支付方式</view>
			</view>
			<text class="payment-placeholder-note">支付接入后，以支付平台和服务端确认的结果为准。</text>
		</template>
		<view class="payment-footer"><button class="payment-submit" :disabled="loading || loadFailed || !selectedMethod || Number(order.status) !== 1" @click="showPayment">{{ order.id && Number(order.status) !== 1 ? '当前订单不可支付' : '去支付' }}</button></view>
	</view>
</template>

<script setup>
	import { computed, ref } from 'vue'
	import { onLoad, onShow, onUnload } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { orderMyDetail } from '@/api/order.js'

	const order = ref({})
	const loading = ref(false)
	const loadFailed = ref(false)
	const invalidId = ref(false)
	const selectedCode = ref('')
	const methods = computed(() => Array.isArray(order.value.payment_methods) ? order.value.payment_methods : [])
	const selectedMethod = computed(() => methods.value.find((method) => method.code === selectedCode.value))
	let orderId = 0
	let disposed = false
	let requestVersion = 0
	let showingDialog = false

	const loadOrder = async () => {
		if (!orderId || disposed || loading.value) return
		const version = ++requestVersion
		const token = uni.getStorageSync('member_token')
		loading.value = true
		loadFailed.value = false
		try {
			const res = await orderMyDetail({ id: orderId })
			if (disposed || version !== requestVersion || token !== uni.getStorageSync('member_token')) return
			order.value = res.data || {}
			if (!methods.value.some((method) => method.code === selectedCode.value)) {
				const initial = methods.value.find((method) => method.code === 'wechat') || methods.value[0]
				selectedCode.value = initial ? initial.code : ''
			}
		} catch (error) {
			if (!disposed && version === requestVersion) loadFailed.value = true
		} finally {
			if (!disposed && version === requestVersion) loading.value = false
		}
	}
	const showPayment = () => {
		if (showingDialog || !selectedMethod.value || Number(order.value.status) !== 1) return
		showingDialog = true
		uni.showModal({
			title: '支付方式',
			content: `你选择了${selectedMethod.value.name}。当前为演示占位，未发起真实付款。`,
			showCancel: false,
			confirmColor: '#ee4442',
			complete: () => { showingDialog = false }
		})
	}
	onLoad((options = {}) => {
		const id = Number(options.id)
		if (!Number.isSafeInteger(id) || id <= 0) { invalidId.value = true; return }
		orderId = id
	})
	onShow(loadOrder)
	onUnload(() => { disposed = true; requestVersion += 1 })
</script>

<style scoped>
	.payment-page { max-width: 700px; min-height: 100vh; margin: 0 auto; padding-bottom: calc(76px + env(safe-area-inset-bottom)); background: #f4f4f4; color: #333333; }
	.payment-notice { padding: 12px 16px; background: #fffbe8; color: #9a782e; font-size: 12px; line-height: 20px; }
	.payment-section { margin-top: 10px; padding: 0 16px; background: #ffffff; }
	.payment-summary-row { min-height: 46px; padding: 12px 0; display: flex; align-items: center; justify-content: space-between; gap: 15px; border-bottom: 1px solid #f2f2f2; font-size: 14px; }
	.payment-summary-row:last-child { border-bottom: 0; }
	.payment-summary-value { min-width: 0; text-align: right; color: #999999; font-size: 13px; word-break: break-all; }
	.payment-amount { color: #ff343f; font-size: 18px; }
	.payment-heading { display: block; padding: 18px 0 8px; font-size: 14px; }
	.payment-method { display: flex; align-items: center; gap: 12px; min-height: 62px; padding: 12px 0; border-bottom: 1px solid #f2f2f2; }
	.payment-method:last-child { border-bottom: 0; }
	.payment-method-icon { width: 38px; height: 32px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; padding: 2px; border-radius: 6px; color: #ffffff; font-size: 10px; font-weight: 600; }
	.payment-method-name { flex: 1; min-width: 0; font-size: 15px; line-height: 21px; word-break: break-word; }
	.payment-radio { width: 20px; height: 20px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border: 1px solid #d4d4d4; border-radius: 50%; }
	.payment-radio--selected { background: #19ad55; border-color: #19ad55; color: #ffffff; font-size: 13px; }
	.payment-placeholder-note { display: block; padding: 20px 16px; color: #aaaaaa; text-align: center; font-size: 11px; line-height: 18px; }
	.payment-state { padding: 70px 20px; color: #999999; text-align: center; font-size: 13px; line-height: 22px; }
	.payment-state text { display: block; }
	.payment-retry { display: inline-block; margin-top: 15px; padding: 0 22px; border: 1px solid #ee4442; border-radius: 18px; background: #ffffff; color: #ee4442; font-size: 12px; line-height: 32px; }
	.payment-retry::after, .payment-submit::after { border: 0; }
	.payment-footer { position: fixed; z-index: 20; bottom: 0; left: 0; right: 0; max-width: 700px; margin: 0 auto; padding-bottom: env(safe-area-inset-bottom); background: #ffffff; }
	.payment-submit { height: 50px; line-height: 50px; margin: 0; padding: 0 16px; border-radius: 0; color: #ffffff; background: #09bb63; font-size: 15px; }
	.payment-submit[disabled] { color: #ffffff; background: #9cd8bb; }
</style>
