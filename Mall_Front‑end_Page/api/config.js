/**
 * 接口地址配置
 *
 * H5 开发时如果遇到跨域，请确认后端 settings.ALLOW_ORIGINS 已放开当前端口
 * （本项目后端已内置 http://localhost:8080 / http://127.0.0.1:8080）。
 */

// 后端地址（不含 /api 前缀）
export const API_HOST = 'http://127.0.0.1:8100'

// 后端接口前缀
export const API_PREFIX = '/api'

export const BASE_URL = API_HOST + API_PREFIX
