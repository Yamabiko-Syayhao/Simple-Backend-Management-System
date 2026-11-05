<template>
	<view class="confirm-page">
		<nav-header title="确认订单" />
		<view v-if="!loggedIn || sessionChanged" class="confirm-state">
			<text>{{ sessionChanged ? '登录账号已变化，请返回重新结算' : '请先登录后确认订单' }}</text>
			<button class="confirm-retry" @click="goLogin">去登录</button>
		</view>
		<view v-else-if="routeError" class="confirm-state">{{ routeError }}</view>
		<view v-else-if="loading && !items.length" class="confirm-state">正在核对商品和优惠…</view>
		<template v-else>
			<view v-if="pendingSubmission" class="confirm-notice">订单提交结果待确认，请重试确认。系统会按同一请求处理，避免重复下单。</view>
			<view v-if="quoteError" class="confirm-state confirm-state--compact">
				<text>订单信息暂时未能确认</text>
				<button class="confirm-retry" :disabled="loading" @click="refreshQuote">重新计算</button>
				<button v-if="selectedCouponId" class="confirm-retry" :disabled="loading" @click="clearCoupon">不使用当前优惠券</button>
			</view>
			<view class="confirm-section confirm-address" role="button" aria-label="选择收货地址" @click="chooseAddress">
				<view class="confirm-address-title"><text>收货地址</text><text class="confirm-arrow">›</text></view>
				<template v-if="quote.address">
					<text class="confirm-receiver">{{ quote.address.receiver_name }} {{ quote.address.mobile }}</text>
					<text class="confirm-address-detail">{{ quote.address.region }} {{ quote.address.detail }}</text>
				</template>
				<text v-else class="confirm-address-empty">请选择或添加收货地址</text>
			</view>
			<view class="confirm-section confirm-coupon" role="button" aria-label="选择优惠券" @click="chooseCoupons">
				<text>优惠券</text><view class="confirm-coupon-value"><text :class="{ 'confirm-money': hasDiscount }">{{ couponLabel }}</text><text class="confirm-arrow">›</text></view>
			</view>
			<view class="confirm-section">
				<view v-for="item in items" :key="item.product_id" class="confirm-item">
					<image v-if="item.image" class="confirm-item-image" :src="imageUrl(item.image)" mode="aspectFit" />
					<view v-else class="confirm-item-image confirm-image-empty">暂无图片</view>
					<view class="confirm-item-main">
						<text class="confirm-item-name">{{ item.name }}</text>
						<text class="confirm-item-spec">{{ item.specification || '标准' }}</text>
						<view class="confirm-item-bottom"><text>¥{{ item.price_text || money(item.price) }}</text><text class="confirm-item-quantity">×{{ item.quantity }}</text></view>
					</view>
				</view>
				<view class="confirm-amount-row"><text>商品金额</text><text class="confirm-money">¥{{ quote.goods_amount_text || '0.00' }}</text></view>
				<view class="confirm-amount-row"><text>邮费</text><text class="confirm-money">¥{{ quote.freight_amount_text || '0.00' }}</text></view>
				<text v-if="quote.freight_rule" class="confirm-freight-rule">{{ quote.freight_rule }}</text>
				<view class="confirm-amount-row"><text>优惠券</text><text class="confirm-money">-¥{{ quote.discount_amount_text || '0.00' }}</text></view>
				<view class="confirm-message-row"><text>订单备注</text><input v-model="userMessage" class="confirm-message" :disabled="submitting || pendingSubmission || Boolean(createdOrderId)" maxlength="500" placeholder="请输入备注（选填）" /></view>
			</view>
		</template>
		<view v-if="loggedIn && !sessionChanged && !routeError" class="confirm-footer">
			<view class="confirm-footer-total"><text>总计：</text><text class="confirm-total">¥{{ quote.order_amount_text || '0.00' }}</text></view>
			<button class="confirm-submit" :loading="submitting" :disabled="loading || submitting || (!createdOrderId && (!quote.quote_token || !quote.address || quoteError))" @click="submitOrder">{{ createdOrderId ? '查看支付方式' : pendingSubmission ? '确认提交结果' : '提交订单' }}</button>
		</view>
	</view>
</template>

<script setup>
	import { computed, ref } from 'vue'
	import { onHide, onLoad, onShow, onUnload } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { orderPreview, orderSubmit } from '@/api/order.js'
	import { imageUrl } from '@/api/url.js'

	const quote = ref({ items: [] })
	const userMessage = ref('')
	const loading = ref(false)
	const submitting = ref(false)
	const quoteError = ref(false)
	const routeError = ref('')
	const loggedIn = ref(false)
	const sessionChanged = ref(false)
	const selectedAddressId = ref(0)
	const selectedCouponId = ref(0)
	const pendingSubmission = ref(false)
	const createdOrderId = ref(0)
	const items = computed(() => Array.isArray(quote.value.items) ? quote.value.items : [])
	const hasDiscount = computed(() => Number(quote.value.discount_amount || 0) > 0)
	const couponLabel = computed(() => {
		if (quote.value.coupon_user_id) return `-¥${quote.value.discount_amount_text || '0.00'}`
		const available = (quote.value.coupons || []).filter((item) => item.available).length
		return available ? `${available}张可用优惠券` : '暂无可用优惠券'
	})
	let sourceData = null
	let requestKey = ''
	let cacheKey = ''
	let ownerToken = ''
	let disposed = false
	let visible = false
	let requestVersion = 0

	const positiveId = (value) => { const id = Number(value); return Number.isSafeInteger(id) && id > 0 ? id : 0 }
	const money = (value) => Number(value || 0).toFixed(2)
	const sameSession = () => ownerToken && ownerToken === uni.getStorageSync('member_token')
	const clearCache = () => { try { if (cacheKey) uni.removeStorageSync(cacheKey) } catch (error) { /* 缓存不可用不影响服务端幂等 */ } }
	const savePending = () => {
		try { uni.setStorageSync(cacheKey, { request_key: requestKey, quote: quote.value, user_message: userMessage.value, resolved_order_id: createdOrderId.value }) } catch (error) { /* 本页仍保留相同请求号 */ }
	}
	const newRequestKey = () => `c${Date.now().toString(36)}${Array.from({ length: 3 }, () => Math.random().toString(36).slice(2, 12)).join('')}`
	const hashKey = (value) => {
		let hash = 2166136261
		for (const ch of value) hash = Math.imul(hash ^ ch.charCodeAt(0), 16777619)
		return (hash >>> 0).toString(36)
	}
	const decode = (value) => { try { return decodeURIComponent(value || '') } catch (error) { return '' } }
	const readSource = (options) => {
		if (options.source === 'cart') {
			const parts = decode(options.cart_ids).split(',').filter(Boolean)
			const ids = parts.map(positiveId)
			if (!ids.length || ids.some((id) => !id) || ids.length > 1000) return null
			return { source: 'cart', cart_ids: [...new Set(ids)].sort((a, b) => a - b) }
		}
		if (options.source === 'buy_now') {
			const goodsId = positiveId(options.goods_id), productId = positiveId(options.product_id)
			const quantity = Number(options.quantity)
			if (!goodsId || !productId || !Number.isInteger(quantity) || quantity < 1 || quantity > 999) return null
			return { source: 'buy_now', goods_id: goodsId, product_id: productId, quantity }
		}
		return null
	}
	const refreshQuote = async () => {
		if (disposed || !sourceData || !sameSession() || pendingSubmission.value || submitting.value || createdOrderId.value) return
		const version = ++requestVersion
		loading.value = true
		quoteError.value = false
		try {
			const res = await orderPreview({ ...sourceData, address_id: selectedAddressId.value || undefined, coupon_user_id: selectedCouponId.value || undefined })
			if (disposed || version !== requestVersion || !sameSession()) return
			quote.value = res.data || { items: [] }
			selectedAddressId.value = positiveId(quote.value.address && quote.value.address.id)
			selectedCouponId.value = positiveId(quote.value.coupon_user_id)
		} catch (error) {
			if (!disposed && version === requestVersion) quoteError.value = true
		} finally {
			if (!disposed && version === requestVersion) loading.value = false
		}
	}
	const chooseAddress = () => {
		if (loading.value || submitting.value || pendingSubmission.value || createdOrderId.value) return
		uni.navigateTo({ url: `/pages/address/index?select=1&selected_id=${selectedAddressId.value}` })
	}
	const chooseCoupons = () => {
		if (loading.value || submitting.value || pendingSubmission.value || createdOrderId.value || !quote.value.quote_token) return
		uni.navigateTo({ url: `/pages/order/coupons?quote_token=${encodeURIComponent(quote.value.quote_token)}&selected_id=${selectedCouponId.value}` })
	}
	const onAddressSelected = (data) => {
		if (disposed || pendingSubmission.value || createdOrderId.value) return
		selectedAddressId.value = positiveId(data && data.id)
		if (visible) refreshQuote()
	}
	const onAddressChange = () => {
		// 地址可能被编辑或删除；允许服务端重新选择有效的默认地址。
		selectedAddressId.value = 0
		if (visible) refreshQuote()
	}
	const onCouponSelected = (data) => {
		if (disposed || pendingSubmission.value || createdOrderId.value) return
		selectedCouponId.value = positiveId(data && data.id)
		if (visible) refreshQuote()
	}
	const clearCoupon = () => { selectedCouponId.value = 0; refreshQuote() }
	const goLogin = () => uni.navigateTo({ url: '/pages/login/login' })
	const openPayment = () => {
		uni.redirectTo({ url: `/pages/order/payment?id=${createdOrderId.value}`, success: clearCache })
	}
	const submitOrder = async () => {
		if (submitting.value || loading.value || disposed || !sameSession()) return
		if (createdOrderId.value) { openPayment(); return }
		if (!quote.value.quote_token || !quote.value.address || quoteError.value) return
		submitting.value = true
		pendingSubmission.value = true
		savePending()
		try {
			const res = await orderSubmit({ quote_token: quote.value.quote_token, request_key: requestKey, user_message: userMessage.value })
			if (disposed || !sameSession()) return
			const id = positiveId(res.data && res.data.id)
			if (!id) throw new Error('missing order id')
			createdOrderId.value = id
			pendingSubmission.value = false
			savePending()
			uni.$emit('cart:change')
			uni.$emit('coupon:change')
			openPayment()
		} catch (error) {
			if (disposed || !sameSession()) return
			if (error && typeof error.code === 'number') {
				// 已明确失败的校验可重新报价；网络异常保持同一请求号确认结果。
				pendingSubmission.value = false
				clearCache()
				quoteError.value = true
			} else {
				uni.showToast({ title: '请重试确认订单提交结果', icon: 'none' })
			}
		} finally { submitting.value = false }
	}

	onLoad((options = {}) => {
		sourceData = readSource(options)
		if (!sourceData) { routeError.value = '结算商品信息无效，请返回重新选择'; return }
		ownerToken = uni.getStorageSync('member_token') || ''
		requestKey = newRequestKey()
		cacheKey = `checkout_pending_${hashKey(ownerToken + JSON.stringify(sourceData))}`
		try {
			const cached = uni.getStorageSync(cacheKey)
			if (cached && typeof cached.request_key === 'string' && cached.quote && cached.quote.quote_token) {
				requestKey = cached.request_key
				quote.value = cached.quote
				userMessage.value = cached.user_message || ''
				createdOrderId.value = positiveId(cached.resolved_order_id)
				pendingSubmission.value = !createdOrderId.value
			}
		} catch (error) { /* 无缓存时重新向服务端报价 */ }
		uni.$on('address:selected', onAddressSelected)
		uni.$on('address:change', onAddressChange)
		uni.$on('checkout:coupon:selected', onCouponSelected)
	})
	onShow(() => {
		visible = true
		const token = uni.getStorageSync('member_token') || ''
		loggedIn.value = Boolean(token)
		if (ownerToken && token && token !== ownerToken) { sessionChanged.value = true; return }
		refreshQuote()
	})
	onHide(() => { visible = false })
	onUnload(() => {
		disposed = true
		requestVersion += 1
		uni.$off('address:selected', onAddressSelected)
		uni.$off('address:change', onAddressChange)
		uni.$off('checkout:coupon:selected', onCouponSelected)
	})
</script>

<style scoped>
	.confirm-page { min-height: 100vh; max-width: 700px; margin: 0 auto; padding-bottom: calc(80px + env(safe-area-inset-bottom)); background: #f4f4f4; color: #333333; }
	.confirm-state { padding: 70px 20px; color: #999999; font-size: 13px; text-align: center; line-height: 22px; }
	.confirm-state--compact { padding: 20px; }
	.confirm-state text { display: block; }
	.confirm-retry { display: inline-block; margin: 15px 4px 0; padding: 0 18px; border: 1px solid #ee4442; border-radius: 18px; color: #ee4442; background: #ffffff; line-height: 32px; font-size: 12px; }
	.confirm-retry::after, .confirm-submit::after { border: 0; }
	.confirm-notice { padding: 12px 16px; background: #fff9df; color: #a07320; font-size: 12px; line-height: 20px; }
	.confirm-section { margin-top: 10px; padding: 0 16px; background: #ffffff; }
	.confirm-address { margin-top: 0; padding-top: 15px; padding-bottom: 17px; }
	.confirm-address-title, .confirm-amount-row, .confirm-message-row, .confirm-coupon, .confirm-item-bottom { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
	.confirm-address-title { font-size: 14px; margin-bottom: 7px; }
	.confirm-arrow { color: #aaaaaa; font-size: 23px; line-height: 20px; }
	.confirm-receiver, .confirm-address-detail { display: block; margin-top: 4px; color: #888888; font-size: 12px; line-height: 19px; word-break: break-word; }
	.confirm-address-empty { color: #ee4442; font-size: 13px; }
	.confirm-coupon { min-height: 47px; font-size: 14px; }
	.confirm-coupon-value { display: flex; align-items: center; gap: 6px; color: #999999; font-size: 13px; }
	.confirm-item { display: flex; padding: 17px 0; gap: 14px; }
	.confirm-item-image { width: 84px; height: 84px; flex-shrink: 0; background: #fafafa; }
	.confirm-image-empty { display: flex; align-items: center; justify-content: center; color: #bbbbbb; font-size: 11px; }
	.confirm-item-main { flex: 1; min-width: 0; }
	.confirm-item-name { display: block; font-size: 14px; line-height: 20px; word-break: break-word; }
	.confirm-item-spec { display: inline-block; max-width: 100%; margin-top: 5px; padding: 1px 5px; border: 1px solid #dddddd; border-radius: 3px; color: #999999; font-size: 11px; line-height: 17px; word-break: break-word; }
	.confirm-item-bottom { margin-top: 18px; font-size: 14px; }
	.confirm-item-quantity { color: #999999; font-size: 12px; }
	.confirm-amount-row { min-height: 45px; padding: 10px 0; border-bottom: 1px solid #f2f2f2; font-size: 14px; }
	.confirm-money { color: #ff343f; }
	.confirm-freight-rule { display: block; padding: 8px 0; color: #aaaaaa; font-size: 11px; line-height: 17px; }
	.confirm-message-row { min-height: 47px; font-size: 14px; }
	.confirm-message { flex: 1; min-width: 0; height: 38px; font-size: 13px; }
	.confirm-footer { position: fixed; left: 0; right: 0; bottom: 0; z-index: 20; max-width: 700px; margin: 0 auto; display: flex; justify-content: flex-end; align-items: center; gap: 12px; padding: 8px 16px calc(8px + env(safe-area-inset-bottom)); background: #ffffff; border-top: 1px solid #eeeeee; }
	.confirm-footer-total { min-width: 0; font-size: 13px; }
	.confirm-total { color: #ff343f; font-size: 19px; word-break: break-all; }
	.confirm-submit { flex-shrink: 0; margin: 0; padding: 0 22px; height: 42px; line-height: 42px; border-radius: 23px; background: linear-gradient(90deg, #ff603c, #f20c32); color: #ffffff; font-size: 14px; }
	.confirm-submit[disabled] { color: #ffffff; background: #f4a3a8; }
	@media (max-width: 360px) { .confirm-section { padding-left: 12px; padding-right: 12px; } .confirm-footer { padding-left: 12px; padding-right: 12px; gap: 8px; } .confirm-submit { padding: 0 16px; } .confirm-total { font-size: 17px; } .confirm-item-image { width: 72px; height: 72px; } }
</style>
