<template>
	<view class="topic-list-page">
		<nav-header title="专题精选"></nav-header>

		<view class="topic-items">
			<view
				v-for="item in list"
				:key="item.id"
				class="topic-card"
				@click="goDetail(item)"
			>
				<view class="topic-cover">
					<image v-if="item.image" class="topic-cover-img" :src="imageUrl(item.image)" mode="aspectFill"></image>
					<view v-else class="topic-cover-img topic-cover-img--empty">暂无图片</view>
					<view class="topic-cover-mask">
						<text class="topic-cover-title">{{ item.title }}</text>
						<text class="topic-cover-read">阅读次数：{{ item.read_count_text }}</text>
					</view>
				</view>
				<view v-if="item.subtitle" class="topic-subtitle">{{ item.subtitle }}</view>
			</view>

			<view v-if="!loading" class="topic-end">{{ list.length ? '没有更多了' : '暂无专题' }}</view>
		</view>
	</view>
</template>

<script setup>
	import { ref } from 'vue'
	import { onLoad } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { topicClientList } from '@/api/topic.js'
	import { imageUrl } from '@/api/url.js'

	const list = ref([])
	const loading = ref(true)

	onLoad(async () => {
		try {
			const res = await topicClientList({ page: 1, pageSize: 20 })
			list.value = (res.data && res.data.rows) || []
		} catch (e) {
			list.value = []
		} finally {
			loading.value = false
		}
	})

	const goDetail = (item) => {
		uni.navigateTo({ url: `/pages/topic/detail?id=${item.id}` })
	}
</script>

<style scoped>
	.topic-list-page {
		min-height: 100vh;
		background-color: #f7f7f7;
	}

	.topic-items {
		padding: 10px 0;
	}

	.topic-card {
		margin: 0 12px 12px;
		background-color: #ffffff;
		border-radius: 4px;
		overflow: hidden;
	}

	.topic-cover {
		position: relative;
		width: 100%;
		height: 170px;
		background-color: #f0f0f0;
	}

	.topic-cover-img {
		width: 100%;
		height: 170px;
		display: block;
	}

	.topic-cover-img--empty {
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 12px;
		color: #b8b8b8;
	}

	.topic-cover-mask {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 0;
		padding: 26px 14px 12px;
		background-image: linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.45) 100%);
	}

	.topic-cover-title {
		display: block;
		font-size: 17px;
		color: #ffffff;
	}

	.topic-cover-read {
		display: block;
		margin-top: 6px;
		font-size: 12px;
		color: rgba(255, 255, 255, 0.85);
	}

	.topic-subtitle {
		padding: 12px 14px;
		font-size: 13px;
		color: #4a4f57;
		line-height: 19px;
	}

	.topic-end {
		padding: 10px 0 30px;
		text-align: center;
		font-size: 12px;
		color: #b8b8b8;
	}
</style>
