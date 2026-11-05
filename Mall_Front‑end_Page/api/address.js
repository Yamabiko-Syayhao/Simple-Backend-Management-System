import { request } from './request'

/** 当前会员的收货地址 */
export function addressMyList(data = {}) {
	return request({ url: '/address/myList', method: 'POST', data })
}

export function addressMyDetail(data) {
	return request({ url: '/address/myDetail', method: 'POST', data })
}

export function addressMySave(data) {
	return request({ url: '/address/mySave', method: 'POST', data })
}

export function addressMyDeleted(data) {
	return request({ url: '/address/myDeleted', method: 'POST', data })
}

export function addressMyDefault(data) {
	return request({ url: '/address/myDefault', method: 'POST', data })
}

/** 与管理后台共用的行政区域树 */
export function regionTree(data = {}) {
	return request({ url: '/region/tree', method: 'POST', data })
}
