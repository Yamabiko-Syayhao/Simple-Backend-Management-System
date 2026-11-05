import { request } from './request'

/** 当前会员的购物车与服务端合计 */
export function cartList(data = {}) {
	return request({ url: '/cart/list', method: 'POST', data })
}

/** 添加真实库存商品；相同库存项合并数量 */
export function cartAdd(data) {
	return request({ url: '/cart/add', method: 'POST', data })
}

/** 修改本人购物车条目的数量 */
export function cartUpdate(data) {
	return request({ url: '/cart/update', method: 'POST', data })
}

/** 单选、全选或取消选择 */
export function cartChecked(data) {
	return request({ url: '/cart/checked', method: 'POST', data })
}

/** 物理删除本人购物车条目 */
export function cartDeleted(data) {
	return request({ url: '/cart/deleted', method: 'POST', data })
}

/** 当前会员购物车商品总件数 */
export function cartCount(data = {}) {
	return request({ url: '/cart/count', method: 'POST', data })
}
