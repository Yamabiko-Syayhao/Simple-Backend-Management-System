<template>
	<view class="my-orders-page">
		<view class="my-orders-header">
			<nav-header title="我的订单" />
			<view class="my-orders-tabs" role="tablist" aria-label="订单状态">
				<view v-for="tab in tabs" :key="tab.key" class="my-orders-tab" :class="{ 'my-orders-tab--active': selectedTab === tab.key }" role="tab" :aria-selected="selectedTab === tab.key" @click="selectTab(tab.key)">{{ tab.label }}</view>
			</view>
		</view>
		<view v-if="!loggedIn" class="my-orders-state"><text>请登录后查看本人订单</text><button class="my-orders-retry" @click="goLogin">去登录</button></view>
		<template v-else>
			<view v-for="order in rows" :key="order.id" class="my-orders-card">
				<view class="my-orders-card-head" role="button" :aria-label="`查看订单${order.order_no}`" @click="openDetail(order)"><text class="my-orders-number">订单编号：{{ order.order_no }}</text><text class="my-orders-status">{{ order.status_name }}</text></view>
				<view role="button" :aria-label="`订单${order.order_no}商品详情`" @click="openDetail(order)">
					<view v-for="(item, index) in order.items || []" :key="`${order.id}-${index}`" class="my-orders-item">
						<image v-if="item.image" class="my-orders-image" :src="imageUrl(item.image)" mode="aspectFit" />
						<view v-else class="my-orders-image my-orders-image--empty">暂无图片</view>
						<view class="my-orders-item-info"><text class="my-orders-name">{{ item.name }}</text><text class="my-orders-spec">{{ item.specification }}</text><view class="my-orders-item-price"><text>¥{{ item.price_text }}</text><text class="my-orders-quantity">×{{ item.quantity }}</text></view></view>
					</view>
					<view v-if="!(order.items || []).length" class="my-orders-missing">暂无商品明细</view>
				</view>
				<view class="my-orders-total">合计：<text>¥{{ order.order_amount_text }}</text><text class="my-orders-freight">（含运费）</text></view>
				<view class="my-orders-actions"><button class="my-orders-action" @click="openDetail(order)">查看详情</button><button v-if="order.can_delete" class="my-orders-action" :disabled="Boolean(deletingId)" @click="remove(order)">{{ deletingId === order.id ? '删除中…' : '删除订单' }}</button><button v-if="order.can_pay" class="my-orders-action my-orders-action--primary" @click="goPayment(order)">去支付</button></view>
			</view>
			<view v-if="loading" class="my-orders-state">正在加载订单…</view>
			<view v-else-if="failed" class="my-orders-state"><text>订单加载失败</text><button class="my-orders-retry" @click="load(false)">重新加载</button></view>
			<view v-else-if="loaded && !rows.length" class="my-orders-state">暂无{{ selectedTab === 'all' ? '' : tabs.find((tab) => tab.key === selectedTab).label }}订单</view>
			<button v-else-if="hasMore" class="my-orders-more" @click="load(false)">加载更多</button>
			<view v-else-if="loaded" class="my-orders-end">没有更多了</view>
		</template>
	</view>
</template>

<script setup>
	import { computed, ref } from 'vue'
	import { onLoad, onReachBottom, onShow, onUnload } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { orderMyDeleted, orderMyList } from '@/api/order.js'
	import { imageUrl } from '@/api/url.js'

	const tabs = [{ key: 'all', label: '全部' }, { key: 'pay', label: '待付款' }, { key: 'send', label: '待发货' }, { key: 'receive', label: '待收货' }, { key: 'done', label: '已完成' }]
	const selectedTab = ref('all'), rows = ref([]), page = ref(0), total = ref(0)
	const loading = ref(false), loaded = ref(false), failed = ref(false), loggedIn = ref(false), deletingId = ref(0)
	const hasMore = computed(() => loaded.value && rows.value.length < total.value)
	const pageSize = 20
	let disposed = false, version = 0, ownerToken = ''
	const goLogin = () => uni.navigateTo({ url: '/pages/login/login' })
	const currentOwner = () => ownerToken && ownerToken === uni.getStorageSync('member_token')
	const load = async (reset = false) => {
		if (disposed || (!reset && loading.value)) return
		if (reset) { version += 1; rows.value = []; page.value = 0; total.value = 0; loaded.value = false; loading.value = false }
		const token = uni.getStorageSync('member_token') || ''
		loggedIn.value = Boolean(token)
		if (!token) { ownerToken = ''; rows.value = []; failed.value = false; return }
		const requestId = ++version, nextPage = page.value + 1
		ownerToken = token
		loading.value = true; failed.value = false
		try {
			const res = await orderMyList({ page: nextPage, pageSize, tab: selectedTab.value })
			if (disposed || requestId !== version || token !== uni.getStorageSync('member_token')) return
			const data = res.data || {}, nextRows = Array.isArray(data.rows) ? data.rows : []
			rows.value = nextPage === 1 ? nextRows : rows.value.concat(nextRows)
			page.value = nextPage; total.value = Number(data.rowTotal) || 0; loaded.value = true
		} catch (error) { if (!disposed && requestId === version && currentOwner()) failed.value = true }
		finally { if (!disposed && requestId === version) loading.value = false }
	}
	const selectTab = (key) => { if (selectedTab.value !== key) { selectedTab.value = key; load(true) } }
	const openDetail = (order) => { if (currentOwner()) uni.navigateTo({ url: `/pages/order/detail?id=${order.id}` }); else load(true) }
	const goPayment = (order) => { if (currentOwner() && order.can_pay) uni.navigateTo({ url: `/pages/order/payment?id=${order.id}` }); else load(true) }
	const remove = async (order) => {
		if (!currentOwner()) { load(true); return }
		if (!order.can_delete || deletingId.value) return
		const token = ownerToken
		deletingId.value = order.id
		const confirmed = await new Promise((resolve) => uni.showModal({ title: '删除订单', content: '确定删除这笔已取消的订单吗？', confirmColor: '#ee4442', success: (result) => resolve(result.confirm), fail: () => resolve(false) }))
		if (!confirmed || disposed || token !== uni.getStorageSync('member_token')) { deletingId.value = 0; return }
		try {
			await orderMyDeleted({ id: order.id })
			if (disposed || token !== uni.getStorageSync('member_token')) return
			uni.$emit('order:change'); uni.showToast({ title: '订单已删除', icon: 'success' }); await load(true)
		} catch (error) { /* 请求层统一提示，保留当前列表 */ }
		finally { if (!disposed) deletingId.value = 0 }
	}
	onLoad((options = {}) => { if (tabs.some((tab) => tab.key === options.tab)) selectedTab.value = options.tab })
	onShow(() => load(true))
	onReachBottom(() => { if (hasMore.value && !failed.value) load(false) })
	onUnload(() => { disposed = true; version += 1 })
</script>

<style scoped>
	.my-orders-page { max-width: 700px; min-height: 100vh; margin: 0 auto; padding-bottom: calc(24px + env(safe-area-inset-bottom)); background: #f3f3f3; }
	.my-orders-header { position: sticky; top: 0; z-index: 10; background: #ffffff; }
	.my-orders-tabs { display: flex; height: 48px; background: #ffffff; }
	.my-orders-tab { position: relative; flex: 1; display: flex; justify-content: center; align-items: center; color: #777777; font-size: 13px; }
	.my-orders-tab--active { color: #333333; }
	.my-orders-tab--active::after { content: ''; position: absolute; bottom: 0; left: 30%; right: 30%; height: 3px; border-radius: 2px; background: #f5223e; }
	.my-orders-card { margin-top: 12px; padding: 0 16px; background: #ffffff; }
	.my-orders-card-head { display: flex; justify-content: space-between; gap: 12px; padding: 15px 0; border-bottom: 1px solid #f4f4f4; font-size: 12px; line-height: 18px; }
	.my-orders-number { flex: 1; min-width: 0; overflow-wrap: anywhere; }
	.my-orders-status { flex-shrink: 0; color: #f5223e; }
	.my-orders-item { display: flex; align-items: center; gap: 14px; padding: 14px 0; }
	.my-orders-image { flex-shrink: 0; width: 78px; height: 78px; }
	.my-orders-image--empty { display: flex; align-items: center; justify-content: center; background: #f7f7f7; color: #bbbbbb; font-size: 11px; }
	.my-orders-item-info { flex: 1; min-width: 0; }
	.my-orders-name { display: block; font-size: 14px; line-height: 21px; overflow-wrap: anywhere; }
	.my-orders-spec { display: inline-block; max-width: 100%; margin-top: 5px; padding: 1px 4px; border: 1px solid #cccccc; border-radius: 2px; color: #999999; font-size: 11px; overflow-wrap: anywhere; }
	.my-orders-item-price { display: flex; justify-content: space-between; gap: 10px; margin-top: 12px; font-size: 13px; }
	.my-orders-quantity { color: #999999; }
	.my-orders-total { padding: 10px 0 16px; text-align: right; font-size: 13px; }
	.my-orders-freight { color: #888888; font-size: 12px; }
	.my-orders-actions { display: flex; justify-content: flex-end; flex-wrap: wrap; gap: 10px; padding: 10px 0; border-top: 1px solid #f4f4f4; }
	.my-orders-action { margin: 0; padding: 0 12px; border: 1px solid #e8e8e8; border-radius: 3px; background: #ffffff; font-size: 12px; line-height: 30px; }
	.my-orders-action--primary { border-color: #f5223e; color: #f5223e; }
	.my-orders-state { padding: 60px 20px; text-align: center; color: #999999; font-size: 13px; line-height: 22px; }
	.my-orders-state text { display: block; }
	.my-orders-retry, .my-orders-more { width: max-content; margin: 16px auto; padding: 0 22px; border-radius: 18px; background: #ffffff; color: #ee4442; font-size: 12px; line-height: 34px; }
	.my-orders-end, .my-orders-missing { padding: 24px 15px; text-align: center; color: #aaaaaa; font-size: 12px; }
	.my-orders-action::after, .my-orders-retry::after, .my-orders-more::after { border: 0; }
	@media (max-width: 360px) { .my-orders-card { padding: 0 12px; } .my-orders-image { width: 64px; height: 64px; } .my-orders-card-head { gap: 8px; font-size: 11px; } }
</style>
