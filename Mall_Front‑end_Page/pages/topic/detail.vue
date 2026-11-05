<template>
	<view class="topic-detail-page">
		<nav-header title="专题详情"></nav-header>

		<view v-if="topic.id" class="topic-body">
			<view class="topic-cover">
				<image v-if="topic.image" class="topic-cover-img" :src="imageUrl(topic.image)" mode="aspectFill"></image>
				<view v-else class="topic-cover-img topic-cover-img--empty">暂无图片</view>
				<view class="topic-cover-mask">
					<text class="topic-title">{{ topic.title }}</text>
					<text class="topic-read">阅读次数：{{ topic.read_count_text }}</text>
				</view>
			</view>

			<view v-if="topic.subtitle" class="topic-subtitle">{{ topic.subtitle }}</view>

			<view class="topic-content">
				<rich-text v-if="contentHtml" :nodes="contentHtml"></rich-text>
				<text v-else class="topic-empty-text">暂无内容</text>
			</view>

			<view v-if="goods.length" class="topic-goods">
				<text class="topic-goods-title">专题好物</text>
				<goods-row
					v-for="item in goods"
					:key="item.id"
					:item="item"
					@tap="goGoods(item)"
				></goods-row>
			</view>
		</view>

		<view v-else-if="!loading" class="topic-end">专题不存在</view>
	</view>
</template>

<script setup>
	import { computed, ref } from 'vue'
	import { onLoad } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import GoodsRow from '@/components/goods-row/goods-row.vue'
	import { topicClientDetail } from '@/api/topic.js'
	import { imageUrl, rewriteHtmlImages } from '@/api/url.js'

	const topic = ref({})
	const goods = ref([])
	const loading = ref(true)

	// 富文本里的 <img src="/api/files/..."> 也要补全后端域名
	const contentHtml = computed(() => rewriteHtmlImages(topic.value.content))

	onLoad(async (options) => {
		const id = Number(options && options.id)
		if (!id) {
			loading.value = false
			return
		}
		try {
			const res = await topicClientDetail({ id })
			topic.value = res.data || {}
			goods.value = (res.data && res.data.goods) || []
		} catch (e) {
			topic.value = {}
		} finally {
			loading.value = false
		}
	})

	const goGoods = (item) => {
		uni.navigateTo({ url: `/pages/goods/detail?id=${item.id}` })
	}
</script>

<style scoped>
	.topic-detail-page {
		min-height: 100vh;
		background-color: #ffffff;
	}

	.topic-cover {
		position: relative;
		width: 100%;
		height: 220px;
		background-color: #f0f0f0;
	}

	.topic-cover-img {
		width: 100%;
		height: 220px;
		display: block;
	}

	.topic-cover-img--empty {
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 13px;
		color: #b8b8b8;
	}

	.topic-cover-mask {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 0;
		padding: 30px 16px 14px;
		background-image: linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.5) 100%);
	}

	.topic-title {
		display: block;
		font-size: 19px;
		color: #ffffff;
	}

	.topic-read {
		display: block;
		margin-top: 6px;
		font-size: 12px;
		color: rgba(255, 255, 255, 0.85);
	}

	.topic-subtitle {
		padding: 14px 16px 0;
		font-size: 13px;
		color: #9aa0a6;
		line-height: 19px;
	}

	.topic-content {
		padding: 12px 16px 4px;
		font-size: 14px;
		color: #333333;
		line-height: 24px;
	}

	.topic-empty-text {
		font-size: 13px;
		color: #b8b8b8;
	}

	.topic-goods {
		margin-top: 8px;
		border-top: 8px solid #f5f5f5;
	}

	.topic-goods-title {
		display: block;
		padding: 14px 16px 6px;
		font-size: 15px;
		font-weight: 600;
		color: #333333;
	}

	.topic-end {
		padding: 80px 0;
		text-align: center;
		font-size: 13px;
		color: #b8b8b8;
	}
</style>
