<template>
	<view class="category-page">
		<view class="category-search-header">
			<view class="category-search" role="button" aria-label="搜索商品" @click="goSearch">
				<image class="category-search-icon" src="/static/icons/ic-search.svg" mode="aspectFit"></image>
				<text>点击前往搜索</text>
			</view>
		</view>
		<view v-if="loading && !categories.length" class="category-state"><text>正在加载分类…</text></view>
		<view v-else-if="loadFailed" class="category-state">
			<text class="category-state-title">分类暂时未能加载</text>
			<text class="category-state-desc">请检查网络后重试</text>
			<button class="category-state-button" :loading="loading" :disabled="loading" @click="loadCategories">重新加载</button>
		</view>
		<view v-else-if="!categories.length" class="category-state">
			<text class="category-state-title">暂无商品分类</text>
			<text class="category-state-desc">商品分类更新后会显示在这里</text>
		</view>
		<view v-else class="category-layout">
			<scroll-view class="category-sidebar" scroll-y :scroll-into-view="`category-parent-${selectedId}`" scroll-with-animation aria-label="一级商品分类">
				<view
					v-for="item in categories"
					:id="`category-parent-${item.id}`"
					:key="item.id"
					class="category-parent"
					:class="{ 'category-parent--selected': selectedId === item.id }"
					role="tab"
					:aria-label="`${item.name}，一级分类`"
					:aria-selected="selectedId === item.id"
					@click="selectCategory(item)"
				>{{ item.name }}</view>
			</scroll-view>
			<!-- 切换一级分类时重建右侧滚动区，独立回到该类目的顶部。 -->
			<scroll-view :key="selectedId" class="category-main" scroll-y aria-label="当前分类内容">
				<view v-for="parent in currentCategories" :key="parent.id" class="category-detail">
					<image
						v-if="bannerUrl(parent)"
						:key="`banner-${parent.id}-${parent.image}`"
						class="category-banner"
						:src="bannerUrl(parent)"
						mode="aspectFit"
						:aria-label="`${parent.name}类目图片`"
						@error="markImageFailed('banner', parent, parent.image)"
					></image>
					<view v-else class="category-banner category-banner--empty">
						<text class="category-banner-name">{{ parent.name }}</text>
						<text class="category-banner-tip">暂无类目图片</text>
					</view>
					<text v-if="parent.description" class="category-description">{{ parent.description }}</text>
					<view v-if="parent.children && parent.children.length" class="category-grid">
						<view
							v-for="child in parent.children"
							:key="child.id"
							class="category-child"
							role="button"
							:aria-label="`查看${child.name}商品`"
							@click="goGoods(child)"
						>
							<image v-if="iconUrl(child)" :key="`icon-${child.id}-${child.icon}`" class="category-child-icon" :src="iconUrl(child)" mode="aspectFit" @error="markImageFailed('icon', child, child.icon)"></image>
							<view v-else class="category-child-icon category-child-icon--empty"><text>{{ firstCharacter(child.name) }}</text></view>
							<text class="category-child-name">{{ child.name }}</text>
						</view>
					</view>
					<view v-else class="category-children-empty">
						<text>暂无子分类</text>
						<button class="category-state-button category-view-goods" @click="goGoods(parent)">查看本类商品</button>
					</view>
				</view>
			</scroll-view>
		</view>
		<tab-bar current="category" />
	</view>
</template>

<script setup>
	import { computed, ref } from 'vue'
	import { onLoad, onShow, onUnload } from '@dcloudio/uni-app'
	import TabBar from '@/components/tab-bar/tab-bar.vue'
	import { categoryClientTree } from '@/api/category.js'
	import { imageUrl } from '@/api/url.js'

	const categories = ref([])
	const selectedId = ref(0)
	const loading = ref(false)
	const loadFailed = ref(false)
	const failedImages = ref({})
	const currentCategories = computed(() => categories.value.filter((item) => item.id === selectedId.value))
	let requestedCategoryId = 0
	let requestVersion = 0
	let disposed = false

	const positiveId = (value) => {
		const id = Number(value)
		return Number.isSafeInteger(id) && id > 0 ? id : 0
	}
	const rememberSelection = (id) => {
		try { uni.setStorageSync('category_selected_id', id) } catch (error) { /* 缓存不可用不影响浏览 */ }
	}
	const selectCategory = (item) => {
		if (selectedId.value === item.id) return
		selectedId.value = item.id
		rememberSelection(item.id)
	}
	const loadCategories = async () => {
		if (loading.value || disposed) return
		const version = ++requestVersion
		loading.value = true
		loadFailed.value = false
		try {
			const res = await categoryClientTree()
			if (disposed || version !== requestVersion) return
			const rows = Array.isArray(res.data) ? res.data : []
			const wantedId = requestedCategoryId || selectedId.value
			const selected = rows.find((item) => item.id === wantedId || (item.children || []).some((child) => child.id === wantedId)) || rows[0]
			categories.value = rows
			selectedId.value = selected ? selected.id : 0
			requestedCategoryId = 0
			failedImages.value = {}
			rememberSelection(selectedId.value)
		} catch (error) {
			if (!disposed && version === requestVersion) loadFailed.value = true
			// 请求层已统一提示；页面提供重试入口，不重复弹出错误。
		} finally {
			if (!disposed && version === requestVersion) loading.value = false
		}
	}
	const isImagePath = (value) => {
		const path = String(value || '').trim()
		return /^(https?:\/\/|\/\/|\/|data:image\/|blob:)/i.test(path) || /^[^\s]+\.(png|jpe?g|gif|webp|svg|bmp|avif|ico)([?#].*)?$/i.test(path)
	}
	const imageKey = (kind, category, path) => `${kind}:${category.id}:${path || ''}`
	const bannerUrl = (category) => {
		// 一级类目顶部大图只取后台的「类目图片」image。
		const path = category.image
		return isImagePath(path) && !failedImages.value[imageKey('banner', category, path)] ? imageUrl(path) : ''
	}
	const iconUrl = (category) => {
		// 二级类目格子只取后台的「类目图标」icon，不用 image 替代。
		const path = category.icon
		return isImagePath(path) && !failedImages.value[imageKey('icon', category, path)] ? imageUrl(path) : ''
	}
	const markImageFailed = (kind, category, path) => {
		if (disposed) return
		failedImages.value = { ...failedImages.value, [imageKey(kind, category, path)]: true }
	}
	const firstCharacter = (name) => Array.from(String(name || '分类'))[0]
	const goGoods = (category) => {
		uni.navigateTo({ url: `/pages/goods/list?category_id=${category.id}` })
	}
	const goSearch = () => uni.navigateTo({ url: '/pages/search/index?focus=1' })

	onLoad((options) => {
		requestedCategoryId = positiveId(options && (options.category_id || options.id))
		if (!requestedCategoryId) {
			try { selectedId.value = positiveId(uni.getStorageSync('category_selected_id')) } catch (error) { /* 首次访问按接口顺序选择 */ }
		}
	})
	onShow(loadCategories)
	onUnload(() => {
		disposed = true
		requestVersion += 1
	})
</script>

<style scoped>
	.category-page { display: flex; flex-direction: column; width: 100%; max-width: 700px; height: 100vh; margin: 0 auto; padding-bottom: calc(56px + env(safe-area-inset-bottom)); overflow: hidden; background: #ffffff; }
	.category-search-header { flex-shrink: 0; padding: 10px 12px; background: #ffffff; }
	.category-search { display: flex; align-items: center; min-height: 34px; padding: 0 12px; border-radius: 18px; color: #b0b4bc; background: #f5f6f7; font-size: 13px; }
	.category-search-icon { flex-shrink: 0; width: 15px; height: 15px; margin-right: 7px; opacity: 0.6; }
	.category-layout { display: flex; flex: 1; min-height: 0; overflow: hidden; }
	.category-sidebar { flex: 0 0 86px; width: 86px; height: 100%; background: #f8f8f8; }
	.category-parent { position: relative; min-height: 48px; display: flex; align-items: center; justify-content: center; padding: 12px 8px; border-left: 3px solid transparent; color: #333333; font-size: 14px; line-height: 21px; text-align: center; overflow-wrap: anywhere; }
	.category-parent--selected { border-left-color: #ee4442; background: #ffffff; color: #ee4442; }
	.category-main { flex: 1; width: 0; height: 100%; min-width: 0; background: #ffffff; }
	.category-detail { padding: 12px 12px 28px; }
	.category-banner { display: block; width: 100%; height: 155px; border-radius: 4px; }
	.category-banner--empty { display: flex; align-items: center; justify-content: center; flex-direction: column; background: #f8f8f8; }
	.category-banner-name { max-width: 100%; padding: 0 12px; color: #999999; font-size: 22px; line-height: 30px; text-align: center; word-break: break-word; }
	.category-banner-tip { margin-top: 8px; color: #b7b7b7; font-size: 11px; }
	.category-description { display: block; padding: 16px 3px 8px; color: #777777; text-align: center; font-size: 12px; line-height: 20px; overflow-wrap: anywhere; }
	.category-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px 6px; padding-top: 22px; }
	.category-child { min-width: 0; display: flex; align-items: center; flex-direction: column; }
	.category-child-icon { display: flex; align-items: center; justify-content: center; width: 60px; height: 60px; flex-shrink: 0; }
	.category-child-icon--empty { border-radius: 50%; background: #f5f5f5; color: #a3a8b0; font-size: 20px; }
	.category-child-name { align-self: stretch; margin-top: 10px; color: #333333; text-align: center; font-size: 12px; line-height: 18px; overflow-wrap: anywhere; }
	.category-state { flex: 1; min-height: 0; padding: 70px 20px; display: flex; align-items: center; justify-content: center; flex-direction: column; color: #aaaaaa; text-align: center; font-size: 13px; }
	.category-state-title { color: #888888; font-size: 15px; }
	.category-state-desc { margin-top: 10px; color: #aaaaaa; font-size: 12px; line-height: 20px; }
	.category-state-button { display: block; margin: 22px auto 0; padding: 0 24px; line-height: 34px; border-radius: 18px; background: #ee4442; color: #ffffff; font-size: 12px; }
	.category-state-button::after { border: 0; }
	.category-children-empty { padding: 48px 8px 20px; text-align: center; color: #aaaaaa; font-size: 13px; }
	.category-view-goods { width: fit-content; max-width: 100%; padding: 0 18px; }
	@media (max-width: 360px) {
		.category-sidebar { flex-basis: 78px; width: 78px; }
		.category-parent { padding: 11px 6px; font-size: 13px; }
		.category-detail { padding-left: 9px; padding-right: 9px; }
		.category-banner { height: 125px; }
		.category-grid { gap: 22px 4px; }
		.category-child-icon { width: 52px; height: 52px; }
		.category-child-name { font-size: 11px; }
	}
	@media (min-width: 600px) {
		.category-sidebar { flex-basis: 100px; width: 100px; }
		.category-detail { padding-left: 20px; padding-right: 20px; }
		.category-banner { height: 190px; }
		.category-grid { gap: 28px 12px; }
		.category-child-icon { width: 72px; height: 72px; }
		.category-child-name { font-size: 14px; line-height: 22px; }
	}
</style>
