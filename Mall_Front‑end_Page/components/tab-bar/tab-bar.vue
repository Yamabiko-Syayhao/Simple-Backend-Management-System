<template>
	<view class="tab-bar">
		<view
			v-for="item in items"
			:key="item.key"
			class="tab-item"
			@click="onTap(item)"
		>
			<view class="tab-icon" :class="{ 'tab-icon--active': current === item.key }">
				<image
					class="tab-icon-img"
					:src="current === item.key ? item.activeIcon : item.icon"
					mode="aspectFit"
				></image>
			</view>
			<text class="tab-label" :class="{ 'tab-label--active': current === item.key }">{{ item.label }}</text>
		</view>
	</view>
</template>

<script setup>
	/**
	 * 自定义底部导航
	 * 选中态：红色圆底 + 白色图标 + 红色文字（与设计稿一致）
	 * 用法：<tab-bar current="profile" />
	 */
	const props = defineProps({
		current: {
			type: String,
			default: 'featured'
		}
	})

	const items = [
		{
			key: 'featured',
			label: '精选',
			icon: '/static/icons/tab-featured.svg',
			activeIcon: '/static/icons/tab-featured-active.svg',
			path: '/pages/index/index'
		},
		{
			key: 'category',
			label: '分类',
			icon: '/static/icons/tab-category.svg',
			activeIcon: '/static/icons/tab-category-active.svg',
			path: '/pages/category/index'
		},
		{
			key: 'cart',
			label: '购物车',
			icon: '/static/icons/tab-cart.svg',
			activeIcon: '/static/icons/tab-cart-active.svg',
			path: '/pages/cart/index'
		},
		{
			key: 'profile',
			label: '我的',
			icon: '/static/icons/tab-profile.svg',
			activeIcon: '/static/icons/tab-profile-active.svg',
			path: '/pages/profile/index'
		}
	]

	const onTap = (item) => {
		if (item.key === props.current) return
		uni.redirectTo({ url: item.path })
	}
</script>

<style scoped>
	.tab-bar {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 99;
		display: flex;
		align-items: center;
		height: calc(56px + env(safe-area-inset-bottom));
		padding-bottom: env(safe-area-inset-bottom);
		background-color: #ffffff;
		border-top: 1px solid #f0f0f0;
	}

	.tab-item {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	.tab-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 26px;
		height: 26px;
	}

	.tab-icon--active {
		border-radius: 50%;
		background-color: #e93b3b;
	}

	.tab-icon-img {
		width: 22px;
		height: 22px;
		display: block;
	}

	.tab-icon--active .tab-icon-img {
		width: 15px;
		height: 15px;
	}

	.tab-label {
		margin-top: 2px;
		font-size: 11px;
		line-height: 14px;
		color: #8a8f99;
	}

	.tab-label--active {
		color: #e93b3b;
	}
</style>
