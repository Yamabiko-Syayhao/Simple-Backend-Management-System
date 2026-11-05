<template>
	<view class="goods-cell" @click="emit('tap', item)">
		<view class="goods-cell-image">
			<image v-if="item.image" class="goods-cell-img" :src="imageUrl(item.image)" mode="aspectFill"></image>
			<view v-else class="goods-cell-img goods-cell-img--empty">暂无图片</view>
		</view>
		<text class="goods-cell-name">{{ item.name }}</text>
		<view class="goods-cell-price">
			<text class="cell-price-symbol">¥</text>
			<text class="cell-price-value">{{ priceText }}</text>
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

	const priceText = computed(() => {
		const num = Number(props.item.retail_price || 0)
		return Number.isInteger(num) ? String(num) : num.toFixed(2)
	})
</script>

<style scoped>
	.goods-cell {
		width: 100%;
		background-color: #ffffff;
	}

	.goods-cell-image {
		width: 100%;
		height: 150px;
		background-color: #f7f7f7;
		overflow: hidden;
	}

	.goods-cell-img {
		width: 100%;
		height: 150px;
		display: block;
	}

	.goods-cell-img--empty {
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 12px;
		color: #b8b8b8;
	}

	.goods-cell-name {
		display: block;
		margin-top: 10px;
		font-size: 13px;
		color: #333333;
		line-height: 18px;
	}

	.goods-cell-price {
		display: flex;
		align-items: baseline;
		margin-top: 6px;
	}

	.cell-price-symbol {
		font-size: 11px;
		color: #e93b3b;
	}

	.cell-price-value {
		font-size: 15px;
		color: #e93b3b;
	}
</style>
