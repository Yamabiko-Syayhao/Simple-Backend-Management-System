<template>
	<view class="brand-list-page">
		<nav-header title="品牌商"></nav-header>

		<view class="brand-list">
			<view
				v-for="item in list"
				:key="item.id"
				class="brand-row"
				@click="goDetail(item)"
			>
				<image v-if="item.image" class="brand-row-img" :src="imageUrl(item.image)" mode="aspectFill"></image>
				<view v-else class="brand-row-img brand-row-img--empty">暂无图片</view>
				<view class="brand-row-main">
					<text class="brand-row-name">{{ item.name }}</text>
					<text class="brand-row-desc">{{ item.description || '暂无介绍' }}</text>
				</view>
				<text class="brand-row-arrow">›</text>
			</view>

			<view v-if="!loading && !list.length" class="brand-empty">暂无品牌商</view>
		</view>
	</view>
</template>

<script setup>
	import { ref } from 'vue'
	import { onLoad } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { brandClientList } from '@/api/brand.js'
	import { imageUrl } from '@/api/url.js'

	const list = ref([])
	const loading = ref(true)

	onLoad(async () => {
		try {
			const res = await brandClientList({ page: 1, pageSize: 50 })
			list.value = (res.data && res.data.rows) || []
		} catch (e) {
			list.value = []
		} finally {
			loading.value = false
		}
	})

	const goDetail = (item) => {
		uni.navigateTo({ url: `/pages/brand/detail?id=${item.id}` })
	}
</script>

<style scoped>
	.brand-list-page {
		min-height: 100vh;
		background-color: #ffffff;
	}

	.brand-row {
		display: flex;
		align-items: center;
		padding: 12px 16px;
		border-bottom: 1px solid #f5f5f5;
	}

	.brand-row-img {
		width: 72px;
		height: 72px;
		border-radius: 4px;
		background-color: #f7f7f7;
		display: block;
	}

	.brand-row-img--empty {
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 11px;
		color: #b8b8b8;
	}

	.brand-row-main {
		flex: 1;
		margin-left: 12px;
		min-width: 0;
	}

	.brand-row-name {
		font-size: 14px;
		color: #333333;
	}

	.brand-row-desc {
		display: block;
		margin-top: 6px;
		font-size: 12px;
		color: #9aa0a6;
		line-height: 17px;
		overflow: hidden;
		text-overflow: ellipsis;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
	}

	.brand-row-arrow {
		margin-left: 8px;
		font-size: 18px;
		color: #c8ccd4;
	}

	.brand-empty {
		padding: 60px 0;
		text-align: center;
		font-size: 13px;
		color: #b8b8b8;
	}
</style>
