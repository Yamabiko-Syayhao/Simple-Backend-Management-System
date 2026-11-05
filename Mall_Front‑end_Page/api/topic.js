import { request } from './request'

/** 客户端专题列表 */
export function topicClientList(data) {
	return request({ url: '/topic/clientList', method: 'POST', data })
}

/** 客户端专题详情（含在售商品） */
export function topicClientDetail(data) {
	return request({ url: '/topic/clientDetail', method: 'POST', data })
}
