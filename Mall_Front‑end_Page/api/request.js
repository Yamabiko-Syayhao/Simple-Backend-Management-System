import { BASE_URL } from './config'

/**
 * 统一请求封装
 * 约定与后端一致：{ code, msg, data, success }
 * code === 0 视为成功；11000 表示登录失效
 */
export function request(options = {}) {
	return new Promise((resolve, reject) => {
		const token = uni.getStorageSync('member_token') || ''

		uni.request({
			url: BASE_URL + (options.url || ''),
			method: options.method || 'POST',
			data: options.data || {},
			timeout: 15000,
			header: {
				'Content-Type': 'application/json',
				...(token ? { token } : {})
			},
			success: (res) => {
				// 旧账号的晚到响应不能写回新账号，也不能清除新账号会话。
				if (token !== (uni.getStorageSync('member_token') || '')) { reject(new Error('账号已切换')); return }
				const body = res.data

				// 非 JSON（例如后端未启动时的错误页）
				if (!body || typeof body !== 'object') {
					uni.showToast({ title: '服务异常，请稍后再试', icon: 'none' })
					reject(body)
					return
				}

				if (body.code === 0) {
					resolve(body)
					return
				}

				if (body.code === 11000) {
					uni.removeStorageSync('member_token')
					uni.removeStorageSync('member_info')
					uni.showToast({ title: '登录已失效，请重新登录', icon: 'none' })
					setTimeout(() => {
						if (!uni.getStorageSync('member_token')) uni.reLaunch({ url: '/pages/login/login' })
					}, 800)
					reject(body)
					return
				}

				uni.showToast({ title: body.msg || '请求失败', icon: 'none' })
				reject(body)
			},
			fail: (err) => {
				if (token !== (uni.getStorageSync('member_token') || '')) { reject(err); return }
				uni.showToast({ title: '网络异常：后端未启动或跨域被拦截', icon: 'none' })
				reject(err)
			}
		})
	})
}
