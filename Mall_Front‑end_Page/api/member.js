import { request } from './request'
import { BASE_URL } from './config'

/** 会员登录 */
export function memberLogin(data) {
	return request({ url: '/member/login', method: 'POST', data })
}

/** 会员注册 */
export function memberRegister(data) {
	return request({ url: '/member/register', method: 'POST', data })
}

/** 当前登录会员信息 */
export function memberProfile() {
	return request({ url: '/member/profile', method: 'POST', data: {} })
}

/** 退出登录 */
export function memberLogout() {
	return request({ url: '/member/logout', method: 'POST', data: {} })
}

/** 仅更新本人昵称、性别，头像由专用上传接口保存 */
export function memberUpdateProfile(data) {
	return request({ url: '/member/updateProfile', method: 'POST', data })
}

/** 校验当前登录密码后修改本人手机号 */
export function memberChangeMobile(data) {
	return request({ url: '/member/changeMobile', method: 'POST', data })
}

/** 上传头像并保存到当前会员，沿用统一响应格式 */
export function memberUploadAvatar(filePath) {
	const token = uni.getStorageSync('member_token') || ''
	return new Promise((resolve, reject) => {
		uni.uploadFile({
			url: BASE_URL + '/member/uploadAvatar', filePath, name: 'file',
			header: { token }, timeout: 30000,
			success: (res) => {
				if (token !== uni.getStorageSync('member_token')) { reject(new Error('账号已切换')); return }
				let body
				try { body = typeof res.data === 'string' ? JSON.parse(res.data) : res.data } catch (error) { body = null }
				if (body && body.code === 0) { resolve(body); return }
				if (body && body.code === 11000) {
					uni.removeStorageSync('member_token')
					uni.removeStorageSync('member_info')
					uni.reLaunch({ url: '/pages/login/login' })
				}
				uni.showToast({ title: body && body.msg || '头像上传失败，请稍后重试', icon: 'none' })
				reject(body || new Error('上传失败'))
			},
			fail: (error) => {
				if (token === uni.getStorageSync('member_token')) uni.showToast({ title: '头像上传失败，请检查网络后重试', icon: 'none' })
				reject(error)
			}
		})
	})
}
