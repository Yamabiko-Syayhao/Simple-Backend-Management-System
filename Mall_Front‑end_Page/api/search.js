import { request } from './request'

/** 我的搜索历史（会员 token） */
export function searchHistoryMyList(data = {}) {
	return request({ url: '/searchHistory/myList', method: 'POST', data })
}

/** 记录一次搜索 */
export function searchHistoryAdd(data) {
	return request({ url: '/searchHistory/add', method: 'POST', data })
}

/** 清空我的搜索历史 */
export function searchHistoryClear(data = {}) {
	return request({ url: '/searchHistory/clear', method: 'POST', data })
}
