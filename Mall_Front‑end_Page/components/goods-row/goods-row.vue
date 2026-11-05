<template>
	<view class="goods-row" @click="emit('tap', item)">
		<view class="goods-row-image">
			<image v-if="item.image" class="goods-row-img" :src="imageUrl(item.image)" mode="aspectFill"></image>
			<view v-else class="goods-row-img goods-row-img--empty">暂无图片</view>
		</view>
		<view class="goods-row-main">
			<text class="goods-row-name">{{ item.name }}</text>
			<text v-if="item.brief" class="goods-row-brief">{{ item.brief }}</text>
			<view class="goods-row-price">
				<text class="price-symbol">¥</text>
				<text class="price-value">{{ priceText }}</text>
				<text v-if="showMarket" class="price-market">¥{{ marketText }}</text>
			</view>
		</view>
	</view>
</template>

<script setup>
	import { computed } from 'vue'
	import { imageUrl } from '@/api/url.js'

	const props = defineProps({
		item: {
			type: Object,
			default: () => ({})
		}
	})

	const emit = defineEmits(['tap'])

	const formatNumber = (value) => {
		const num = Number(value || 0)
		return Number.isInteger(num) ? String(num) : num.toFixed(2)
	}

	const priceText = computed(() => formatNumber(props.item.retail_price))
	const marketText = computed(() => formatNumber(props.item.market_price))
	const showMarket = computed(() => Number(props.item.market_price || 0) > Number(props.item.retail_price || 0))
</script>

<style scoped>
	.goods-row {
		display: flex;
		padding: 12px 16px;
		background-color: #ffffff;
		border-bottom: 8px solid #f5f5f5;
	}

	.goods-row-image {
		flex-shrink: 0;
		width: 88px;
		height: 88px;
		margin-right: 12px;
		border-radius: 4px;
		overflow: hidden;
		background-color: #f7f7f7;
	}

	.goods-row-img {
		width: 88px;
		height: 88px;
		display: block;
	}

	.goods-row-img--empty {
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 11px;
		color: #b8b8b8;
	}

	.goods-row-main {
		flex: 1;
		display: flex;
		flex-direction: column;
		justify-content: center;
		min-width: 0;
	}

	.goods-row-name {
		font-size: 14px;
		color: #333333;
		line-height: 20px;
		overflow: hidden;
	}

	.goods-row-brief {
		margin-top: 4px;
		font-size: 12px;
		color: #9aa0a6;
		line-height: 17px;
	}

	.goods-row-price {
		display: flex;
		align-items: baseline;
		margin-top: 8px;
	}

	.price-symbol {
		font-size: 12px;
		color: #e93b3b;
	}

	.price-value {
		font-size: 16px;
		color: #e93b3b;
		margin-right: 6px;
	}

	.price-market {
		font-size: 12px;
		color: #b8b8b8;
		text-decoration: line-through;
	}
</style>
