import { request } from './request'

/** 客户端品牌商列表 */
export function brandClientList(data) {
	return request({ url: '/brand/clientList', method: 'POST', data })
}

/** 客户端品牌商详情 */
export function brandClientDetail(data) {
	return request({ url: '/brand/clientDetail', method: 'POST', data })
}
