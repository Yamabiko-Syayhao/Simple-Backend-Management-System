<template>
	<view class="search-page">
		<!-- 顶部搜索 -->
		<view class="search-header">
			<text class="back-arrow" @click="goBack">‹</text>
			<view class="search-box">
				<image class="search-icon" src="/static/icons/ic-search.svg" mode="aspectFit"></image>
				<input
					v-model="keyword"
					class="search-input"
					type="text"
					placeholder="请输入商品名称"
					placeholder-class="search-placeholder"
					confirm-type="search"
					:focus="autoFocus"
					@confirm="onSearch"
				/>
			</view>
			<text class="search-action" @click="onSearch">搜索</text>
		</view>

		<!-- 历史搜索 -->
		<view class="history-head">
			<text class="history-title">历史搜索</text>
			<view v-if="history.length" class="history-clear" @click="onClear">
				<image class="history-clear-icon" src="/static/icons/ic-trash.svg" mode="aspectFit"></image>
				<text class="history-clear-text">清空历史记录</text>
			</view>
		</view>
		<view v-if="history.length" class="history-tags">
			<view
				v-for="item in history"
				:key="item.id"
				class="history-tag"
				@click="onTag(item.keyword)"
			>
				{{ item.keyword }}
			</view>
		</view>
		<view v-else class="history-empty">暂无搜索历史</view>

		<!-- 搜索结果 -->
		<view v-if="searched" class="result-block">
			<view class="result-head">
				<text class="result-title">搜索结果</text>
				<text class="result-count">共 {{ total }} 件</text>
			</view>
			<goods-row
				v-for="item in results"
				:key="item.id"
				:item="item"
				@tap="goDetail(item)"
			></goods-row>
			<view v-if="!results.length" class="result-empty">没有找到相关商品</view>
		</view>
	</view>
</template>

<script setup>
	import { ref } from 'vue'
	import { onLoad } from '@dcloudio/uni-app'
	import GoodsRow from '@/components/goods-row/goods-row.vue'
	import { searchHistoryMyList, searchHistoryAdd, searchHistoryClear } from '@/api/search.js'
	import { goodsClientList } from '@/api/goods.js'

	const keyword = ref('')
	const history = ref([])
	const results = ref([])
	const total = ref(0)
	const searched = ref(false)
	const autoFocus = ref(false)

	const loadHistory = async () => {
		try {
			const res = await searchHistoryMyList()
			history.value = res.data || []
		} catch (e) {
			history.value = []
		}
	}

	onLoad((options) => {
		autoFocus.value = Boolean(options && options.focus)
		loadHistory()
	})

	const goBack = () => {
		const pages = getCurrentPages()
		if (pages.length > 1) uni.navigateBack()
		else uni.reLaunch({ url: '/pages/index/index' })
	}

	const onSearch = async () => {
		const value = (keyword.value || '').trim()
		if (!value) {
			uni.showToast({ title: '请输入商品名称', icon: 'none' })
			return
		}

		try {
			const res = await goodsClientList({ page: 1, pageSize: 30, keyword: value })
			results.value = (res.data && res.data.rows) || []
			total.value = (res.data && res.data.rowTotal) || 0
			searched.value = true
		} catch (e) {
			results.value = []
			searched.value = true
		}

		// 搜索成功后写入历史（同一关键字只保留最新一条，后端已处理）
		try {
			await searchHistoryAdd({ keyword: value })
			await loadHistory()
		} catch (e) {
			// 历史记录失败不影响搜索结果
		}
	}

	const onTag = (value) => {
		keyword.value = value
		onSearch()
	}

	const onClear = () => {
		uni.showModal({
			title: '提示',
			content: '确定要清空历史记录吗？',
			success: async (res) => {
				if (!res.confirm) return
				try {
					await searchHistoryClear()
					history.value = []
					uni.showToast({ title: '已清空', icon: 'none' })
				} catch (e) {
					// 错误提示由 request 统一处理
				}
			}
		})
	}

	const goDetail = (item) => {
		uni.navigateTo({ url: `/pages/goods/detail?id=${item.id}` })
	}
</script>

<style scoped>
	.search-page {
		min-height: 100vh;
		background-color: #ffffff;
	}

	.search-header {
		display: flex;
		align-items: center;
		padding: 8px 12px;
		border-bottom: 1px solid #f5f5f5;
	}

	.back-arrow {
		width: 24px;
		font-size: 22px;
		line-height: 22px;
		color: #4a90e2;
	}

	.search-box {
		flex: 1;
		display: flex;
		align-items: center;
		height: 32px;
		padding: 0 10px;
		border-radius: 16px;
		background-color: #f5f5f5;
	}

	.search-icon {
		width: 14px;
		height: 14px;
		margin-right: 6px;
		opacity: 0.55;
	}

	.search-input {
		flex: 1;
		height: 30px;
		font-size: 13px;
		color: #333333;
		background-color: transparent;
	}

	.search-placeholder {
		font-size: 13px;
		color: #9aa0a6;
	}

	.search-action {
		margin-left: 10px;
		font-size: 14px;
		color: #333333;
	}

	.history-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 16px 16px 8px;
	}

	.history-title {
		font-size: 14px;
		color: #333333;
	}

	.history-clear {
		display: flex;
		align-items: center;
	}

	.history-clear-icon {
		width: 13px;
		height: 13px;
		margin-right: 4px;
		opacity: 0.6;
	}

	.history-clear-text {
		font-size: 12px;
		color: #9aa0a6;
	}

	.history-tags {
		display: flex;
		flex-wrap: wrap;
		padding: 0 16px;
	}

	.history-tag {
		margin: 0 8px 8px 0;
		padding: 5px 12px;
		font-size: 12px;
		color: #4a4f57;
		background-color: #f5f5f5;
		border-radius: 13px;
	}

	.history-empty {
		padding: 6px 16px 20px;
		font-size: 12px;
		color: #b8b8b8;
	}

	.result-block {
		margin-top: 6px;
		border-top: 8px solid #f5f5f5;
	}

	.result-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 12px 16px 6px;
	}

	.result-title {
		font-size: 14px;
		font-weight: 600;
		color: #333333;
	}

	.result-count {
		font-size: 12px;
		color: #9aa0a6;
	}

	.result-empty {
		padding: 40px 0;
		text-align: center;
		font-size: 13px;
		color: #b8b8b8;
	}
</style>
