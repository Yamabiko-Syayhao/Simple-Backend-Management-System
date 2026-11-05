import { request } from './request'

/** 服务端校验所选商品、地址、优惠券并计算确认订单金额 */
export function orderPreview(data) {
	return request({ url: '/order/preview', method: 'POST', data })
}

/** 按服务端报价与固定请求号创建订单，重试不重复下单 */
export function orderSubmit(data) {
	return request({ url: '/order/submit', method: 'POST', data })
}

/** 当前会员订单详情及支付方式（支付仅为占位展示） */
export function orderMyDetail(data) {
	return request({ url: '/order/myDetail', method: 'POST', data })
}

/** 当前报价对应的本人优惠券及不可使用原因 */
export function orderCouponList(data) {
	return request({ url: '/order/coupons', method: 'POST', data })
}

/** 当前会员的订单列表，按服务端订单状态分页 */
export function orderMyList(data = {}) {
	return request({ url: '/order/myList', method: 'POST', data })
}

/** 当前会员各订单状态数量 */
export function orderMySummary() {
	return request({ url: '/order/mySummary', method: 'POST', data: {} })
}

/** 删除本人已取消订单，是否可删由服务端确认 */
export function orderMyDeleted(data) {
	return request({ url: '/order/myDeleted', method: 'POST', data })
}
