<template>
	<view class="brand-detail-page">
		<nav-header title="品牌详情"></nav-header>

		<view v-if="brand.id" class="brand-body">
			<view class="brand-cover">
				<image v-if="brand.image" class="brand-cover-img" :src="imageUrl(brand.image)" mode="aspectFill"></image>
				<view v-else class="brand-cover-img brand-cover-img--empty">暂无图片</view>
				<view class="brand-cover-mask">
					<text class="brand-cover-name">{{ brand.name }}</text>
					<view v-if="brand.floor_price" class="brand-cover-price">¥{{ formatNumber(brand.floor_price) }}起</view>
				</view>
			</view>

			<view class="brand-desc-block">
				<text class="brand-desc">{{ brand.description || '暂无介绍' }}</text>
			</view>
		</view>

		<view v-else-if="!loading" class="brand-empty">品牌商不存在</view>
	</view>
</template>

<script setup>
	import { ref } from 'vue'
	import { onLoad } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { brandClientDetail } from '@/api/brand.js'
	import { imageUrl } from '@/api/url.js'

	const brand = ref({})
	const loading = ref(true)

	const formatNumber = (value) => {
		const num = Number(value || 0)
		return Number.isInteger(num) ? String(num) : num.toFixed(2)
	}

	onLoad(async (options) => {
		const id = Number(options && options.id)
		if (!id) {
			loading.value = false
			return
		}
		try {
			const res = await brandClientDetail({ id })
			brand.value = res.data || {}
		} catch (e) {
			brand.value = {}
		} finally {
			loading.value = false
		}
	})
</script>

<style scoped>
	.brand-detail-page {
		min-height: 100vh;
		background-color: #ffffff;
	}

	.brand-cover {
		position: relative;
		width: 100%;
		height: 240px;
		background-color: #f7f7f7;
	}

	.brand-cover-img {
		width: 100%;
		height: 240px;
		display: block;
	}

	.brand-cover-img--empty {
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 13px;
		color: #b8b8b8;
	}

	.brand-cover-mask {
		position: absolute;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		background-color: rgba(0, 0, 0, 0.18);
	}

	.brand-cover-name {
		font-size: 22px;
		color: #ffffff;
		letter-spacing: 1px;
	}

	.brand-cover-price {
		margin-top: 10px;
		font-size: 15px;
		color: #ffffff;
	}

	.brand-desc-block {
		padding: 18px 20px;
	}

	.brand-desc {
		font-size: 14px;
		color: #4a4f57;
		line-height: 24px;
	}

	.brand-empty {
		padding: 80px 0;
		text-align: center;
		font-size: 13px;
		color: #b8b8b8;
	}
</style>
