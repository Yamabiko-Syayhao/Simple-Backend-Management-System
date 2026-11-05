<template>
	<view class="member-faq-page">
		<view class="member-faq-header"><nav-header title="常见问题" /><view class="member-faq-search"><input v-model="keyword" class="member-faq-search-input" placeholder="请输入问题关键词" maxlength="100" confirm-type="search" @confirm="search" /><button class="member-faq-search-button" @click="search">搜索</button></view></view>
		<view class="member-faq-list"><view v-for="item in rows" :key="item.id" class="member-faq-item"><view class="member-faq-question" role="button" :aria-label="item.question" :aria-expanded="expandedId === item.id" @click="expandedId = expandedId === item.id ? 0 : item.id"><text>{{ item.question }}</text><text class="member-faq-arrow">{{ expandedId === item.id ? '−' : '＋' }}</text></view><text v-if="expandedId === item.id" class="member-faq-answer">{{ item.answer || '暂无回复' }}</text></view></view>
		<view v-if="loading" class="member-faq-state">正在加载常见问题…</view>
		<view v-else-if="failed" class="member-faq-state"><text>常见问题加载失败</text><button class="member-faq-retry" @click="load(false)">重新加载</button></view>
		<view v-else-if="loaded && !rows.length" class="member-faq-state">{{ query ? '没有找到相关问题' : '暂无常见问题' }}</view>
		<button v-else-if="hasMore" class="member-faq-more" @click="load(false)">加载更多</button>
		<view v-else-if="loaded" class="member-faq-end">没有更多了</view>
	</view>
</template>

<script setup>
	import { computed, ref } from 'vue'
	import { onLoad, onReachBottom, onUnload } from '@dcloudio/uni-app'
	import NavHeader from '@/components/nav-header/nav-header.vue'
	import { faqList } from '@/api/faq.js'
	const rows = ref([]), keyword = ref(''), query = ref(''), page = ref(0), total = ref(0), loading = ref(false), loaded = ref(false), failed = ref(false), expandedId = ref(0)
	const hasMore = computed(() => loaded.value && rows.value.length < total.value)
	let disposed = false, version = 0
	const load = async (reset = false) => {
		if (disposed || (!reset && loading.value)) return
		if (reset) { version += 1; rows.value = []; page.value = 0; total.value = 0; loaded.value = false; loading.value = false; expandedId.value = 0 }
		const requestId = ++version, nextPage = page.value + 1
		loading.value = true; failed.value = false
		try {
			const res = await faqList({ page: nextPage, pageSize: 20, ...(query.value ? { question: query.value } : {}) })
			if (disposed || requestId !== version) return
			const data = res.data || {}, nextRows = Array.isArray(data.rows) ? data.rows : []
			rows.value = nextPage === 1 ? nextRows : rows.value.concat(nextRows); page.value = nextPage; total.value = Number(data.rowTotal) || 0; loaded.value = true
		} catch (error) { if (!disposed && requestId === version) failed.value = true }
		finally { if (!disposed && requestId === version) loading.value = false }
	}
	const search = () => { query.value = keyword.value.trim(); load(true) }
	onLoad(() => load(true))
	onReachBottom(() => { if (hasMore.value && !failed.value) load(false) })
	onUnload(() => { disposed = true; version += 1 })
</script>

<style scoped>
	.member-faq-page { max-width: 700px; min-height: 100vh; margin: 0 auto; padding-bottom: calc(24px + env(safe-area-inset-bottom)); background: #f3f3f3; }
	.member-faq-header { position: sticky; top: 0; z-index: 10; background: #ffffff; }
	.member-faq-search { display: flex; align-items: center; gap: 10px; padding: 14px 16px; }
	.member-faq-search-input { flex: 1; min-width: 0; height: 34px; padding: 0 12px; border-radius: 18px; background: #f6f6f6; font-size: 13px; }
	.member-faq-search-button { margin: 0; padding: 0 15px; border-radius: 18px; background: #ee4442; color: #ffffff; font-size: 13px; line-height: 34px; }
	.member-faq-list { margin-top: 10px; background: #ffffff; }
	.member-faq-item { padding: 0 16px; border-bottom: 1px solid #f3f3f3; }
	.member-faq-question { display: flex; justify-content: space-between; align-items: center; gap: 16px; min-height: 56px; padding: 14px 0; font-size: 14px; line-height: 22px; }
	.member-faq-question > text:first-child { flex: 1; min-width: 0; overflow-wrap: anywhere; }
	.member-faq-arrow { flex-shrink: 0; color: #aaaaaa; font-size: 18px; }
	.member-faq-answer { display: block; padding: 0 0 18px; white-space: pre-wrap; overflow-wrap: anywhere; color: #888888; font-size: 13px; line-height: 23px; }
	.member-faq-state { padding: 70px 20px; color: #999999; text-align: center; font-size: 13px; line-height: 22px; }
	.member-faq-state text { display: block; }
	.member-faq-retry, .member-faq-more { width: max-content; margin: 18px auto; padding: 0 22px; border-radius: 18px; color: #ee4442; background: #ffffff; font-size: 12px; line-height: 34px; }
	.member-faq-end { padding: 24px 16px; color: #999999; text-align: center; font-size: 12px; }
	.member-faq-search-button::after, .member-faq-retry::after, .member-faq-more::after { border: 0; }
	@media (max-width: 360px) { .member-faq-search { padding: 12px; gap: 8px; } .member-faq-question { gap: 10px; font-size: 13px; } }
</style>
