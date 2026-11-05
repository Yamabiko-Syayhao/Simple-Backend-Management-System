<template>
	<view class="cart-page">
		<view class="cart-content">
			<view class="cart-header">
				<view>
					<text class="cart-title">购物车</text>
					<text v-if="rows.length" class="cart-count">共 {{ totalQuantity }} 件商品</text>
				</view>
				<button v-if="rows.length" class="cart-edit" :disabled="busy || loadFailed" @click="toggleEditing">
					{{ editing ? '完成' : '编辑' }}
				</button>
			</view>

			<view v-if="!loggedIn" class="cart-state">
				<image class="cart-state-icon" src="/static/icons/tab-cart.svg" mode="aspectFit"></image>
				<text class="cart-state-title">登录后查看购物车</text>
				<text class="cart-state-desc">喜欢的商品会为你保留在这里</text>
				<button class="cart-state-action" @click="goLogin">去登录</button>
			</view>
			<view v-else-if="loading && !hasLoaded" class="cart-state">
				<text class="cart-state-desc">正在加载购物车…</text>
			</view>
			<view v-else-if="loadFailed" class="cart-state">
				<text class="cart-state-title">购物车暂时未能加载</text>
				<text class="cart-state-desc">请检查网络后重试</text>
				<button class="cart-state-action" :loading="loading" :disabled="busy" @click="loadCart">重新加载</button>
			</view>
			<view v-else-if="hasLoaded && !rows.length" class="cart-state">
				<view class="cart-empty-picture">
					<image class="cart-empty-icon" src="/static/icons/tab-cart.svg" mode="aspectFit"></image>
					<text class="cart-empty-dot cart-empty-dot--one">·</text>
					<text class="cart-empty-dot cart-empty-dot--two">·</text>
				</view>
				<text class="cart-state-title">您的购物车空空如也～</text>
				<text class="cart-state-desc">去挑选几件喜欢的商品吧</text>
				<button class="cart-state-action" @click="goShopping">去逛逛</button>
			</view>
			<view v-else class="cart-list" :class="{ 'cart-list--busy': busy }">
				<view v-for="item in rows" :key="item.id" class="cart-swipe-row">
					<button
						v-if="editing || openedItemId === item.id || (swipingItemId === item.id && swipeOffset > 0)"
						class="cart-delete-action"
						:aria-label="`删除${item.name || '商品'}`"
						:disabled="busy"
						@click.stop="removeItems([item.id])"
					>删除</button>
					<view
						class="cart-item"
						:class="{ 'cart-item--invalid': !item.available, 'cart-item--editing': editing, 'cart-item--swiping': swipingItemId === item.id }"
						:style="itemSwipeStyle(item)"
						@touchstart="startSwipe(item, $event)"
						@touchmove="moveSwipe"
						@touchend="finishSwipe"
						@touchcancel="cancelSwipe"
						@mousedown="startMouseSwipe(item, $event)"
					>
					<view
						class="cart-check-hit"
						role="checkbox"
						:aria-label="`选择${item.name || '商品'}`"
						:aria-checked="isSelected(item)"
						:aria-disabled="busy || (!editing && !item.available)"
						@click="toggleItem(item)"
					>
						<view class="cart-check" :class="{ 'cart-check--selected': isSelected(item), 'cart-check--disabled': !editing && !item.available }">
							<text v-if="isSelected(item)" class="cart-check-mark">✓</text>
						</view>
					</view>
					<view class="cart-product" @click="goGoods(item)">
						<image v-if="item.image" class="cart-image" :src="imageUrl(item.image)" mode="aspectFit"></image>
						<view v-else class="cart-image cart-image--empty">暂无图片</view>
						<view class="cart-info">
							<text class="cart-name">{{ item.name || '商品已删除' }}</text>
							<text class="cart-specification">{{ item.specification || '规格已失效' }}</text>
							<text v-if="!item.available" class="cart-invalid-tip">{{ item.invalid_reason || '该商品暂不可购买' }}</text>
							<view class="cart-price-row">
								<text class="cart-price">¥{{ item.price_text || '0.00' }}</text>
								<text v-if="!editing" class="cart-quantity">×{{ item.quantity }}</text>
							</view>
						</view>
					</view>
					<view class="cart-item-bottom">
						<text class="cart-date">{{ item.creation_date ? `添加于 ${item.creation_date}` : '' }}</text>
						<view v-if="editing && canEditQuantity(item)" class="cart-stepper">
							<button class="cart-stepper-button" :disabled="busy || item.quantity <= 1" aria-label="减少数量" @click="changeQuantity(item, -1)">−</button>
							<text class="cart-stepper-value">{{ item.quantity }}</text>
							<button class="cart-stepper-button" :disabled="busy || item.quantity >= quantityLimit(item)" aria-label="增加数量" @click="changeQuantity(item, 1)">＋</button>
						</view>
					</view>
					</view>
				</view>
				<view class="cart-list-note">商品价格和库存以实时信息为准</view>
			</view>
		</view>

		<view class="cart-summary">
			<view class="cart-summary-inner">
				<view
					class="cart-select-all"
					role="checkbox"
					aria-label="全选购物车商品"
					:aria-checked="allSelected"
					:aria-disabled="busy || loadFailed || !selectableRows.length"
					@click="toggleAll"
				>
					<view class="cart-check" :class="{ 'cart-check--selected': allSelected, 'cart-check--disabled': !selectableRows.length || loadFailed }">
						<text v-if="allSelected" class="cart-check-mark">✓</text>
					</view>
					<text class="cart-select-label">全选</text>
				</view>
				<view v-if="editing" class="cart-summary-right">
					<text class="cart-selected-desc">已选 {{ editSelectedIds.length }} 项</text>
					<button class="cart-submit cart-submit--delete" :disabled="busy || loadFailed || !editSelectedIds.length" @click="removeItems(editSelectedIds)">删除</button>
				</view>
				<view v-else class="cart-summary-right">
					<view class="cart-total">
						<view><text class="cart-total-label">总计：</text><text class="cart-total-price">¥{{ loadFailed ? '--' : totalAmountText }}</text></view>
						<text class="cart-total-note">不含运费</text>
					</view>
					<button class="cart-submit" :class="{ 'cart-submit--muted': !selectedCount }" :disabled="busy || loadFailed || !selectableRows.length" @click="checkout">结算{{ selectedQuantity ? `(${selectedQuantity})` : '' }}</button>
				</view>
			</view>
		</view>
		<tab-bar current="cart" />
	</view>
</template>

<script setup>
	import { computed, ref } from 'vue'
	import { onHide, onLoad, onShow, onUnload } from '@dcloudio/uni-app'
	import TabBar from '@/components/tab-bar/tab-bar.vue'
	import { cartChecked, cartDeleted, cartList, cartUpdate } from '@/api/cart.js'
	import { imageUrl } from '@/api/url.js'

	const rows = ref([])
	const totalQuantity = ref(0)
	const selectedQuantity = ref(0)
	const selectedCount = ref(0)
	const totalAmountText = ref('0.00')
	const loggedIn = ref(false)
	const hasLoaded = ref(false)
	const loading = ref(false)
	const mutating = ref(false)
	const confirming = ref(false)
	const loadFailed = ref(false)
	const editing = ref(false)
	const openedItemId = ref(null)
	const swipingItemId = ref(null)
	const swipeOffset = ref(0)
	const deleteActionWidth = 76
	let gesture = null
	let suppressClickUntil = 0
	// 编辑只选择待删除的条目，不改变正常模式的结算选择，失效条目也可删除。
	const editSelectedIds = ref([])
	const busy = computed(() => loading.value || mutating.value || confirming.value)
	const selectableRows = computed(() => editing.value ? rows.value : rows.value.filter((item) => item.available))
	const allSelected = computed(() => selectableRows.value.length > 0 && selectableRows.value.every(isSelected))
	let visible = false
	let disposed = false
	let requestVersion = 0
	let refreshPending = false
	let loadedToken = ''
	let navigatingToCheckout = false

	const resetSwipe = () => {
		openedItemId.value = null
		swipingItemId.value = null
		swipeOffset.value = 0
		gesture = null
	}
	const itemSwipeStyle = (item) => ({
		transform: `translate3d(-${editing.value ? 0 : swipingItemId.value === item.id ? swipeOffset.value : openedItemId.value === item.id ? deleteActionWidth : 0}px, 0, 0)`
	})
	const touchPoint = (event) => {
		const point = event.touches && event.touches[0] || event.changedTouches && event.changedTouches[0]
		return point ? { x: point.clientX ?? point.pageX, y: point.clientY ?? point.pageY } : null
	}
	const startGesture = (item, point, source) => {
		if (busy.value || loadFailed.value || editing.value) return
		if (!point) return
		const initialOffset = openedItemId.value === item.id ? deleteActionWidth : 0
		if (openedItemId.value !== item.id) openedItemId.value = null
		gesture = { id: item.id, x: point.x, y: point.y, initialOffset, source, direction: '', distance: 0, moved: false }
	}
	const startSwipe = (item, event) => {
		if (!event.touches || event.touches.length !== 1) {
			cancelSwipe()
			return
		}
		startGesture(item, touchPoint(event), 'touch')
	}
	const moveGesture = (point, event) => {
		if (!gesture || busy.value || editing.value) return
		if (!point) return
		const dx = point.x - gesture.x
		const dy = point.y - gesture.y
		if (!gesture.direction) {
			if (Math.max(Math.abs(dx), Math.abs(dy)) < 8) return
			gesture.direction = Math.abs(dx) > Math.abs(dy) * 1.2 ? 'horizontal' : 'vertical'
		}
		gesture.moved = true
		if (gesture.direction !== 'horizontal') return
		// 只拦截已确认的横向手势，保留页面正常的上下滚动。
		if (event.cancelable !== false && event.preventDefault) event.preventDefault()
		gesture.distance = dx
		swipingItemId.value = gesture.id
		swipeOffset.value = Math.max(0, Math.min(deleteActionWidth, gesture.initialOffset - dx))
	}
	const moveSwipe = (event) => {
		if (!event.touches || event.touches.length !== 1) {
			cancelSwipe()
			return
		}
		moveGesture(touchPoint(event), event)
	}
	const startMouseSwipe = (item, event) => {
		// #ifdef H5
		// uni-app 包装后的鼠标事件有坐标，但不保留原生 button 字段。
		if ((event.button != null && event.button !== 0) || busy.value || editing.value || Date.now() < suppressClickUntil) return
		startGesture(item, { x: event.clientX, y: event.clientY }, 'mouse')
		if (gesture && event.preventDefault) event.preventDefault()
		// #endif
	}
	const moveMouseSwipe = (event) => {
		if (gesture && gesture.source === 'mouse') moveGesture({ x: event.clientX, y: event.clientY }, event)
	}
	const finishMouseSwipe = () => {
		if (gesture && gesture.source === 'mouse') finishSwipe()
	}
	const finishSwipe = () => {
		if (!gesture) return
		if (gesture.moved) suppressClickUntil = Date.now() + 350
		if (gesture.direction === 'horizontal') {
			const open = gesture.distance < -28 || (gesture.distance <= 28 && swipeOffset.value > deleteActionWidth / 2)
			openedItemId.value = open ? gesture.id : null
		}
		gesture = null
		swipingItemId.value = null
		swipeOffset.value = 0
	}
	const cancelSwipe = () => {
		if (gesture && gesture.moved) suppressClickUntil = Date.now() + 350
		gesture = null
		swipingItemId.value = null
		swipeOffset.value = 0
	}
	const consumeSwipeTap = () => {
		if (Date.now() < suppressClickUntil) return true
		if (openedItemId.value !== null) {
			resetSwipe()
			return true
		}
		return false
	}

	const clearCart = () => {
		resetSwipe()
		rows.value = []
		totalQuantity.value = 0
		selectedQuantity.value = 0
		selectedCount.value = 0
		totalAmountText.value = '0.00'
		editSelectedIds.value = []
		editing.value = false
	}

	const fetchCart = async () => {
		const token = uni.getStorageSync('member_token') || ''
		loggedIn.value = Boolean(token)
		if (token !== loadedToken) {
			clearCart()
			hasLoaded.value = false
			loadedToken = token
		}
		if (!token) {
			clearCart()
			loadFailed.value = false
			hasLoaded.value = true
			return false
		}
		const version = ++requestVersion
		try {
			const res = await cartList()
			if (disposed || version !== requestVersion || token !== uni.getStorageSync('member_token')) return false
			const data = res.data || {}
			rows.value = data.rows || []
			totalQuantity.value = Number(data.total_quantity || 0)
			selectedQuantity.value = Number(data.selected_quantity || 0)
			selectedCount.value = Number(data.selected_count || 0)
			totalAmountText.value = data.total_amount_text || '0.00'
			const existingIds = new Set(rows.value.map((item) => item.id))
			if (!existingIds.has(openedItemId.value)) resetSwipe()
			editSelectedIds.value = editSelectedIds.value.filter((id) => existingIds.has(id))
			if (!rows.value.length) editing.value = false
			hasLoaded.value = true
			loadFailed.value = false
			return true
		} catch (error) {
			if (!disposed && version === requestVersion) {
				// 请求封装统一提示错误；失败后停止用旧合计继续操作。
				loggedIn.value = Boolean(uni.getStorageSync('member_token'))
				if (!loggedIn.value) clearCart()
				loadFailed.value = loggedIn.value
			}
			return false
		}
	}

	const flushRefresh = () => {
		if (refreshPending && visible && !disposed && !busy.value) {
			refreshPending = false
			loadCart()
		}
	}

	const loadCart = async () => {
		if (busy.value) {
			refreshPending = true
			return
		}
		loading.value = true
		try {
			await fetchCart()
		} finally {
			loading.value = false
			flushRefresh()
		}
	}

	const runMutation = async (action, successMessage = '') => {
		if (busy.value || loadFailed.value || !loggedIn.value || disposed) return
		mutating.value = true
		try {
			await action()
			await fetchCart()
			uni.$emit('cart:change', { source: 'cart' })
			if (!disposed && !loadFailed.value && successMessage) uni.showToast({ title: successMessage, icon: 'success' })
		} catch (error) {
			// 服务端可能因库存/状态变更拒绝操作，刷新后显示当前实际状态。
			await fetchCart()
		} finally {
			mutating.value = false
			flushRefresh()
		}
	}

	function isSelected(item) {
		return editing.value ? editSelectedIds.value.includes(item.id) : Boolean(item.available && item.checked)
	}

	const toggleEditing = () => {
		if (busy.value || loadFailed.value) return
		resetSwipe()
		editing.value = !editing.value
		editSelectedIds.value = editing.value ? rows.value.filter((item) => item.available && item.checked).map((item) => item.id) : []
	}

	const toggleItem = (item) => {
		if (busy.value || loadFailed.value || consumeSwipeTap()) return
		if (editing.value) {
			editSelectedIds.value = isSelected(item) ? editSelectedIds.value.filter((id) => id !== item.id) : [...editSelectedIds.value, item.id]
			return
		}
		if (!item.available) return
		runMutation(() => cartChecked({ ids: [item.id], checked: !item.checked }))
	}

	const toggleAll = () => {
		if (busy.value || loadFailed.value || !selectableRows.value.length) return
		if (editing.value) {
			editSelectedIds.value = allSelected.value ? [] : rows.value.map((item) => item.id)
			return
		}
		runMutation(() => cartChecked({ ids: selectableRows.value.map((item) => item.id), checked: !allSelected.value }))
	}

	const quantityLimit = (item) => Math.min(999, Math.max(0, Number(item.stock || 0)))
	const canEditQuantity = (item) => Boolean(item.available || item.invalid_reason === '库存不足，请调整数量') && quantityLimit(item) > 0
	const changeQuantity = (item, delta) => {
		const limit = quantityLimit(item)
		// 库存减少时一次降到当前可用库存，避免每次减一仍因超库存被服务端拒绝。
		const quantity = delta < 0 ? Math.min(Number(item.quantity) - 1, limit) : Number(item.quantity) + 1
		if (!canEditQuantity(item) || quantity < 1 || quantity > limit) return
		runMutation(() => cartUpdate({ id: item.id, quantity }))
	}

	const removeItems = async (selectedIds) => {
		if (busy.value || loadFailed.value) return
		const ids = [...selectedIds]
		if (!ids.length) {
			uni.showToast({ title: '请先选择要删除的商品', icon: 'none' })
			return
		}
		confirming.value = true
		const confirmed = await new Promise((resolve) => {
			uni.showModal({
				title: '删除商品',
				content: `确定从购物车删除这 ${ids.length} 项商品吗？`,
				confirmColor: '#ee4442',
				success: (result) => resolve(result.confirm),
				fail: () => resolve(false)
			})
		})
		confirming.value = false
		if (confirmed && !disposed) await runMutation(() => cartDeleted({ ids }), '删除成功')
		flushRefresh()
	}

	const goGoods = (item) => {
		if (editing.value || busy.value || consumeSwipeTap() || !item.available || !item.goods_id) return
		uni.navigateTo({ url: `/pages/goods/detail?id=${item.goods_id}` })
	}
	const goLogin = () => uni.navigateTo({ url: '/pages/login/login' })
	const goShopping = () => uni.redirectTo({ url: '/pages/index/index' })
	const checkout = () => {
		if (busy.value || loadFailed.value || editing.value || navigatingToCheckout) return
		const ids = rows.value.filter((item) => item.available && item.checked).map((item) => item.id)
		if (!ids.length) {
			uni.showToast({ title: '请先选择商品', icon: 'none' })
			return
		}
		navigatingToCheckout = true
		resetSwipe()
		uni.navigateTo({
			url: `/pages/order/confirm?source=cart&cart_ids=${encodeURIComponent(ids.join(','))}`,
			complete: () => { navigatingToCheckout = false }
		})
	}
	const onCartChange = (event) => {
		if (event && event.source === 'cart') return
		if (visible) loadCart()
	}
	onLoad(() => {
		uni.$on('cart:change', onCartChange)
		// #ifdef H5
		if (typeof window !== 'undefined') {
			window.addEventListener('mousemove', moveMouseSwipe)
			window.addEventListener('mouseup', finishMouseSwipe)
			window.addEventListener('blur', cancelSwipe)
		}
		// #endif
	})
	onShow(() => {
		visible = true
		loadCart()
	})
	onHide(() => { visible = false; resetSwipe() })
	onUnload(() => {
		disposed = true
		resetSwipe()
		visible = false
		requestVersion += 1
		uni.$off('cart:change', onCartChange)
		// #ifdef H5
		if (typeof window !== 'undefined') {
			window.removeEventListener('mousemove', moveMouseSwipe)
			window.removeEventListener('mouseup', finishMouseSwipe)
			window.removeEventListener('blur', cancelSwipe)
		}
		// #endif
	})
</script>

<style scoped>
	.cart-page { min-height: 100vh; padding-bottom: calc(130px + env(safe-area-inset-bottom)); background: #f5f5f5; color: #333333; }
	.cart-content { max-width: 700px; margin: 0 auto; }
	.cart-header { min-height: 58px; display: flex; align-items: center; justify-content: space-between; padding: 0 16px; background: #ffffff; }
	.cart-title { font-size: 18px; font-weight: 600; }
	.cart-count { margin-left: 10px; font-size: 12px; color: #999999; }
	.cart-edit { margin: 0; padding: 6px 0 6px 14px; font-size: 13px; line-height: 24px; background: transparent; color: #333333; }
	.cart-edit::after, .cart-delete-action::after, .cart-stepper-button::after, .cart-submit::after, .cart-state-action::after { border: 0; }
	.cart-state { min-height: 56vh; display: flex; align-items: center; justify-content: center; flex-direction: column; padding: 54px 20px; text-align: center; }
	.cart-state-icon { width: 68px; height: 68px; opacity: 0.35; margin-bottom: 22px; }
	.cart-empty-picture { position: relative; width: 116px; height: 116px; margin-bottom: 18px; border-radius: 50%; background: #ebebeb; display: flex; align-items: center; justify-content: center; }
	.cart-empty-icon { width: 66px; height: 66px; opacity: 0.32; }
	.cart-empty-dot { position: absolute; font-size: 40px; color: #cccccc; line-height: 1; }
	.cart-empty-dot--one { left: -4px; top: 8px; }
	.cart-empty-dot--two { right: -4px; bottom: 8px; }
	.cart-state-title { font-size: 15px; color: #888888; }
	.cart-state-desc { margin-top: 10px; font-size: 12px; color: #aaaaaa; line-height: 20px; }
	.cart-state-action { margin: 24px 0 0; padding: 0 27px; height: 36px; line-height: 36px; border-radius: 20px; background: #ee4442; color: #ffffff; font-size: 13px; }
	.cart-list { margin-top: 10px; }
	.cart-list--busy { opacity: 0.7; }
	.cart-swipe-row { position: relative; overflow: hidden; margin-bottom: 1px; background: #ffffff; }
	.cart-delete-action { position: absolute; top: 0; bottom: 0; right: 0; display: flex; align-items: center; justify-content: center; width: 76px; margin: 0; padding: 0; border-radius: 0; background: #ee4442; color: #ffffff; font-size: 14px; line-height: 22px; }
	.cart-delete-action[disabled] { background: #f19a99; color: #ffffff; }
	.cart-item { position: relative; display: flex; flex-wrap: wrap; align-items: center; width: 100%; padding: 16px 16px 12px 6px; background: #ffffff; touch-action: pan-y; transition: transform 0.2s ease, width 0.2s ease; }
	.cart-item--editing { width: calc(100% - 76px); }
	.cart-item--swiping { transition: none; }
	.cart-check-hit { width: 38px; flex: 0 0 38px; min-height: 68px; display: flex; justify-content: center; align-items: center; }
	.cart-check { width: 20px; height: 20px; flex: 0 0 20px; border: 1px solid #d5d5d5; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #ffffff; }
	.cart-check--selected { border-color: #ee4442; background: #ee4442; }
	.cart-check--disabled { background: #eeeeee; border-color: #dddddd; }
	.cart-check-mark { font-size: 13px; color: #ffffff; line-height: 18px; }
	.cart-product { display: flex; flex: 1; min-width: 0; gap: 12px; align-items: flex-start; }
	.cart-image { width: 80px; height: 80px; flex: 0 0 80px; border-radius: 5px; background: #fafafa; }
	.cart-image--empty { display: flex; justify-content: center; align-items: center; color: #bbbbbb; font-size: 11px; }
	.cart-info { flex: 1; min-width: 0; }
	.cart-name { display: block; font-size: 14px; line-height: 20px; word-break: break-word; }
	.cart-specification { display: inline-block; max-width: 100%; margin-top: 6px; padding: 2px 6px; border-radius: 3px; font-size: 11px; color: #999999; background: #f5f5f5; line-height: 16px; word-break: break-word; }
	.cart-invalid-tip { display: block; margin-top: 6px; font-size: 11px; color: #dc5959; line-height: 17px; }
	.cart-price-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 10px; }
	.cart-price { color: #ee4442; font-size: 15px; }
	.cart-quantity { font-size: 12px; color: #999999; }
	.cart-item--invalid .cart-image { opacity: 0.45; }
	.cart-item--invalid .cart-name, .cart-item--invalid .cart-price { color: #aaaaaa; }
	.cart-item-bottom { width: 100%; display: flex; align-items: center; justify-content: flex-end; flex-wrap: wrap; gap: 10px; padding: 9px 0 0 38px; }
	.cart-date { flex: 1; font-size: 10px; color: #b2b2b2; min-width: 120px; line-height: 18px; }
	.cart-stepper { display: flex; align-items: center; height: 27px; border: 1px solid #eeeeee; border-radius: 3px; overflow: hidden; }
	.cart-stepper-button { width: 29px; height: 26px; line-height: 24px; padding: 0; margin: 0; font-size: 17px; background: #f7f7f7; color: #555555; border-radius: 0; }
	.cart-stepper-button[disabled] { color: #cccccc; background: #fafafa; }
	.cart-stepper-value { min-width: 31px; padding: 0 5px; text-align: center; font-size: 12px; }
	.cart-list-note { padding: 18px 12px; text-align: center; font-size: 11px; color: #b2b2b2; }
	.cart-summary { position: fixed; left: 0; right: 0; bottom: calc(56px + env(safe-area-inset-bottom)); z-index: 98; background: #ffffff; border-top: 1px solid #f0f0f0; }
	.cart-summary-inner { max-width: 700px; min-height: 60px; padding: 8px 16px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; gap: 8px; }
	.cart-select-all { display: flex; align-items: center; min-height: 42px; padding-right: 10px; }
	.cart-select-label { margin-left: 7px; font-size: 13px; }
	.cart-summary-right { display: flex; justify-content: flex-end; align-items: center; flex: 1; min-width: 0; gap: 12px; }
	.cart-total { text-align: right; min-width: 0; }
	.cart-total-label { font-size: 12px; }
	.cart-total-price { color: #ee4442; font-size: 17px; word-break: break-all; }
	.cart-total-note { display: block; margin-top: 3px; font-size: 10px; color: #aaaaaa; }
	.cart-selected-desc { font-size: 12px; color: #999999; }
	.cart-submit { flex: 0 0 auto; min-width: 104px; padding: 0 20px; margin: 0; height: 40px; line-height: 40px; border-radius: 22px; font-size: 13px; color: #ffffff; background: linear-gradient(100deg, #ff6843, #ed0934); }
	.cart-submit--delete { background: #ee4442; }
	.cart-submit[disabled], .cart-submit--muted { color: #ffffff; background: #f7a5a9; }
	@media (min-width: 701px) {
		.cart-page { background: #ffffff; }
		.cart-content { background: #f5f5f5; min-height: calc(100vh - 116px - env(safe-area-inset-bottom)); }
	}
	@media (max-width: 360px) {
		.cart-summary-inner { padding: 8px 10px; }
		.cart-summary-right { gap: 6px; }
		.cart-submit { min-width: 88px; padding: 0 12px; }
		.cart-total-price { font-size: 15px; }
		.cart-item { padding-right: 10px; }
		.cart-image { width: 66px; height: 66px; flex-basis: 66px; }
		.cart-product { gap: 9px; }
	}
</style>
