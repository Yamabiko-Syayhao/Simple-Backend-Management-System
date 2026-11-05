<template>
	<view class="address-edit-page">
		<nav-header :title="addressId ? '编辑地址' : '新增地址'"></nav-header>
		<view v-if="loading" class="address-edit-state">正在加载…</view>
		<view v-else-if="failed" class="address-edit-state">
			<text>{{ invalidId ? '地址参数无效' : '地址或地区数据加载失败' }}</text>
			<button v-if="!invalidId" class="address-retry" @click="load">重新加载</button>
			<button v-else class="address-retry" @click="back">返回地址列表</button>
		</view>
		<view v-else-if="!loggedIn" class="address-edit-state"><text>请先登录后添加地址</text><button class="address-retry" @click="goLogin">去登录</button></view>
		<view v-else class="address-edit-form">
			<view class="address-field"><text class="address-field-label">姓名</text><input v-model="form.receiver_name" class="address-input" placeholder="收货人姓名" maxlength="64" :disabled="busy" /></view>
			<view class="address-field"><text class="address-field-label">电话</text><input v-model="form.mobile" class="address-input" type="number" placeholder="收货人手机号" maxlength="11" :disabled="busy" /></view>
			<view class="address-field address-region-field" role="button" aria-label="选择省市区" @click="openRegions"><text class="address-field-label">地区</text><text class="address-region-value" :class="{ 'address-placeholder': !regionText }">{{ regionText || '选择省 / 市 / 区' }}</text><text class="address-region-arrow">›</text></view>
			<view class="address-field"><text class="address-field-label">详细地址</text><textarea v-model="form.detail" class="address-detail-input" placeholder="街道门牌、楼层房间号等信息" maxlength="255" auto-height :disabled="busy" /></view>
			<view class="address-default-field"><text>设为默认收货地址</text><switch :checked="form.is_default" :disabled="busy" color="#ee4442" @change="form.is_default = $event.detail.value" /></view>
			<view class="address-form-actions"><button class="address-save" :loading="saving" :disabled="busy" @click="save">保存</button><button v-if="addressId" class="address-delete" :disabled="busy" @click="remove">删除</button></view>
		</view>
		<view v-if="regionVisible" class="region-popup">
			<view class="region-mask" @click="regionVisible = false" @touchmove.stop.prevent></view>
			<view class="region-panel">
				<view class="region-toolbar"><button @click="regionVisible = false">取消</button><text>选择地区</text><button class="region-confirm" :disabled="!pickerValid" @click="confirmRegion">确认</button></view>
				<picker-view class="region-picker" :value="pickerIndexes" indicator-style="height: 44px;" @change="changeRegion">
					<picker-view-column><view v-for="item in provinces" :key="item.id" class="region-picker-item">{{ item.name }}</view></picker-view-column>
					<picker-view-column><view v-for="item in cities" :key="item.id" class="region-picker-item">{{ item.name }}</view><view v-if="!cities.length" class="region-picker-item">暂无城市</view></picker-view-column>
					<picker-view-column><view v-for="item in districts" :key="item.id" class="region-picker-item">{{ item.name }}</view><view v-if="!districts.length" class="region-picker-item">暂无区县</view></picker-view-column>
				</picker-view>
				<text v-if="!pickerValid" class="region-incomplete">该地区暂无完整省市区数据，请联系管理员补充行政区域</text>
			</view>
		</view>
	</view>
</template>

<script setup>
	import { computed, reactive, ref } from 'vue'
	import { onLoad, onUnload } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { addressMyDeleted, addressMyDetail, addressMySave, regionTree } from '@/api/address.js'

	const addressId = ref(0)
	const form = reactive({ receiver_name: '', mobile: '', region_ids: [], detail: '', is_default: false })
	const regions = ref([])
	const loading = ref(false)
	const saving = ref(false)
	const deleting = ref(false)
	const confirming = ref(false)
	const failed = ref(false)
	const invalidId = ref(false)
	const loggedIn = ref(false)
	const regionVisible = ref(false)
	const pickerIndexes = ref([0, 0, 0])
	const busy = computed(() => loading.value || saving.value || deleting.value || confirming.value)
	const provinces = computed(() => regions.value)
	const cities = computed(() => (provinces.value[pickerIndexes.value[0]] || {}).children || [])
	const districts = computed(() => (cities.value[pickerIndexes.value[1]] || {}).children || [])
	const pickerValid = computed(() => Boolean(provinces.value[pickerIndexes.value[0]] && cities.value[pickerIndexes.value[1]] && districts.value[pickerIndexes.value[2]]))
	const regionText = computed(() => {
		const province = provinces.value.find((item) => item.id === form.region_ids[0])
		const city = province && (province.children || []).find((item) => item.id === form.region_ids[1])
		const district = city && (city.children || []).find((item) => item.id === form.region_ids[2])
		return province && city && district ? [province.name, city.name, district.name].join(' ') : ''
	})
	let disposed = false
	let requestVersion = 0

	const normalizeTree = (rows) => rows.filter((item) => Number(item.level) === 1 && Number(item.parent_id) === 0).map((province) => ({
		...province, id: Number(province.id), children: (province.children || []).filter((item) => Number(item.level) === 2 && Number(item.parent_id) === Number(province.id)).map((city) => ({
			...city, id: Number(city.id), children: (city.children || []).filter((item) => Number(item.level) === 3 && Number(item.parent_id) === Number(city.id)).map((district) => ({ ...district, id: Number(district.id) }))
		}))
	}))
	const load = async () => {
		if (loading.value || disposed || invalidId.value) return
		const token = uni.getStorageSync('member_token') || ''
		loggedIn.value = Boolean(token)
		if (!token) return
		const version = ++requestVersion
		loading.value = true
		failed.value = false
		try {
			const [regionRes, addressRes] = await Promise.all([regionTree(), addressId.value ? addressMyDetail({ id: addressId.value }) : Promise.resolve(null)])
			if (disposed || version !== requestVersion || token !== uni.getStorageSync('member_token')) return
			regions.value = normalizeTree(Array.isArray(regionRes.data) ? regionRes.data : [])
			if (addressRes) {
				const row = addressRes.data || {}
				Object.assign(form, { receiver_name: row.receiver_name || '', mobile: row.mobile || '', region_ids: (row.region_ids || []).map(Number), detail: row.detail || '', is_default: Boolean(row.is_default) })
			}
		} catch (error) { if (!disposed && version === requestVersion) failed.value = true }
		finally { if (!disposed && version === requestVersion) loading.value = false }
	}
	const openRegions = () => {
		if (busy.value) return
		if (!regions.value.length) { uni.showToast({ title: '暂无可用行政区域，请联系管理员', icon: 'none' }); return }
		let provinceIndex = provinces.value.findIndex((item) => item.id === form.region_ids[0])
		if (provinceIndex < 0) provinceIndex = 0
		const cityRows = provinces.value[provinceIndex].children || []
		let cityIndex = cityRows.findIndex((item) => item.id === form.region_ids[1])
		if (cityIndex < 0) cityIndex = 0
		const districtRows = (cityRows[cityIndex] || {}).children || []
		let districtIndex = districtRows.findIndex((item) => item.id === form.region_ids[2])
		if (districtIndex < 0) districtIndex = 0
		pickerIndexes.value = [provinceIndex, cityIndex, districtIndex]
		regionVisible.value = true
	}
	const changeRegion = (event) => {
		const next = (event.detail.value || [0, 0, 0]).map((value) => Math.max(0, Number(value) || 0))
		const current = pickerIndexes.value
		if (next[0] !== current[0]) pickerIndexes.value = [Math.min(next[0], Math.max(0, provinces.value.length - 1)), 0, 0]
		else if (next[1] !== current[1]) pickerIndexes.value = [current[0], Math.min(next[1], Math.max(0, cities.value.length - 1)), 0]
		else pickerIndexes.value = [current[0], current[1], Math.min(next[2], Math.max(0, districts.value.length - 1))]
	}
	const confirmRegion = () => {
		if (!pickerValid.value) return
		form.region_ids = [provinces.value[pickerIndexes.value[0]].id, cities.value[pickerIndexes.value[1]].id, districts.value[pickerIndexes.value[2]].id]
		regionVisible.value = false
	}
	const goLogin = () => uni.navigateTo({ url: '/pages/login/login' })
	const back = () => {
		if (getCurrentPages().length > 1) uni.navigateBack()
		else uni.redirectTo({ url: '/pages/address/index' })
	}
	const save = async () => {
		if (busy.value) return
		const name = form.receiver_name.trim(), mobile = form.mobile.trim(), detail = form.detail.trim()
		let message = ''
		if (!name) message = '请填写收货人姓名'
		else if (!/^1[3-9]\d{9}$/.test(mobile)) message = '请输入正确的11位手机号码'
		else if (!regionText.value || form.region_ids.length !== 3) message = '请选择完整的省市区'
		else if (!detail) message = '请填写详细地址'
		if (message) { uni.showToast({ title: message, icon: 'none' }); return }
		saving.value = true
		const token = uni.getStorageSync('member_token')
		try {
			const res = await addressMySave({ ...(addressId.value ? { id: addressId.value } : {}), receiver_name: name, mobile, region_ids: form.region_ids, detail, is_default: form.is_default })
			if (disposed || token !== uni.getStorageSync('member_token')) return
			uni.$emit('address:change', { id: res.data && res.data.id })
			uni.showToast({ title: '地址已保存', icon: 'success' })
			back()
		} catch (error) { /* 请求层统一提示 */ }
		finally { if (!disposed) saving.value = false }
	}
	const remove = async () => {
		if (busy.value || !addressId.value) return
		confirming.value = true
		const confirmed = await new Promise((resolve) => uni.showModal({ title: '删除地址', content: '确定删除这个收货地址吗？', confirmColor: '#ee4442', success: (result) => resolve(result.confirm), fail: () => resolve(false) }))
		confirming.value = false
		if (!confirmed || disposed) return
		deleting.value = true
		const token = uni.getStorageSync('member_token')
		try {
			await addressMyDeleted({ id: addressId.value })
			if (disposed || token !== uni.getStorageSync('member_token')) return
			uni.$emit('address:change', { deleted_id: addressId.value })
			uni.showToast({ title: '地址已删除', icon: 'success' })
			back()
		} catch (error) { /* 请求层统一提示 */ }
		finally { if (!disposed) deleting.value = false }
	}
	onLoad((options = {}) => {
		if (Object.prototype.hasOwnProperty.call(options, 'id')) {
			const id = Number(options.id)
			if (!Number.isSafeInteger(id) || id <= 0) { invalidId.value = true; failed.value = true; loggedIn.value = Boolean(uni.getStorageSync('member_token')); return }
			addressId.value = id
		}
		load()
	})
	onUnload(() => { disposed = true; requestVersion += 1 })
</script>

<style scoped>
	.address-edit-page { max-width: 700px; min-height: 100vh; margin: 0 auto; padding-bottom: calc(40px + env(safe-area-inset-bottom)); background: #f5f5f5; }
	.address-edit-form { margin-top: 12px; background: #ffffff; }
	.address-field { min-height: 54px; padding: 13px 16px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #f5f5f5; }
	.address-field-label { flex: 0 0 62px; color: #555555; font-size: 13px; line-height: 22px; }
	.address-input { flex: 1; min-width: 0; height: 28px; color: #333333; font-size: 14px; }
	.address-detail-input { flex: 1; min-width: 0; min-height: 44px; font-size: 13px; line-height: 22px; }
	.address-region-value { flex: 1; min-width: 0; color: #333333; font-size: 13px; line-height: 22px; overflow-wrap: anywhere; }
	.address-placeholder { color: #aaaaaa; }
	.address-region-arrow { color: #aaaaaa; font-size: 23px; }
	.address-default-field { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 17px 16px; color: #555555; font-size: 13px; }
	.address-form-actions { padding: 28px 16px 34px; background: #f5f5f5; }
	.address-save { height: 43px; line-height: 43px; border-radius: 23px; background: #ee4442; color: #ffffff; font-size: 14px; }
	.address-delete { height: 43px; margin-top: 12px; line-height: 43px; border: 1px solid #e3e3e3; border-radius: 23px; background: #ffffff; color: #666666; font-size: 14px; }
	.address-save[disabled] { color: #ffffff; background: #f3aaaa; }
	.address-save::after, .address-delete::after, .address-retry::after, .region-toolbar button::after { border: 0; }
	.address-edit-state { padding: 110px 20px; text-align: center; color: #999999; font-size: 13px; }
	.address-retry { display: block; width: 116px; margin-top: 20px; line-height: 34px; border-radius: 18px; background: #ee4442; color: #ffffff; font-size: 12px; }
	.region-popup { position: fixed; z-index: 1000; inset: 0; }
	.region-mask { position: absolute; inset: 0; background: rgba(0, 0, 0, 0.58); }
	.region-panel { position: absolute; left: 0; right: 0; bottom: 0; max-width: 700px; margin: 0 auto; padding-bottom: env(safe-area-inset-bottom); overflow: hidden; border-radius: 18px 18px 0 0; background: #ffffff; }
	.region-toolbar { display: flex; align-items: center; justify-content: space-between; min-height: 54px; padding: 0 8px; border-bottom: 1px solid #f4f4f4; color: #777777; font-size: 14px; }
	.region-toolbar button { margin: 0; padding: 0 10px; line-height: 40px; font-size: 13px; color: #999999; background: transparent; }
	.region-toolbar .region-confirm { color: #4a90e2; }
	.region-toolbar .region-confirm[disabled] { color: #cccccc; }
	.region-picker { height: 244px; width: 100%; }
	.region-picker-item { display: flex; align-items: center; justify-content: center; padding: 0 5px; line-height: 44px; text-align: center; font-size: 15px; }
	.region-incomplete { display: block; padding: 8px 16px 15px; color: #b57d35; text-align: center; font-size: 11px; line-height: 18px; }
	@media (max-width: 360px) { .address-field { padding: 12px; gap: 8px; } .address-field-label { flex-basis: 58px; } .region-picker-item { font-size: 13px; } }
</style>
