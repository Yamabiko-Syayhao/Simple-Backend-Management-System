<template>
	<view class="my-favorites-page">
		<nav-header title="我的收藏" />
		<view v-if="!loggedIn" class="my-favorites-state"><text>请登录后查看本人收藏</text><button class="my-favorites-retry" @click="goLogin">去登录</button></view>
		<template v-else>
			<view v-for="item in rows" :key="item.id" class="my-favorites-item">
				<view class="my-favorites-product" role="button" :aria-label="`查看收藏商品${item.name}`" @click="openGoods(item)"><image v-if="item.image" class="my-favorites-image" :src="imageUrl(item.image)" mode="aspectFit" /><view v-else class="my-favorites-image my-favorites-image--empty">暂无图片</view><view class="my-favorites-info"><text class="my-favorites-name">{{ item.name || '商品已失效' }}</text><text class="my-favorites-brief">{{ item.available ? item.brief : item.invalid_reason }}</text><text v-if="item.available" class="my-favorites-price">¥{{ item.retail_price_text }}</text></view></view>
				<button class="my-favorites-remove" :disabled="Boolean(removingId)" @click="remove(item)">{{ removingId === item.id ? '处理中…' : '取消收藏' }}</button>
			</view>
			<view v-if="loading" class="my-favorites-state">正在加载收藏…</view>
			<view v-else-if="failed" class="my-favorites-state"><text>收藏加载失败</text><button class="my-favorites-retry" @click="load(false)">重新加载</button></view>
			<view v-else-if="loaded && !rows.length" class="my-favorites-empty"><image src="/static/icons/ic-star.svg" class="my-favorites-empty-icon" mode="aspectFit" /><text>没有商品收藏</text><button class="my-favorites-retry" @click="goHome">去逛逛</button></view>
			<button v-else-if="hasMore" class="my-favorites-more" @click="load(false)">加载更多</button>
			<view v-else-if="loaded" class="my-favorites-end">没有更多了</view>
		</template>
	</view>
</template>

<script setup>
	import { computed, ref } from 'vue'
	import { onReachBottom, onShow, onUnload } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { favoriteMyDeleted, favoriteMyList } from '@/api/favorite.js'
	import { imageUrl } from '@/api/url.js'
	const rows = ref([]), page = ref(0), total = ref(0), loading = ref(false), loaded = ref(false), failed = ref(false), loggedIn = ref(false), removingId = ref(0)
	const hasMore = computed(() => loaded.value && rows.value.length < total.value)
	let disposed = false, version = 0, ownerToken = ''
	const goLogin = () => uni.navigateTo({ url: '/pages/login/login' })
	const goHome = () => uni.reLaunch({ url: '/pages/index/index' })
	const load = async (reset = false) => {
		if (disposed || (!reset && loading.value)) return
		if (reset) { version += 1; rows.value = []; page.value = 0; total.value = 0; loaded.value = false; loading.value = false }
		const token = uni.getStorageSync('member_token') || ''
		loggedIn.value = Boolean(token)
		if (!token) { ownerToken = ''; rows.value = []; failed.value = false; return }
		ownerToken = token
		const requestId = ++version, nextPage = page.value + 1
		loading.value = true; failed.value = false
		try {
			const res = await favoriteMyList({ page: nextPage, pageSize: 20 })
			if (disposed || requestId !== version || token !== uni.getStorageSync('member_token')) return
			const data = res.data || {}, nextRows = Array.isArray(data.rows) ? data.rows : []
			rows.value = nextPage === 1 ? nextRows : rows.value.concat(nextRows); page.value = nextPage; total.value = Number(data.rowTotal) || 0; loaded.value = true
		} catch (error) { if (!disposed && requestId === version && token === uni.getStorageSync('member_token')) failed.value = true }
		finally { if (!disposed && requestId === version) loading.value = false }
	}
	const openGoods = (item) => {
		if (ownerToken !== uni.getStorageSync('member_token')) { load(true); return }
		if (!item.available) { uni.showToast({ title: item.invalid_reason || '该商品已失效', icon: 'none' }); return }
		uni.navigateTo({ url: `/pages/goods/detail?id=${item.goods_id}` })
	}
	const remove = async (item) => {
		if (ownerToken !== uni.getStorageSync('member_token')) { load(true); return }
		if (removingId.value) return
		removingId.value = item.id
		const token = ownerToken
		const confirmed = await new Promise((resolve) => uni.showModal({ title: '取消收藏', content: '确定取消收藏这件商品吗？', confirmColor: '#ee4442', success: (result) => resolve(result.confirm), fail: () => resolve(false) }))
		if (!confirmed || disposed || token !== uni.getStorageSync('member_token')) { removingId.value = 0; return }
		try {
			await favoriteMyDeleted({ id: item.id })
			if (disposed || token !== uni.getStorageSync('member_token')) return
			uni.$emit('favorite:change', { goods_id: item.goods_id, collected: false }); uni.showToast({ title: '已取消收藏', icon: 'success' }); await load(true)
		} catch (error) { /* 请求层统一提示 */ }
		finally { if (!disposed) removingId.value = 0 }
	}
	onShow(() => load(true))
	onReachBottom(() => { if (hasMore.value && !failed.value) load(false) })
	onUnload(() => { disposed = true; version += 1 })
</script>

<style scoped>
	.my-favorites-page { max-width: 700px; min-height: 100vh; margin: 0 auto; padding-bottom: calc(24px + env(safe-area-inset-bottom)); background: #f3f3f3; }
	.my-favorites-item { position: relative; margin-top: 10px; padding: 16px 16px 50px; background: #ffffff; }
	.my-favorites-product { display: flex; align-items: center; gap: 16px; }
	.my-favorites-image { flex-shrink: 0; width: 90px; height: 90px; }
	.my-favorites-image--empty { display: flex; align-items: center; justify-content: center; color: #aaaaaa; font-size: 11px; background: #f7f7f7; }
	.my-favorites-info { flex: 1; min-width: 0; }
	.my-favorites-name { display: block; color: #333333; font-size: 14px; line-height: 21px; overflow-wrap: anywhere; }
	.my-favorites-brief { display: block; margin-top: 5px; color: #999999; font-size: 12px; line-height: 18px; overflow-wrap: anywhere; }
	.my-favorites-price { display: block; margin-top: 12px; color: #ee4442; font-size: 15px; }
	.my-favorites-remove { position: absolute; right: 16px; bottom: 12px; margin: 0; padding: 0 12px; border: 1px solid #eeeeee; border-radius: 3px; background: #ffffff; color: #888888; font-size: 12px; line-height: 28px; }
	.my-favorites-state { padding: 70px 20px; color: #999999; text-align: center; font-size: 13px; line-height: 22px; }
	.my-favorites-state text { display: block; }
	.my-favorites-empty { display: flex; flex-direction: column; align-items: center; padding: 110px 20px; color: #999999; font-size: 13px; }
	.my-favorites-empty-icon { width: 72px; height: 72px; margin-bottom: 24px; opacity: 0.3; }
	.my-favorites-retry, .my-favorites-more { width: max-content; margin: 18px auto; padding: 0 22px; border-radius: 18px; color: #ee4442; background: #ffffff; font-size: 12px; line-height: 34px; }
	.my-favorites-end { padding: 24px 16px; color: #999999; text-align: center; font-size: 12px; }
	.my-favorites-remove::after, .my-favorites-retry::after, .my-favorites-more::after { border: 0; }
	@media (max-width: 360px) { .my-favorites-item { padding: 12px 12px 50px; } .my-favorites-image { width: 72px; height: 72px; } .my-favorites-product { gap: 12px; } }
</style>
