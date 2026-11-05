<template>
	<view class="nav-header">
		<view class="nav-back" @click="goBack">
			<text class="nav-back-arrow">‹</text>
			<text class="nav-back-text">返回</text>
		</view>
		<text class="nav-title">{{ title }}</text>
		<view class="nav-right"></view>
	</view>
</template>

<script setup>
	defineProps({
		title: {
			type: String,
			default: ''
		}
	})

	const goBack = () => {
		const pages = getCurrentPages()
		if (pages.length > 1) {
			uni.navigateBack()
		} else {
			uni.reLaunch({ url: '/pages/index/index' })
		}
	}
</script>

<style scoped>
	.nav-header {
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
		height: 44px;
		background-color: #ffffff;
		border-bottom: 1px solid #f2f2f2;
	}

	.nav-back {
		position: absolute;
		left: 12px;
		top: 0;
		bottom: 0;
		display: flex;
		align-items: center;
	}

	.nav-back-arrow {
		font-size: 20px;
		line-height: 20px;
		color: #4a90e2;
		margin-right: 2px;
	}

	.nav-back-text {
		font-size: 14px;
		color: #4a90e2;
	}

	.nav-title {
		font-size: 16px;
		font-weight: 500;
		color: #333333;
	}

	.nav-right {
		position: absolute;
		right: 12px;
		width: 40px;
		height: 1px;
	}
</style>
