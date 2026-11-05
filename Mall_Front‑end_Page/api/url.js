import { API_HOST } from './config'

/**
 * 后端上传的图片存的是相对路径（如 /api/files/2026/10/30/xxx.jpg），
 * 客户端 H5 直接用在 <image src> 上会解析到前端域名导致 404，
 * 所以统一在这里拼上后端地址。
 *
 * - http(s):// 或 // 开头：原样返回
 * - data: / blob:：原样返回
 * - / 开头：拼 API_HOST
 * - 其它：补一个 / 再拼
 */
export function imageUrl(path) {
	if (!path) return ''
	const value = String(path).trim()
	if (!value) return ''
	if (/^(https?:)?\/\//i.test(value)) return value
	if (/^(data|blob):/i.test(value)) return value
	if (value.charAt(0) === '/') return API_HOST + value
	return API_HOST + '/' + value
}

/** 富文本里的图片地址也要补全后端域名（兼容单双引号） */
export function rewriteHtmlImages(html) {
	if (!html) return ''
	return String(html).replace(/(src=["'])\/(?!\/)/g, (_match, prefix) => `${prefix}${API_HOST}/`)
}
