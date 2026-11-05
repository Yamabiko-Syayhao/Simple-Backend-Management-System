<template>
	<view class="address-page">
		<nav-header :title="selectMode ? '选择收货地址' : '收货地址'"></nav-header>
		<view v-if="!loggedIn" class="address-state">
			<text>登录后管理收货地址</text>
			<button class="address-action" @click="goLogin">去登录</button>
		</view>
		<view v-else-if="loading && !loaded" class="address-state">正在加载地址…</view>
		<view v-else-if="failed" class="address-state">
			<text>地址暂时未能加载</text>
			<button class="address-action" :disabled="busy" @click="loadAddresses">重新加载</button>
		</view>
		<view v-else-if="loaded && !rows.length" class="address-state">
			<text>还没有收货地址</text>
			<text class="address-empty-desc">添加地址后，下次购买可直接使用</text>
		</view>
		<view v-else class="address-list">
			<view v-for="item in rows" :key="item.id" class="address-card">
				<view class="address-card-main" role="button" :aria-label="`${selectMode ? '选择' : '编辑'}${item.receiver_name}的地址`" @click="onAddress(item)">
					<view v-if="selectMode" class="address-radio" :class="{ 'address-radio--selected': selectedId === item.id }"><text v-if="selectedId === item.id">✓</text></view>
					<view class="address-card-info">
						<view class="address-person"><text class="address-name">{{ item.receiver_name }}</text><text class="address-mobile">{{ item.mobile }}</text><text v-if="item.is_default" class="address-badge">默认</text></view>
						<text class="address-location">{{ item.region }} {{ item.detail }}</text>
					</view>
					<text class="address-arrow">›</text>
				</view>
				<view class="address-card-tools">
					<button class="address-default" :class="{ 'address-default--active': item.is_default }" :disabled="busy || item.is_default" @click="setDefault(item)">{{ item.is_default ? '默认收货地址' : '设为默认' }}</button>
					<button class="address-edit" :disabled="busy" @click="editAddress(item)">编辑</button>
				</view>
			</view>
		</view>
		<view class="address-footer"><button class="address-add" :disabled="busy || !loggedIn" @click="addAddress">新增地址</button></view>
	</view>
</template>

<script setup>
	import { computed, ref } from 'vue'
	import { onLoad, onShow, onUnload } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { addressMyDefault, addressMyList } from '@/api/address.js'

	const rows = ref([])
	const selectMode = ref(false)
	const selectedId = ref(0)
	const loggedIn = ref(false)
	const loading = ref(false)
	const changing = ref(false)
	const loaded = ref(false)
	const failed = ref(false)
	const busy = computed(() => loading.value || changing.value)
	let disposed = false
	let requestVersion = 0
	let knownToken = ''

	const loadAddresses = async () => {
		if (loading.value || disposed) return
		const token = uni.getStorageSync('member_token') || ''
		loggedIn.value = Boolean(token)
		if (token !== knownToken) { rows.value = []; loaded.value = false; knownToken = token }
		if (!token) { rows.value = []; failed.value = false; loaded.value = true; return }
		const version = ++requestVersion
		loading.value = true
		try {
			const res = await addressMyList()
			if (disposed || version !== requestVersion || token !== uni.getStorageSync('member_token')) return
			rows.value = res.data && res.data.rows || []
			if (selectedId.value && !rows.value.some((item) => item.id === selectedId.value)) selectedId.value = 0
			loaded.value = true
			failed.value = false
		} catch (error) {
			if (!disposed && version === requestVersion) { failed.value = true; loggedIn.value = Boolean(uni.getStorageSync('member_token')) }
		} finally {
			if (!disposed && version === requestVersion) loading.value = false
		}
	}
	const goLogin = () => uni.navigateTo({ url: '/pages/login/login' })
	const editAddress = (item) => { if (!busy.value) uni.navigateTo({ url: `/pages/address/edit?id=${item.id}` }) }
	const addAddress = () => { if (!busy.value && loggedIn.value) uni.navigateTo({ url: '/pages/address/edit' }) }
	const onAddress = (item) => {
		if (busy.value || failed.value) return
		if (!selectMode.value) { editAddress(item); return }
		selectedId.value = item.id
		uni.$emit('address:selected', { id: item.id })
		if (getCurrentPages().length > 1) uni.navigateBack()
		else uni.redirectTo({ url: '/pages/order/confirm' })
	}
	const setDefault = async (item) => {
		if (busy.value || item.is_default) return
		changing.value = true
		const token = uni.getStorageSync('member_token')
		try {
			await addressMyDefault({ id: item.id })
			if (disposed || token !== uni.getStorageSync('member_token')) return
			uni.$emit('address:change')
			await loadAddresses()
			uni.showToast({ title: '默认地址已更新', icon: 'success' })
		} catch (error) { /* 请求层统一提示 */ }
		finally { if (!disposed) changing.value = false }
	}
	onLoad((options = {}) => {
		selectMode.value = options.select === '1'
		const id = Number(options.selected_id)
		selectedId.value = Number.isSafeInteger(id) && id > 0 ? id : 0
	})
	onShow(loadAddresses)
	onUnload(() => { disposed = true; requestVersion += 1 })
</script>

<style scoped>
	.address-page { max-width: 700px; min-height: 100vh; margin: 0 auto; padding-bottom: calc(84px + env(safe-area-inset-bottom)); background: #f4f4f4; }
	.address-list { padding: 12px; }
	.address-card { margin-bottom: 12px; border-radius: 9px; background: #ffffff; overflow: hidden; }
	.address-card-main { display: flex; align-items: center; gap: 12px; padding: 16px 13px; }
	.address-card-info { flex: 1; min-width: 0; }
	.address-person { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; font-size: 14px; line-height: 22px; }
	.address-name { font-size: 15px; }
	.address-mobile { color: #555555; }
	.address-badge { padding: 0 5px; border-radius: 3px; background: #fff0f1; color: #ed4145; font-size: 10px; line-height: 18px; }
	.address-location { display: block; margin-top: 6px; color: #777777; font-size: 12px; line-height: 20px; overflow-wrap: anywhere; }
	.address-arrow { color: #bbbbbb; font-size: 23px; }
	.address-radio { display: flex; align-items: center; justify-content: center; width: 20px; height: 20px; flex-shrink: 0; border: 1px solid #d2d2d2; border-radius: 50%; color: #ffffff; font-size: 12px; }
	.address-radio--selected { border-color: #ee4442; background: #ee4442; }
	.address-card-tools { display: flex; justify-content: space-between; padding: 6px 13px; border-top: 1px solid #f5f5f5; }
	.address-default, .address-edit { margin: 0; padding: 0; line-height: 28px; background: transparent; color: #888888; font-size: 11px; }
	.address-default--active, .address-default[disabled] { color: #ee4442; background: transparent; }
	.address-edit { padding: 0 5px 0 20px; color: #555555; }
	.address-default::after, .address-edit::after, .address-add::after, .address-action::after { border: 0; }
	.address-state { padding: 110px 20px; display: flex; align-items: center; flex-direction: column; color: #999999; font-size: 14px; text-align: center; }
	.address-empty-desc { margin-top: 12px; font-size: 12px; color: #aaaaaa; }
	.address-action { margin-top: 22px; padding: 0 24px; line-height: 34px; border-radius: 18px; font-size: 12px; color: #ffffff; background: #ee4442; }
	.address-footer { position: fixed; left: 0; right: 0; bottom: 0; z-index: 20; max-width: 700px; margin: 0 auto; padding: 9px 16px calc(9px + env(safe-area-inset-bottom)); background: #ffffff; }
	.address-add { height: 42px; margin: 0; border-radius: 23px; line-height: 42px; color: #ffffff; font-size: 14px; background: #ee4442; }
	.address-add[disabled] { color: #ffffff; background: #f2abab; }
</style>
