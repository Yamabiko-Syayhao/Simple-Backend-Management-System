<template>
	<view class="goods-detail-page">
		<nav-header title="商品详情"></nav-header>
		<view v-if="loading" class="page-state">商品加载中…</view>
		<view v-else-if="!goods.id" class="page-state">
			<text>{{ loadError || '商品不存在或已被删除' }}</text>
			<button v-if="goodsId" class="retry-button" @click="loadGoods">重新加载</button>
		</view>
		<view v-else class="detail-body">
			<view class="gallery-wrap">
				<swiper v-if="gallery.length" class="gallery" :indicator-dots="gallery.length > 1" indicator-active-color="#e93b3b" indicator-color="#dddddd" :circular="gallery.length > 1" :autoplay="gallery.length > 1" :interval="4500" :duration="350">
					<swiper-item v-for="(src, index) in gallery" :key="src + index">
						<image class="gallery-image" :src="src" mode="aspectFit" @click="previewGallery(index)"></image>
					</swiper-item>
				</swiper>
				<view v-else class="gallery gallery-empty">暂无商品图片</view>
			</view>
			<view class="info-block">
				<view class="price-line">
					<text class="current-price">¥{{ formatPrice(displayPrice) }}</text>
					<text v-if="showMarket" class="market-price">¥{{ formatPrice(goods.market_price) }}</text>
				</view>
				<text class="goods-name">{{ goods.name }}</text>
				<text v-if="goods.brief" class="goods-brief">{{ goods.brief }}</text>
				<text v-if="unavailableReason" class="unavailable-tip">{{ unavailableReason }}</text>
			</view>
			<view class="row-list">
				<view class="detail-row" @click="openSpecifications">
					<text class="row-label">规格</text>
					<text class="row-value">{{ selectedProduct ? selectedProduct.specification : '请选择规格' }}</text>
					<text class="row-arrow">›</text>
				</view>
				<view class="detail-row" @click="activeSheet = 'attributes'">
					<text class="row-label">属性</text>
					<text class="row-value">商品参数</text>
					<text class="row-arrow">›</text>
				</view>
				<view class="detail-row">
					<text class="row-label">运费</text>
					<text class="row-value">以结算页面为准</text>
				</view>
			</view>
			<view class="description-block">
				<view class="description-title">商品详情</view>
				<view v-if="hasDetail" class="rich-content"><rich-text :nodes="detailHtml"></rich-text></view>
				<view v-else class="description-empty">暂无商品详情</view>
			</view>
		</view>

		<view class="detail-bar">
			<view class="cart-entry" @click="goCart">
				<view class="cart-icon-wrap">
					<image class="cart-icon" src="/static/icons/tab-cart.svg" mode="aspectFit"></image>
					<text v-if="cartQuantity" class="cart-badge">{{ cartQuantity > 99 ? '99+' : cartQuantity }}</text>
				</view>
				<text class="cart-label">购物车</text>
			</view>
			<view class="action-buttons">
				<button class="action-button action-cart" :disabled="!canAddAny || adding" @click="openSpecifications">加入购物车</button>
				<button class="action-button action-buy" :disabled="!canAddAny || adding" @click="onBuy">立即购买</button>
			</view>
		</view>

		<view v-if="activeSheet" class="popup-layer">
			<view class="popup-mask" @click="closeSheet" @touchmove.stop.prevent></view>
			<view v-if="activeSheet === 'specifications'" class="popup-panel specification-panel">
				<view class="sku-summary">
					<image v-if="selectedImage" class="sku-image" :src="selectedImage" mode="aspectFit"></image>
					<view v-else class="sku-image sku-image-empty">暂无图片</view>
					<view class="sku-summary-text">
						<text class="sku-price">¥{{ formatPrice(displayPrice) }}</text>
						<text class="sku-summary-line">{{ selectedProduct ? '已选 ' + selectedProduct.specification : '请选择商品规格' }}</text>
						<text class="sku-stock">{{ selectedProduct ? '库存 ' + selectedStock + (goods.unit || '件') : '' }}</text>
					</view>
					<view class="sheet-close" @click="closeSheet">×</view>
				</view>
				<scroll-view class="specification-scroll" scroll-y @touchmove.stop>
					<view class="specification-section">
						<text class="section-label">{{ specificationName }}</text>
						<view v-if="products.length" class="specification-options">
							<view v-for="item in products" :key="item.id" class="specification-option" :class="{ 'option-selected': selectedProductId === item.id, 'option-disabled': !productAvailable(item) }" @click="selectProduct(item)">
								<text>{{ item.specification || '标准' }}</text><text v-if="!productAvailable(item)" class="sold-out-label">（无货）</text>
							</view>
						</view>
						<view v-else class="specification-empty">暂无可购买的规格</view>
					</view>
					<view class="quantity-row">
						<text class="section-label">购买数量</text>
						<view class="quantity-stepper">
							<button class="quantity-button" :disabled="quantity <= 1 || adding" @click="changeQuantity(-1)">−</button>
							<input :key="quantityInputKey" class="quantity-input" type="number" :value="quantity" :disabled="!selectedProduct || !selectedStock || adding" :maxlength="3" @blur="onQuantityInput" @confirm="onQuantityInput" />
							<button class="quantity-button" :disabled="!selectedProduct || quantity >= quantityLimit || adding" @click="changeQuantity(1)">＋</button>
						</view>
					</view>
					<text v-if="unavailableReason" class="sheet-status">{{ unavailableReason }}</text>
				</scroll-view>
				<view class="sheet-actions">
					<button class="action-button action-cart" :loading="adding" :disabled="!canAddSelected || adding" @click="addToCart">{{ adding ? '加入中' : '加入购物车' }}</button>
					<button class="action-button action-buy" :disabled="!canAddSelected || adding" @click="onBuy">立即购买</button>
				</view>
			</view>
			<view v-else class="popup-panel attributes-panel">
				<view class="sheet-title">商品属性<view class="sheet-close" @click="closeSheet">×</view></view>
				<scroll-view class="attributes-scroll" scroll-y @touchmove.stop>
					<view v-for="(item, index) in attributes" :key="index" class="attribute-row">
						<text class="attribute-name">{{ item.name }}</text>
						<text class="attribute-value">{{ item.value }}</text>
					</view>
					<view v-if="!attributes.length" class="description-empty">暂无商品参数</view>
				</scroll-view>
			</view>
		</view>
	</view>
</template>

<script setup>
	import { computed, onUnmounted, ref } from 'vue'
	import { onLoad, onShow } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { goodsClientDetail } from '@/api/goods.js'
	import { cartAdd, cartCount } from '@/api/cart.js'
	import { imageUrl, rewriteHtmlImages } from '@/api/url.js'

	const goodsId = ref(0)
	const goods = ref({})
	const loading = ref(true)
	const loadError = ref('')
	const activeSheet = ref('')
	const selectedProductId = ref(0)
	const quantity = ref(1)
	const quantityInputKey = ref(0)
	const cartQuantity = ref(0)
	const adding = ref(false)
	let pageAlive = true
	let navigatingToLogin = false
	let navigatingToCheckout = false
	let countRequestId = 0

	const products = computed(() => Array.isArray(goods.value.products) ? goods.value.products : [])
	const attributes = computed(() => Array.isArray(goods.value.attributes) ? goods.value.attributes : [])
	const selectedProduct = computed(() => products.value.find((item) => item.id === selectedProductId.value) || null)
	const selectedStock = computed(() => Math.max(0, Number(selectedProduct.value && selectedProduct.value.quantity) || 0))
	const quantityLimit = computed(() => Math.min(999, selectedStock.value))
	const displayPrice = computed(() => selectedProduct.value ? selectedProduct.value.price : goods.value.retail_price)
	const showMarket = computed(() => Number(goods.value.market_price || 0) > Number(displayPrice.value || 0))
	const gallery = computed(() => {
		const urls = Array.isArray(goods.value.gallery) ? goods.value.gallery.filter((src) => typeof src === 'string' && src.trim()) : []
		return [...new Set((urls.length ? urls : [goods.value.image]).filter(Boolean).map(imageUrl))]
	})
	const selectedImage = computed(() => {
		const product = selectedProduct.value
		const specification = (goods.value.specifications || []).find((item) => product && item.value === product.specification)
		return imageUrl((product && product.image) || (specification && specification.image) || goods.value.image) || gallery.value[0] || ''
	})
	const specificationName = computed(() => {
		const names = [...new Set((goods.value.specifications || []).map((item) => item.name).filter(Boolean))]
		return names.length === 1 ? names[0] : '规格'
	})
	const canAddAny = computed(() => Boolean(goods.value.is_on_sale) && goods.value.cart_available !== false && products.value.some(productAvailable))
	const canAddSelected = computed(() => canAddAny.value && selectedProduct.value && selectedStock.value > 0)
	const unavailableReason = computed(() => {
		if (!goods.value.id) return ''
		if (!goods.value.is_on_sale) return '商品暂未上架，暂时无法加入购物车'
		if (!products.value.length || !products.value.some(productAvailable)) return '商品暂时缺货'
		if (selectedProduct.value && !selectedStock.value) return '所选规格暂时缺货，请选择其他规格'
		return ''
	})
	const detailHtml = computed(() => {
		// rich-text 负责富文本渲染；这里仅补图片域名并适配手机宽度。
		return rewriteHtmlImages(goods.value.detail).replace(/<img\b[^>]*>/gi, (tag) => {
			const cleanTag = tag.replace(/\sstyle\s*=\s*(["'])[\s\S]*?\1/gi, '')
			return cleanTag.replace(/\s*\/?>$/, ' style="max-width:100%;height:auto;display:block;" />')
		})
	})
	const hasDetail = computed(() => Boolean(detailHtml.value.replace(/<[^>]*>/g, '').replace(/&nbsp;|\s/g, '')) || /<(img|video|audio|table|hr)\b/i.test(detailHtml.value))

	function productAvailable(item) {
		return Number(item.quantity) > 0
	}
	function formatPrice(value) {
		return Number(value || 0).toFixed(2)
	}
	function normalizeQuantity(value) {
		const parsed = Number(value)
		return Math.min(Math.max(1, quantityLimit.value), Number.isFinite(parsed) ? Math.max(1, Math.floor(parsed)) : 1)
	}
	function changeQuantity(delta) {
		if (adding.value) return
		quantity.value = normalizeQuantity(quantity.value + delta)
	}
	function onQuantityInput(event) {
		quantity.value = normalizeQuantity(event.detail.value)
		// 同值也重新同步输入框，避免空串或越界值停留在界面上。
		quantityInputKey.value += 1
	}
	function selectProduct(item) {
		if (adding.value || !productAvailable(item)) return
		selectedProductId.value = item.id
		quantity.value = normalizeQuantity(quantity.value)
		quantityInputKey.value += 1
	}
	function closeSheet() {
		if (!adding.value) activeSheet.value = ''
	}
	function openSpecifications() {
		if (goods.value.id) activeSheet.value = 'specifications'
	}
	function previewGallery(index) {
		uni.previewImage({ current: gallery.value[index], urls: gallery.value })
	}
	function goCart() {
		if (!ensureLogin()) return
		activeSheet.value = ''
		uni.navigateTo({ url: '/pages/cart/index' })
	}
	function ensureLogin() {
		if (uni.getStorageSync('member_token')) return true
		if (navigatingToLogin) return false
		navigatingToLogin = true
		uni.showToast({ title: '请先登录后再操作', icon: 'none' })
		setTimeout(() => {
			if (pageAlive) uni.navigateTo({ url: '/pages/login/login' })
			navigatingToLogin = false
		}, 500)
		return false
	}
	async function loadCartCount() {
		const requestId = ++countRequestId
		const token = uni.getStorageSync('member_token')
		if (!token) {
			cartQuantity.value = 0
			return
		}
		try {
			const res = await cartCount()
			if (pageAlive && requestId === countRequestId && token === uni.getStorageSync('member_token')) {
				cartQuantity.value = Number(res.data && res.data.count) || 0
			}
		} catch (error) {
			// 请求层统一提示；角标失败不影响商品详情。
		}
	}
	async function loadGoods() {
		if (!goodsId.value) return
		loading.value = true
		loadError.value = ''
		try {
			const res = await goodsClientDetail({ id: goodsId.value })
			if (!pageAlive) return
			goods.value = res.data || {}
			selectedProductId.value = products.value.length === 1 ? products.value[0].id : 0
			quantity.value = 1
		} catch (error) {
			if (pageAlive) {
				goods.value = {}
				loadError.value = error && error.msg || '商品加载失败，请重试'
			}
		} finally {
			if (pageAlive) loading.value = false
		}
	}
	async function addToCart() {
		if (adding.value || !ensureLogin()) return
		if (!selectedProduct.value) {
			uni.showToast({ title: '请选择商品规格', icon: 'none' })
			return
		}
		if (!canAddSelected.value) {
			uni.showToast({ title: unavailableReason.value || '该规格暂时无法购买', icon: 'none' })
			return
		}
		quantity.value = normalizeQuantity(quantity.value)
		adding.value = true
		try {
			await cartAdd({ goods_id: goods.value.id, product_id: selectedProduct.value.id, quantity: quantity.value })
			if (!pageAlive) return
			activeSheet.value = ''
			uni.showToast({ title: '已加入购物车', icon: 'success' })
			uni.$emit('cart:change')
		} catch (error) {
			// 库存及已有购物车数量由服务端校验，失败提示由请求层显示。
		} finally {
			adding.value = false
		}
	}
	function onBuy() {
		if (adding.value || navigatingToCheckout || !ensureLogin()) return
		// 首次点击先确认规格及数量，标准规格也经过同一个确认步骤。
		if (activeSheet.value !== 'specifications') {
			activeSheet.value = 'specifications'
			return
		}
		if (!selectedProduct.value) {
			uni.showToast({ title: '请选择商品规格', icon: 'none' })
			return
		}
		if (!canAddSelected.value) return
		quantity.value = normalizeQuantity(quantity.value)
		navigatingToCheckout = true
		uni.navigateTo({
			url: `/pages/order/confirm?source=buy_now&goods_id=${goods.value.id}&product_id=${selectedProduct.value.id}&quantity=${quantity.value}`,
			success: () => { activeSheet.value = '' },
			complete: () => { navigatingToCheckout = false }
		})
	}
	onLoad((options) => {
		const id = Number(options && options.id)
		if (!Number.isSafeInteger(id) || id <= 0) {
			loading.value = false
			return
		}
		goodsId.value = id
		loadGoods()
	})
	onShow(loadCartCount)
	uni.$on('cart:change', loadCartCount)
	onUnmounted(() => {
		pageAlive = false
		uni.$off('cart:change', loadCartCount)
	})
</script>

<style scoped>
	.goods-detail-page { max-width: 700px; min-height: 100vh; margin: 0 auto; padding-bottom: calc(74px + env(safe-area-inset-bottom)); background: #f4f4f4; }
	.gallery-wrap { background: #ffffff; }
	.gallery { width: 100%; height: 100vw; max-height: 700px; }
	.gallery-image { display: block; width: 100%; height: 100%; }
	.gallery-empty { display: flex; align-items: center; justify-content: center; color: #aaaaaa; font-size: 13px; }
	.info-block { padding: 14px 16px 18px; background: #ffffff; }
	.price-line { display: flex; align-items: baseline; gap: 10px; }
	.current-price, .sku-price { color: #ff343f; font-size: 23px; line-height: 32px; }
	.market-price { font-size: 12px; color: #999999; text-decoration: line-through; }
	.goods-name { display: block; margin-top: 4px; font-size: 16px; color: #333333; line-height: 24px; overflow-wrap: anywhere; }
	.goods-brief { display: block; margin-top: 6px; font-size: 13px; color: #999999; line-height: 20px; overflow-wrap: anywhere; }
	.unavailable-tip { display: block; margin-top: 12px; font-size: 12px; color: #d37625; line-height: 20px; }
	.row-list { margin-top: 12px; padding: 0 16px; background: #ffffff; }
	.detail-row { display: flex; align-items: center; min-height: 46px; padding: 12px 0; border-bottom: 1px solid #f4f4f4; }
	.detail-row:last-child { border-bottom: 0; }
	.row-label { flex-shrink: 0; font-size: 14px; color: #333333; }
	.row-value { flex: 1; min-width: 0; margin-left: 18px; text-align: right; font-size: 13px; color: #999999; overflow-wrap: anywhere; }
	.row-arrow { margin-left: 7px; color: #aaaaaa; font-size: 23px; line-height: 16px; }
	.description-block { margin-top: 12px; background: #ffffff; }
	.description-title { padding: 14px 0; border-bottom: 1px solid #f2f2f2; text-align: center; font-size: 14px; }
	.rich-content { padding: 10px; overflow-x: auto; overflow-wrap: anywhere; line-height: 1.7; font-size: 14px; }
	.description-empty { padding: 32px 16px; text-align: center; font-size: 13px; color: #999999; }
	.page-state { padding: 100px 20px; text-align: center; line-height: 24px; font-size: 14px; color: #999999; }
	.retry-button { width: 110px; margin-top: 18px; border: 1px solid #e93b3b; border-radius: 18px; font-size: 13px; color: #e93b3b; line-height: 32px; background: #ffffff; }
	.detail-bar { position: fixed; z-index: 20; left: 0; right: 0; bottom: 0; max-width: 700px; margin: 0 auto; display: flex; align-items: center; padding: 8px 12px calc(8px + env(safe-area-inset-bottom)); border-top: 1px solid #f0f0f0; background: #ffffff; box-sizing: border-box; }
	.cart-entry { display: flex; flex-shrink: 0; align-items: center; justify-content: center; flex-direction: column; width: 54px; margin-right: 12px; }
	.cart-icon-wrap { position: relative; height: 25px; }
	.cart-icon { display: block; width: 23px; height: 23px; }
	.cart-label { font-size: 10px; color: #666666; line-height: 14px; }
	.cart-badge { position: absolute; right: -14px; top: -5px; min-width: 15px; padding: 0 3px; border: 1px solid #ffffff; border-radius: 10px; background: #f53343; color: #ffffff; text-align: center; line-height: 15px; font-size: 10px; }
	.action-buttons { display: flex; flex: 1; min-width: 0; }
	.action-button { flex: 1; min-width: 0; height: 42px; margin: 0; padding: 0 8px; border: 0; line-height: 42px; text-align: center; font-size: 14px; color: #ffffff; border-radius: 0; }
	.action-button::after, .quantity-button::after, .retry-button::after { border: 0; }
	.action-cart { border-radius: 23px 0 0 23px; background: linear-gradient(90deg, #ffd421, #ff9314); }
	.action-buy { border-radius: 0 23px 23px 0; background: linear-gradient(90deg, #ff613b, #f20c32); }
	.action-button[disabled] { color: #ffffff; opacity: 0.45; }
	.popup-layer { position: fixed; z-index: 1000; inset: 0; }
	.popup-mask { position: absolute; inset: 0; background: rgba(0, 0, 0, 0.62); }
	.popup-panel { position: absolute; bottom: 0; left: 0; right: 0; width: 100%; max-width: 700px; margin: 0 auto; box-sizing: border-box; border-radius: 18px 18px 0 0; background: #ffffff; overflow: hidden; }
	.specification-panel { display: flex; flex-direction: column; height: 72vh; min-height: 370px; max-height: 680px; }
	.sku-summary { position: relative; flex-shrink: 0; display: flex; align-items: center; padding: 22px 40px 18px 16px; border-bottom: 1px solid #f4f4f4; }
	.sku-image { flex-shrink: 0; width: 86px; height: 86px; margin-right: 15px; border-radius: 5px; background: #fafafa; }
	.sku-image-empty { display: flex; align-items: center; justify-content: center; color: #bbbbbb; font-size: 11px; }
	.sku-summary-text { flex: 1; min-width: 0; }
	.sku-summary-line { display: block; margin-top: 3px; font-size: 12px; color: #777777; line-height: 18px; overflow-wrap: anywhere; }
	.sku-stock { display: block; margin-top: 3px; color: #999999; font-size: 12px; line-height: 18px; }
	.sheet-close { position: absolute; top: 12px; right: 12px; display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; color: #888888; font-size: 27px; font-weight: 300; }
	.specification-scroll { flex: 1; height: 0; min-height: 0; }
	.specification-section { padding: 18px 16px; border-bottom: 1px solid #f5f5f5; }
	.section-label { font-size: 14px; color: #333333; }
	.specification-options { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
	.specification-option { padding: 7px 12px; border: 1px solid #eeeeee; border-radius: 5px; color: #555555; background: #f7f7f7; font-size: 13px; line-height: 20px; overflow-wrap: anywhere; }
	.option-selected { border-color: #ff3a4b; color: #ff3a4b; background: #fff0f2; }
	.option-disabled { color: #bbbbbb; background: #fafafa; border-style: dashed; }
	.sold-out-label { font-size: 11px; }
	.specification-empty { padding-top: 16px; color: #999999; font-size: 13px; }
	.quantity-row { display: flex; align-items: center; justify-content: space-between; padding: 17px 16px; }
	.quantity-stepper { display: flex; align-items: center; gap: 2px; }
	.quantity-button { width: 32px; height: 30px; margin: 0; padding: 0; border-radius: 3px; background: #f3f4f5; color: #666666; font-size: 21px; line-height: 28px; }
	.quantity-button[disabled] { color: #cccccc; background: #fafafa; }
	.quantity-input { width: 42px; height: 30px; text-align: center; font-size: 14px; color: #333333; background: #f7f7f7; }
	.sheet-status { display: block; padding: 0 16px 15px; color: #d37625; font-size: 12px; line-height: 20px; }
	.sheet-actions { flex-shrink: 0; display: flex; padding: 12px 16px calc(12px + env(safe-area-inset-bottom)); background: #ffffff; }
	.attributes-panel { padding-bottom: env(safe-area-inset-bottom); }
	.sheet-title { position: relative; height: 56px; border-bottom: 1px solid #f4f4f4; font-size: 15px; line-height: 56px; text-align: center; }
	.attributes-scroll { height: 45vh; max-height: 500px; }
	.attribute-row { display: flex; align-items: flex-start; margin: 0 18px; padding: 14px 0; border-bottom: 1px solid #f3f3f3; font-size: 13px; line-height: 22px; }
	.attribute-name { width: 30%; flex-shrink: 0; padding-right: 15px; color: #888888; overflow-wrap: anywhere; }
	.attribute-value { flex: 1; min-width: 0; color: #333333; white-space: pre-wrap; overflow-wrap: anywhere; }
	@media (max-width: 360px) {
		.cart-entry { width: 42px; margin-right: 6px; }
		.action-button { font-size: 13px; padding: 0 4px; }
		.sku-image { width: 68px; height: 68px; margin-right: 10px; }
	}
</style>
