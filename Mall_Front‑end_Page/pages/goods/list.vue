<template>
	<view class="goods-list-page">
		<view class="goods-list-header">
			<nav-header :title="pageTitle"></nav-header>
			<scroll-view
				v-if="categoryMode && categoryTabs.length && !categoryLoading && !categoryError"
				class="goods-category-scroll"
				scroll-x
				:scroll-into-view="activeTabId"
				:scroll-with-animation="true"
				:show-scrollbar="false"
			>
				<view class="goods-category-tabs" role="tablist" aria-label="商品分类">
					<view
						v-for="item in categoryTabs"
						:id="`goods-category-tab-${item.id}`"
						:key="item.id"
						class="goods-category-tab"
						:class="{ 'goods-category-tab--active': selectedCategoryId === item.id }"
						role="tab"
						:aria-selected="selectedCategoryId === item.id"
						@click="selectCategory(item)"
					>{{ item.name }}</view>
				</view>
			</scroll-view>
		</view>

		<view v-if="categoryMode && categoryLoading" class="list-state">分类加载中…</view>
		<view v-else-if="categoryMode && categoryError" class="list-state">
			<text class="list-state-text">分类暂时未能加载</text>
			<button class="list-retry" @click="loadCategories">重新加载分类</button>
		</view>
		<view v-else-if="categoryMode && categoryLoaded && !activeCategory" class="list-state">
			<text class="list-state-text">该类目不存在或已被删除</text>
			<button class="list-retry" @click="goCategories">返回分类页</button>
		</view>
		<template v-else>
			<view v-if="categoryMode && activeCategory" class="goods-category-intro">
				<text class="goods-category-name">{{ activeCategory.name }}</text>
				<text v-if="activeCategory.description" class="goods-category-description">{{ activeCategory.description }}</text>
			</view>
			<goods-row
				v-for="item in list"
				:key="item.id"
				:item="item"
				@tap="goDetail(item)"
			></goods-row>
			<view v-if="goodsLoading" :class="list.length ? 'list-end' : 'list-state'">加载中…</view>
			<view v-else-if="goodsError" :class="list.length ? 'list-load-error' : 'list-state'">
				<text class="list-state-text">{{ list.length ? '更多商品加载失败' : '商品暂时未能加载' }}</text>
				<button class="list-retry" @click="retryGoods">点击重试</button>
			</view>
			<view v-else-if="goodsLoaded && !list.length" class="list-state">暂无商品</view>
			<view v-else-if="goodsLoaded && !hasMore" class="list-end">没有更多了</view>
		</template>
	</view>
</template>

<script setup>
	import { computed, ref } from 'vue'
	import { onLoad, onReachBottom, onUnload } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import GoodsRow from '@/components/goods-row/goods-row.vue'
	import { goodsClientList } from '@/api/goods.js'
	import { categoryClientTree } from '@/api/category.js'

	const query = ref({ scene: 'default', keyword: '', brand_id: '', title: '' })
	const categoryMode = ref(false)
	const selectedCategoryId = ref(0)
	const categoryTree = ref([])
	const categoryLoading = ref(false)
	const categoryLoaded = ref(false)
	const categoryError = ref(false)
	const list = ref([])
	const page = ref(0)
	const pageSize = 20
	const total = ref(0)
	const goodsLoading = ref(false)
	const goodsLoaded = ref(false)
	const goodsError = ref(false)
	const endReached = ref(false)
	let disposed = false
	let categoryRequestVersion = 0
	let goodsRequestVersion = 0

	const parentCategory = computed(() => categoryTree.value.find((parent) =>
		Number(parent.id) === selectedCategoryId.value ||
		(parent.children || []).some((child) => Number(child.id) === selectedCategoryId.value)
	) || null)
	const activeCategory = computed(() => {
		const parent = parentCategory.value
		if (!parent) return null
		return Number(parent.id) === selectedCategoryId.value ? parent :
			(parent.children || []).find((child) => Number(child.id) === selectedCategoryId.value) || null
	})
	const categoryTabs = computed(() => {
		const parent = parentCategory.value
		if (!parent) return []
		const children = parent.children || []
		// “全部”是父级商品范围的切换项，使用真实父 ID，不额外创建类目。
		return children.length ? [{ ...parent, name: '全部' }, ...children] : [parent]
	})
	const activeTabId = computed(() => `goods-category-tab-${selectedCategoryId.value}`)
	const pageTitle = computed(() => categoryMode.value ? activeCategory.value && activeCategory.value.name || '分类商品' : query.value.title || '商品列表')
	const hasMore = computed(() => goodsLoaded.value && !endReached.value && list.value.length < total.value)

	const resetGoods = () => {
		goodsRequestVersion += 1
		goodsLoading.value = false
		goodsLoaded.value = false
		goodsError.value = false
		list.value = []
		page.value = 0
		total.value = 0
		endReached.value = false
	}
	const loadCategories = async () => {
		if (disposed) return
		resetGoods()
		categoryError.value = false
		if (!selectedCategoryId.value) {
			categoryTree.value = []
			categoryLoaded.value = true
			return
		}
		const version = ++categoryRequestVersion
		categoryLoading.value = true
		try {
			const res = await categoryClientTree()
			if (disposed || version !== categoryRequestVersion) return
			categoryTree.value = (Array.isArray(res.data) ? res.data : []).map((parent) => ({
				...parent,
				id: Number(parent.id),
				children: (Array.isArray(parent.children) ? parent.children : []).map((child) => ({ ...child, id: Number(child.id) }))
			}))
			categoryLoaded.value = true
			categoryLoading.value = false
			if (activeCategory.value) await loadGoods(true)
		} catch (error) {
			if (!disposed && version === categoryRequestVersion) categoryError.value = true
		} finally {
			if (!disposed && version === categoryRequestVersion) categoryLoading.value = false
		}
	}
	const loadGoods = async (reset = false) => {
		if (disposed || categoryMode.value && (categoryLoading.value || categoryError.value || !activeCategory.value)) return
		if (!reset && (goodsLoading.value || !hasMore.value)) return
		if (reset) resetGoods()
		const requestedPage = reset ? 1 : page.value + 1
		const categoryId = selectedCategoryId.value
		const version = ++goodsRequestVersion
		goodsLoading.value = true
		goodsError.value = false
		try {
			const res = await goodsClientList({
				page: requestedPage,
				pageSize,
				scene: query.value.scene,
				keyword: query.value.keyword || undefined,
				category_id: categoryMode.value ? categoryId : undefined,
				brand_id: query.value.brand_id || undefined
			})
			if (disposed || version !== goodsRequestVersion || categoryId !== selectedCategoryId.value) return
			const rows = Array.isArray(res.data && res.data.rows) ? res.data.rows : []
			const combined = reset ? rows : list.value.concat(rows)
			const seen = new Set()
			list.value = combined.filter((item) => {
				if (seen.has(item.id)) return false
				seen.add(item.id)
				return true
			})
			total.value = Math.max(0, Number(res.data && res.data.rowTotal) || 0)
			page.value = requestedPage
			endReached.value = rows.length < pageSize || requestedPage * pageSize >= total.value
			goodsLoaded.value = true
		} catch (error) {
			// 请求封装统一提示；页码只在成功后推进，下一页失败时保留已有商品。
			if (!disposed && version === goodsRequestVersion) goodsError.value = true
		} finally {
			if (!disposed && version === goodsRequestVersion) goodsLoading.value = false
		}
	}
	const selectCategory = (item) => {
		if (disposed || selectedCategoryId.value === item.id) return
		selectedCategoryId.value = item.id
		loadGoods(true)
		uni.pageScrollTo({ scrollTop: 0, duration: 0 })
	}
	const retryGoods = () => loadGoods(page.value === 0)
	const goCategories = () => uni.redirectTo({ url: '/pages/category/index' })
	const goDetail = (item) => uni.navigateTo({ url: `/pages/goods/detail?id=${item.id}` })
	const decodeTitle = (value) => {
		try { return decodeURIComponent(value || '') } catch (error) { return value || '' }
	}

	onLoad((options = {}) => {
		query.value = {
			scene: options.scene || 'default',
			keyword: options.keyword || '',
			brand_id: options.brand_id || '',
			title: decodeTitle(options.title)
		}
		categoryMode.value = Object.prototype.hasOwnProperty.call(options, 'category_id')
		const id = Number(options.category_id)
		selectedCategoryId.value = Number.isSafeInteger(id) && id > 0 ? id : 0
		if (categoryMode.value) loadCategories()
		else loadGoods(true)
	})
	onReachBottom(() => {
		if (!goodsError.value) loadGoods(false)
	})
	onUnload(() => {
		disposed = true
		categoryRequestVersion += 1
		goodsRequestVersion += 1
	})
</script>

<style scoped>
	.goods-list-page { max-width: 700px; min-height: 100vh; margin: 0 auto; padding-bottom: calc(20px + env(safe-area-inset-bottom)); background: #ffffff; }
	.goods-list-header { position: sticky; top: 0; z-index: 10; background: #ffffff; }
	.goods-category-scroll { width: 100%; border-bottom: 1px solid #f5f5f5; white-space: nowrap; }
	.goods-category-tabs { display: inline-flex; min-width: 100%; }
	.goods-category-tab { position: relative; display: inline-flex; flex-shrink: 0; align-items: center; justify-content: center; min-height: 46px; padding: 0 14px; color: #666666; font-size: 13px; line-height: 20px; }
	.goods-category-tab--active { color: #ee4442; }
	.goods-category-tab--active::after { position: absolute; bottom: 3px; left: 50%; width: 28px; height: 3px; border-radius: 2px; background: #ee4442; content: ''; transform: translateX(-50%); }
	.goods-category-intro { padding: 24px 18px 28px; text-align: center; }
	.goods-category-name { display: block; font-size: 19px; color: #333333; line-height: 28px; word-break: break-word; }
	.goods-category-description { display: block; margin-top: 10px; color: #999999; font-size: 14px; line-height: 22px; word-break: break-word; }
	.list-state { padding: 65px 20px; text-align: center; color: #aaaaaa; font-size: 13px; line-height: 22px; }
	.list-state-text { display: block; }
	.list-load-error { padding: 18px 20px 24px; text-align: center; color: #aaaaaa; font-size: 12px; }
	.list-retry { display: inline-block; margin: 16px 0 0; padding: 0 22px; height: 34px; border: 1px solid #ee4442; border-radius: 18px; background: #ffffff; color: #ee4442; font-size: 12px; line-height: 32px; }
	.list-retry::after { border: 0; }
	.list-end { padding: 20px 12px 28px; text-align: center; color: #aaaaaa; font-size: 12px; }
	@media (max-width: 360px) {
		.goods-category-tab { padding: 0 12px; }
		.goods-category-intro { padding: 20px 14px 24px; }
		.goods-category-name { font-size: 18px; }
	}
</style>
