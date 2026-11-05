<template>
	<view class="home-page">
		<!-- 搜索 -->
		<view class="search-bar" @click="goSearch">
			<image class="search-icon" src="/static/icons/ic-search.svg" mode="aspectFit"></image>
			<text class="search-placeholder">点击前往搜索</text>
		</view>

		<!-- 轮播 -->
		<view class="banner-wrap">
			<swiper
				v-if="banners.length"
				class="banner"
				:autoplay="true"
				:interval="4000"
				:duration="400"
				circular
				indicator-dots
				indicator-color="rgba(255,255,255,.5)"
				indicator-active-color="#ffffff"
			>
				<swiper-item v-for="item in banners" :key="item.id" @click="onBanner(item)">
					<image class="banner-img" :src="imageUrl(item.image)" mode="aspectFill"></image>
				</swiper-item>
			</swiper>
			<view v-else class="banner banner--empty">
				<text class="banner-empty-text">商城精选</text>
			</view>
		</view>

		<!-- 快捷分类 -->
		<view v-if="categories.length" class="quick-nav">
			<view
				v-for="item in categories"
				:key="item.id"
				class="quick-item"
				@click="goCategory(item)"
			>
				<image v-if="isImageUrl(item.icon)" class="quick-icon" :src="imageUrl(item.icon)" mode="aspectFit"></image>
				<view v-else class="quick-icon quick-icon--empty">{{ item.name.slice(0, 1) }}</view>
				<text class="quick-label">{{ item.name }}</text>
			</view>
		</view>

		<!-- 优惠券 -->
		<view v-if="coupons.length" class="coupon-section">
			<scroll-view scroll-x class="coupon-scroll">
				<view class="coupon-list">
					<view
						v-for="item in coupons"
						:key="item.id"
						class="coupon-card"
						:class="{ 'coupon-card--loading': claimingIds.includes(item.id) }"
						@click="claimCoupon(item)"
					>
						<view class="coupon-left">
							<text class="coupon-symbol">¥</text>
							<text class="coupon-amount">{{ item.discount_text }}</text>
							<text class="coupon-unit">元</text>
						</view>
						<view class="coupon-right">
							<text class="coupon-name">{{ item.name }}</text>
							<text class="coupon-desc">{{ item.min_text }}</text>
							<text class="coupon-time">{{ item.time_text }}</text>
							<text class="coupon-claim-label">{{ claimingIds.includes(item.id) ? '领取中…' : '点击领取' }}</text>
						</view>
					</view>
				</view>
			</scroll-view>
		</view>

		<!-- 团购专区 -->
		<view class="section-head">
			<text class="section-title">团购专区</text>
			<view class="section-more" @click="goGroupList">
				<text>更多团购商品</text>
				<text class="chevron">›</text>
			</view>
		</view>
		<scroll-view v-if="groups.length" scroll-x class="group-scroll">
			<view class="group-list">
				<view
					v-for="item in groups"
					:key="item.id"
					class="group-card"
					@click="goGoods(item.goods_id)"
				>
					<image v-if="item.goods_image" class="group-img" :src="imageUrl(item.goods_image)" mode="aspectFill"></image>
					<view v-else class="group-img group-img--empty">暂无图片</view>
					<text class="group-name">{{ item.goods_name }}</text>
					<view class="group-price-line">
						<text class="group-price">¥{{ formatNumber(item.discount) }}</text>
						<text class="group-people">{{ item.people }}人团</text>
					</view>
				</view>
			</view>
		</scroll-view>

		<!-- 品牌商直供 -->
		<view class="section-head">
			<text class="section-title">品牌商直供</text>
			<view class="section-more" @click="goBrandList">
				<text>更多品牌商</text>
				<text class="chevron">›</text>
			</view>
		</view>
		<view class="brand-grid">
			<view
				v-for="item in brands"
				:key="item.id"
				class="brand-item"
				@click="goBrand(item.id)"
			>
				<image v-if="item.image" class="brand-img" :src="imageUrl(item.image)" mode="aspectFill"></image>
				<view v-else class="brand-img brand-img--empty">暂无图片</view>
				<text class="brand-name">{{ item.name }}</text>
			</view>
		</view>

		<!-- 新品首发 -->
		<view class="section-head">
			<text class="section-title">新品首发</text>
			<view class="section-more" @click="goGoodsList('new', '新品首发')">
				<text>更多新品首发</text>
				<text class="chevron">›</text>
			</view>
		</view>
		<view class="goods-grid">
			<view v-for="item in newGoods" :key="item.id" class="goods-grid-item">
				<goods-cell :item="item" @tap="goGoods(item.id)"></goods-cell>
			</view>
		</view>

		<!-- 人气推荐 -->
		<view class="section-head">
			<text class="section-title">人气推荐</text>
			<view class="section-more" @click="goGoodsList('hot', '大家都在买')">
				<text>更多人气推荐</text>
				<text class="chevron">›</text>
			</view>
		</view>
		<view class="goods-grid">
			<view v-for="item in hotGoods" :key="item.id" class="goods-grid-item">
				<goods-cell :item="item" @tap="goGoods(item.id)"></goods-cell>
			</view>
		</view>

		<!-- 专题精选 -->
		<view class="section-head">
			<text class="section-title">专题精选</text>
			<view class="section-more" @click="goTopicList">
				<text>更多专题精选</text>
				<text class="chevron">›</text>
			</view>
		</view>
		<view class="topic-grid">
			<view
				v-for="item in topics"
				:key="item.id"
				class="topic-item"
				@click="goTopic(item.id)"
			>
				<image v-if="item.image" class="topic-img" :src="imageUrl(item.image)" mode="aspectFill"></image>
				<view v-else class="topic-img topic-img--empty">暂无图片</view>
				<text class="topic-title">{{ item.title }}</text>
				<text v-if="item.subtitle" class="topic-subtitle">{{ item.subtitle }}</text>
			</view>
		</view>

		<view class="page-bottom"></view>
		<tab-bar current="featured" />
	</view>
</template>

<script setup>
	import { onMounted, onUnmounted, reactive, ref, toRefs } from 'vue'
	import TabBar from '@/components/tab-bar/tab-bar.vue'
	import GoodsCell from '@/components/goods-cell/goods-cell.vue'
	import { adBanners, couponClientList, couponClaim } from '@/api/marketing.js'
	import { categoryClientList } from '@/api/category.js'
	import { groupRuleClientList } from '@/api/group.js'
	import { brandClientList } from '@/api/brand.js'
	import { goodsClientList } from '@/api/goods.js'
	import { topicClientList } from '@/api/topic.js'
	import { imageUrl } from '@/api/url.js'

	const state = reactive({
		banners: [],
		categories: [],
		coupons: [],
		groups: [],
		brands: [],
		newGoods: [],
		hotGoods: [],
		topics: []
	})
	const claimingIds = ref([])
	let pageAlive = true
	let openingLogin = false
	const claimCoupon = async (item) => {
		if (claimingIds.value.includes(item.id)) return
		if (!uni.getStorageSync('member_token')) {
			if (openingLogin) return
			openingLogin = true
			uni.showToast({ title: '请先登录后领取优惠券', icon: 'none' })
			uni.navigateTo({ url: '/pages/login/login', complete: () => { openingLogin = false } })
			return
		}
		claimingIds.value = [...claimingIds.value, item.id]
		try {
			await couponClaim({ id: item.id })
			if (pageAlive) {
				uni.showToast({ title: '领取成功', icon: 'success' })
				uni.$emit('coupon:change')
			}
		} catch (error) {
			// 数量、限领、分发类型及有效期由后端统一校验并提示。
		} finally {
			if (pageAlive) claimingIds.value = claimingIds.value.filter((id) => id !== item.id)
		}
	}
	onUnmounted(() => { pageAlive = false })

	// 模板里直接使用 banners / categories …，必须把它们从 state 中解构成响应式引用
	const {
		banners,
		categories,
		coupons,
		groups,
		brands,
		newGoods,
		hotGoods,
		topics
	} = toRefs(state)

	const formatNumber = (value) => {
		const num = Number(value || 0)
		return Number.isInteger(num) ? String(num) : num.toFixed(2)
	}

	// 类目 icon 可能是后台图标名（如 ele-Menu）而不是图片地址，只对图片地址渲染 image
	const isImageUrl = (value) => {
		if (!value) return false
		return /^(https?:\/\/|\/)/.test(value)
	}

	const loadAll = async () => {
		const tasks = [
			adBanners({}).then((res) => {
				state.banners = (res.data && res.data.rows) || []
			}),
			categoryClientList({}).then((res) => {
				state.categories = res.data || []
			}),
			couponClientList({}).then((res) => {
				state.coupons = res.data || []
			}),
			groupRuleClientList({}).then((res) => {
				state.groups = res.data || []
			}),
			brandClientList({ page: 1, pageSize: 4 }).then((res) => {
				state.brands = (res.data && res.data.rows) || []
			}),
			goodsClientList({ page: 1, pageSize: 6, scene: 'new' }).then((res) => {
				state.newGoods = (res.data && res.data.rows) || []
			}),
			goodsClientList({ page: 1, pageSize: 6, scene: 'hot' }).then((res) => {
				state.hotGoods = (res.data && res.data.rows) || []
			}),
			topicClientList({ page: 1, pageSize: 4 }).then((res) => {
				state.topics = (res.data && res.data.rows) || []
			})
		]
		// 单个接口失败不影响其他模块渲染
		await Promise.all(tasks.map((task) => task.catch(() => null)))
	}

	onMounted(loadAll)

	const goSearch = () => uni.navigateTo({ url: '/pages/search/index' })
	const goGroupList = () => uni.navigateTo({ url: '/pages/group/list' })
	const goBrandList = () => uni.navigateTo({ url: '/pages/brand/list' })
	const goTopicList = () => uni.navigateTo({ url: '/pages/topic/list' })
	const goBrand = (id) => uni.navigateTo({ url: `/pages/brand/detail?id=${id}` })
	const goGoods = (id) => uni.navigateTo({ url: `/pages/goods/detail?id=${id}` })
	const goTopic = (id) => uni.navigateTo({ url: `/pages/topic/detail?id=${id}` })
	const goCategory = (item) =>
		uni.navigateTo({ url: `/pages/goods/list?category_id=${item.id}&title=${encodeURIComponent(item.name)}` })
	const goGoodsList = (scene, title) =>
		uni.navigateTo({ url: `/pages/goods/list?scene=${scene}&title=${encodeURIComponent(title)}` })
	const onBanner = (item) => {
		if (item.link) {
			// #ifdef H5
			window.location.href = item.link
			// #endif
			// #ifndef H5
			comingSoon('广告跳转')
			// #endif
			return
		}
		comingSoon('广告详情')
	}
	const comingSoon = (label) => uni.showToast({ title: `${label}功能开发中`, icon: 'none' })
</script>

<style scoped>
	.coupon-card--loading { opacity: 0.65; }
	.coupon-claim-label { display: block; margin-top: 3px; color: #e93b3b; font-size: 10px; }
	.home-page {
		min-height: 100vh;
		padding-bottom: 76px;
		background-color: #ffffff;
		box-sizing: border-box;
	}

	/* 搜索 */
	.search-bar {
		display: flex;
		align-items: center;
		height: 34px;
		margin: 10px 16px;
		padding: 0 12px;
		border-radius: 17px;
		background-color: #f5f5f5;
	}

	.search-icon {
		width: 15px;
		height: 15px;
		margin-right: 6px;
		opacity: 0.55;
	}

	.search-placeholder {
		font-size: 13px;
		color: #9aa0a6;
	}

	/* 轮播 */
	.banner-wrap {
		margin: 0 0 12px;
	}

	.banner {
		width: 100%;
		height: 168px;
	}

	.banner--empty {
		display: flex;
		align-items: center;
		justify-content: center;
		background-image: linear-gradient(135deg, #f4d9d0 0%, #e9c4bb 100%);
	}

	.banner-empty-text {
		font-size: 20px;
		color: #ffffff;
		letter-spacing: 4px;
	}

	.banner-img {
		width: 100%;
		height: 168px;
		display: block;
	}

	/* 快捷分类 */
	.quick-nav {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		padding: 4px 8px 12px;
	}

	.quick-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		width: 20%;
		margin-bottom: 10px;
	}

	.quick-icon {
		width: 44px;
		height: 44px;
		border-radius: 50%;
		background-color: #f5f5f5;
		display: block;
	}

	.quick-icon--empty {
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 15px;
		color: #9aa0a6;
	}

	.quick-label {
		margin-top: 6px;
		font-size: 12px;
		color: #4a4f57;
	}

	/* 优惠券 */
	.coupon-section {
		padding: 0 0 12px;
	}

	.coupon-scroll {
		width: 100%;
		white-space: nowrap;
	}

	.coupon-list {
		display: inline-flex;
		padding: 0 16px;
	}

	.coupon-card {
		display: flex;
		align-items: center;
		width: 280px;
		height: 76px;
		margin-right: 10px;
		padding: 0 12px;
		border: 1px solid #e93b3b;
		border-radius: 2px;
		background-color: #ffffff;
		box-sizing: border-box;
	}

	.coupon-left {
		display: flex;
		align-items: baseline;
		width: 96px;
		flex-shrink: 0;
		color: #e93b3b;
	}

	.coupon-symbol {
		font-size: 13px;
	}

	.coupon-amount {
		font-size: 24px;
		font-weight: 600;
		margin: 0 2px;
	}

	.coupon-unit {
		font-size: 12px;
	}

	.coupon-right {
		flex: 1;
		display: flex;
		flex-direction: column;
		justify-content: center;
		min-width: 0;
		border-left: 1px dashed #f0d0d0;
		padding-left: 12px;
	}

	.coupon-name {
		font-size: 14px;
		color: #333333;
	}

	.coupon-desc {
		margin-top: 4px;
		font-size: 11px;
		color: #9aa0a6;
	}

	.coupon-time {
		margin-top: 2px;
		font-size: 11px;
		color: #9aa0a6;
	}

	/* 通用区块标题 */
	.section-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 14px 16px 10px;
	}

	.section-title {
		font-size: 15px;
		font-weight: 600;
		color: #333333;
	}

	.section-more {
		display: flex;
		align-items: center;
		font-size: 12px;
		color: #9aa0a6;
	}

	.chevron {
		margin-left: 2px;
		font-size: 15px;
		line-height: 15px;
	}

	/* 团购 */
	.group-scroll {
		width: 100%;
		white-space: nowrap;
	}

	.group-list {
		display: inline-flex;
		padding: 0 16px 4px;
	}

	.group-card {
		width: 120px;
		margin-right: 10px;
		background-color: #ffffff;
	}

	.group-img {
		width: 120px;
		height: 120px;
		border-radius: 4px;
		background-color: #f7f7f7;
		display: block;
	}

	.group-img--empty {
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 11px;
		color: #b8b8b8;
	}

	.group-name {
		display: block;
		margin-top: 6px;
		font-size: 12px;
		color: #333333;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.group-price-line {
		display: flex;
		align-items: baseline;
		margin-top: 4px;
	}

	.group-price {
		font-size: 14px;
		color: #e93b3b;
		margin-right: 6px;
	}

	.group-people {
		font-size: 11px;
		color: #9aa0a6;
	}

	/* 品牌 */
	.brand-grid {
		display: flex;
		flex-wrap: wrap;
		padding: 0 16px;
	}

	.brand-item {
		width: 50%;
		padding: 0 5px 10px;
		box-sizing: border-box;
	}

	.brand-img {
		width: 100%;
		height: 108px;
		border-radius: 2px;
		background-color: #f7f7f7;
		display: block;
	}

	.brand-img--empty {
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 11px;
		color: #b8b8b8;
	}

	.brand-name {
		display: block;
		margin-top: 8px;
		text-align: center;
		font-size: 13px;
		color: #333333;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	/* 商品网格 */
	.goods-grid {
		display: flex;
		flex-wrap: wrap;
		padding: 0 16px;
	}

	.goods-grid-item {
		width: 50%;
		padding: 0 5px 14px;
		box-sizing: border-box;
	}

	/* 专题 */
	.topic-grid {
		display: flex;
		flex-wrap: wrap;
		padding: 0 16px;
	}

	.topic-item {
		width: 50%;
		padding: 0 5px 12px;
		box-sizing: border-box;
	}

	.topic-img {
		width: 100%;
		height: 118px;
		border-radius: 2px;
		background-color: #f7f7f7;
		display: block;
	}

	.topic-img--empty {
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 11px;
		color: #b8b8b8;
	}

	.topic-title {
		display: block;
		margin-top: 8px;
		font-size: 13px;
		color: #333333;
		line-height: 18px;
	}

	.topic-subtitle {
		display: block;
		margin-top: 3px;
		font-size: 11px;
		color: #9aa0a6;
		line-height: 15px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.page-bottom {
		height: 12px;
		background-color: #f5f5f5;
	}
</style>
