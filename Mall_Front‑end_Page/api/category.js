import { request } from './request'

/** 客户端商品分类（一级分类，首页快捷入口用） */
export function categoryClientList(data = {}) {
	return request({ url: '/category/clientList', method: 'POST', data })
}

/** 客户端完整两级类目；分类页与分类商品页共用 */
export function categoryClientTree(data = {}) {
	return request({ url: '/category/clientTree', method: 'POST', data })
}
