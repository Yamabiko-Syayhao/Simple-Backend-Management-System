import { request } from './request'

/** 首页轮播广告（按位置，默认首页） */
export function adBanners(data = {}) {
	return request({ url: '/ad/banners', method: 'POST', data })
}

/** 客户端可领取优惠券 */
export function couponClientList(data = {}) {
	return request({ url: '/coupon/clientList', method: 'POST', data })
}

/** 当前会员领取一张通用领券，数量和限领由服务端校验 */
export function couponClaim(data) {
	return request({ url: '/coupon/claim', method: 'POST', data })
}

/** 当前会员已领取的优惠券 */
export function couponMyList(data = {}) {
	return request({ url: '/coupon/myList', method: 'POST', data })
}
