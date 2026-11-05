import { request } from './request'

/** 后台维护的常见问题，客户端只读 */
export function faqList(data = {}) {
	return request({ url: '/faq/list', method: 'POST', data })
}
