<template>
	<view class="group-list-page">
		<nav-header title="团购列表"></nav-header>

		<view class="group-banner">
			<text class="group-banner-text">团购列表</text>
		</view>

		<view class="group-items">
			<view
				v-for="item in list"
				:key="item.id"
				class="group-item"
				@click="goGoods(item.goods_id)"
			>
				<image v-if="item.goods_image" class="group-item-img" :src="imageUrl(item.goods_image)" mode="aspectFill"></image>
				<view v-else class="group-item-img group-item-img--empty">暂无图片</view>
				<view class="group-item-main">
					<text class="group-item-name">{{ item.goods_name }}</text>
					<text v-if="item.goods_brief" class="group-item-brief">{{ item.goods_brief }}</text>
					<view class="group-item-price">
						<text class="price-symbol">¥</text>
						<text class="price-value">{{ formatNumber(item.discount) }}</text>
						<text class="price-market">¥{{ formatNumber(item.goods_price) }}</text>
					</view>
					<view class="group-item-meta">
						<text class="meta-text">{{ item.people }}人成团</text>
						<text class="meta-text">截止 {{ item.end_time }}</text>
					</view>
				</view>
			</view>

			<view v-if="!loading" class="group-end">{{ list.length ? '没有更多了' : '暂无进行中的团购' }}</view>
		</view>
	</view>
</template>

<script setup>
	import { ref } from 'vue'
	import { onLoad } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { groupRuleClientList } from '@/api/group.js'
	import { imageUrl } from '@/api/url.js'

	const list = ref([])
	const loading = ref(true)

	const formatNumber = (value) => {
		const num = Number(value || 0)
		return Number.isInteger(num) ? String(num) : num.toFixed(2)
	}

	onLoad(async () => {
		try {
			const res = await groupRuleClientList({})
			list.value = res.data || []
		} catch (e) {
			list.value = []
		} finally {
			loading.value = false
		}
	})

	const goGoods = (id) => {
		uni.navigateTo({ url: `/pages/goods/detail?id=${id}` })
	}
</script>

<style scoped>
	.group-list-page {
		min-height: 100vh;
		background-color: #f7f7f7;
	}

	.group-banner {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 150px;
		background-image: linear-gradient(135deg, #d9c7bd 0%, #bda898 100%);
	}

	.group-banner-text {
		font-size: 24px;
		color: #ffffff;
		letter-spacing: 4px;
	}

	.group-items {
		padding: 10px 0;
	}

	.group-item {
		display: flex;
		margin: 0 12px 10px;
		padding: 12px;
		background-color: #ffffff;
		border-radius: 4px;
	}

	.group-item-img {
		width: 96px;
		height: 96px;
		border-radius: 4px;
		background-color: #f7f7f7;
		display: block;
	}

	.group-item-img--empty {
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 11px;
		color: #b8b8b8;
	}

	.group-item-main {
		flex: 1;
		margin-left: 12px;
		min-width: 0;
	}

	.group-item-name {
		font-size: 14px;
		color: #333333;
	}

	.group-item-brief {
		display: block;
		margin-top: 4px;
		font-size: 12px;
		color: #9aa0a6;
	}

	.group-item-price {
		display: flex;
		align-items: baseline;
		margin-top: 8px;
	}

	.price-symbol {
		font-size: 12px;
		color: #e93b3b;
	}

	.price-value {
		font-size: 18px;
		color: #e93b3b;
		margin-right: 8px;
	}

	.price-market {
		font-size: 12px;
		color: #b8b8b8;
		text-decoration: line-through;
	}

	.group-item-meta {
		display: flex;
		justify-content: space-between;
		margin-top: 8px;
	}

	.meta-text {
		font-size: 11px;
		color: #9aa0a6;
	}

	.group-end {
		padding: 20px 0 30px;
		text-align: center;
		font-size: 12px;
		color: #b8b8b8;
	}
</style>
