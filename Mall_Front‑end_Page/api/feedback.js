import { request } from './request'

/** 服务中心客服资料与可选反馈类型 */
export function feedbackContact() {
	return request({ url: '/feedback/contact', method: 'POST', data: {} })
}

/** 当前会员提交意见反馈，身份和账号由服务端取得 */
export function feedbackMySubmit(data) {
	return request({ url: '/feedback/mySubmit', method: 'POST', data })
}
