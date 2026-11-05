import { request } from './request'

/** 客户端商品列表 / 搜索
 * @param {Object} data { page, pageSize, keyword, scene: 'default'|'new'|'hot', brand_id, category_id }
 */
export function goodsClientList(data) {
	return request({ url: '/goods/clientList', method: 'POST', data })
}

/** 客户端商品详情 */
export function goodsClientDetail(data) {
	return request({ url: '/goods/clientDetail', method: 'POST', data })
}
