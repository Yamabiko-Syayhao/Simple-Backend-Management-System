<template>
	<view class="password-page"><nav-header title="密码设置" /><view class="password-form"><view v-for="field in fields" :key="field" class="password-field"><text>{{ field }}</text><input :placeholder="'暂未开放'" disabled /></view></view><text class="password-tip">密码修改暂未开放。如需重置密码，请前往服务中心联系管理员。</text><button class="password-placeholder" disabled>暂未开放密码修改</button><button class="password-service" @click="service">前往服务中心</button></view>
</template>
<script setup>
	const fields = ['手机号', '验证码', '新密码', '确认密码']
	const service = () => uni.navigateTo({ url: '/pages/profile/service' })
</script>
<style scoped>
	.password-page { min-height:100vh; max-width:700px; margin:auto; background:#f3f3f3; }
	.password-form { padding:0 16px; background:#fff; }
	.password-field { display:flex; align-items:center; gap:16px; min-height:46px; border-bottom:1px solid #f4f4f4; font-size:14px; }
	.password-field text { flex:0 0 82px; }
	.password-field input { flex:1; min-width:0; font-size:14px; }
	.password-tip { display:block; padding:18px 16px; font-size:12px; line-height:22px; color:#999; }
	.password-placeholder,.password-service { margin:14px 16px; font-size:14px; }
	.password-service { background:#fff; color:#d83b3b; }
	.password-service::after { border:0; }
</style>
