import { request } from './request'

/** 当前会员收藏的商品 */
export function favoriteMyList(data = {}) {
	return request({ url: '/favorite/myList', method: 'POST', data })
}

/** 取消本人一条收藏，不删除商品 */
export function favoriteMyDeleted(data) {
	return request({ url: '/favorite/myDeleted', method: 'POST', data })
}

/** 幂等设置本人商品收藏状态 */
export function favoriteMySet(data) {
	return request({ url: '/favorite/mySet', method: 'POST', data })
}
