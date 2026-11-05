import { request } from './request'

/** 客户端进行中的团购 */
export function groupRuleClientList(data = {}) {
	return request({ url: '/groupRule/clientList', method: 'POST', data })
}
