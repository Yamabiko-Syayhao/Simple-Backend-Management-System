import {createRouter, createWebHashHistory, NavigationGuardNext, RouteLocationNormalized} from 'vue-router';
import {nextTick} from 'vue';
import NProgress from 'nprogress';
import 'nprogress/nprogress.css';
import {storeToRefs} from 'pinia';
import {NextLoading} from '/@/utils/loading';
import {useKeepALiveNames} from '/@/stores/keepAliveNames';
import {useRoutesList} from '/@/stores/routesList';
import {useThemeConfig} from '/@/stores/themeConfig';
import {Session} from '/@/utils/storage';
import {notFoundAndNoPower, staticRoutes} from '/@/router/route';
import {initFrontEndControlRoutes} from '/@/router/frontEnd';
import {initBackEndControlRoutes} from '/@/router/backEnd';

/**
 * 1、前端控制路由时：isRequestRoutes 为 false，需要写 roles，需要走 setFilterRoute 方法。
 * 2、后端控制路由时：isRequestRoutes 为 true，不需要写 roles，不需要走 setFilterRoute 方法），
 * 相关方法已拆解到对应的 `backEnd.ts` 与 `frontEnd.ts`（他们互不影响，不需要同时改 2 个文件）。
 * 特别说明：
 * 1、前端控制：路由菜单由前端去写（无菜单管理界面，有角色管理界面），角色管理中有 roles 属性，需返回到 userInfo 中。
 * 2、后端控制：路由菜单由后端返回（有菜单管理界面、有角色管理界面）
 */


/**
 * 创建一个可以被 Vue 应用程序使用的路由实例
 * @method createRouter(options: RouterOptions): Router
 * @link 参考：https://next.router.vuejs.org/zh/api/#createrouter
 */
export const router = createRouter({
	history: createWebHashHistory(),
	routes: [...notFoundAndNoPower, ...staticRoutes],
});

/**
 * 路由多级嵌套数组处理成一维数组
 * @param arr 传入路由菜单数据数组
 * @returns 返回处理后的一维路由菜单数组
 */
export function formatFlatteningRoutes(arr: any) {
	if (arr.length <= 0) return false;
	for (let i = 0; i < arr.length; i++) {
		if (arr[i].children) {
			arr = arr.slice(0, i + 1).concat(arr[i].children, arr.slice(i + 1));
		}
	}
	return arr;
}

/**
 * 一维数组处理成多级嵌套数组（只保留二级：也就是二级以上全部处理成只有二级，keep-alive 支持二级缓存）
 * @description isKeepAlive 处理 `name` 值，进行缓存。顶级关闭，全部不缓存
 * @link 参考：https://v3.cn.vuejs.org/api/built-in-components.html#keep-alive
 * @param arr 处理后的一维路由菜单数组
 * @returns 返回将一维数组重新处理成 `定义动态路由（dynamicRoutes）` 的格式
 */
export function formatTwoStageRoutes(arr: any) {
	if (arr.length <= 0) return false;
	const newArr: any = [];
	const cacheList: Array<string> = [];
	arr.forEach((v: any) => {
		if (v.path === '/') {
			newArr.push({
				component: v.component,
				name: v.name,
				path: v.path,
				redirect: v.redirect,
				meta: v.meta,
				children: []
			});
		} else {
			if (v.path.indexOf('/:') > -1) {
				v.meta['isDynamic'] = true;
				v.meta['isDynamicPath'] = v.path;
			}
			newArr[0].children.push({...v});
			if (newArr[0].meta.isKeepAlive && v.meta.isKeepAlive) {
				cacheList.push(v.name);
				const stores = useKeepALiveNames();
				stores.setCacheKeepAlive(cacheList);
			}
		}
	});
	return newArr;
}

let pendingLoading = false;


router.beforeEach(async (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {


const storesThemeConfig = useThemeConfig();
const {themeConfig} = storeToRefs(storesThemeConfig);
const {isRequestRoutes} = themeConfig.value;

	NProgress.configure({showSpinner: false});
	if (to.meta.title) NProgress.start();
	const token = Session.get('token');
	const publicPaths = ['/login', '/register', '/forget-password'];
	if (publicPaths.includes(to.path) && !token) {
		NextLoading.done();
		next();
		NProgress.done();
	} else {
		if (!token) {
			NextLoading.done();
			next(`/login?redirect=${to.path}&params=${JSON.stringify(to.query ? to.query : to.params)}`);
			Session.clear();
			NProgress.done();
		} else if (token && publicPaths.includes(to.path)) {
			NextLoading.done();
			next('/home');
			NProgress.done();
		} else {
			const storesRoutesList = useRoutesList();
			const {routesList, isGet} = storeToRefs(storesRoutesList);
			if (routesList.value.length === 0 && !isGet.value) {
				pendingLoading = true;
				if (!window.nextLoading) NextLoading.start();
				try {
					if (isRequestRoutes) {
						await initBackEndControlRoutes();
					} else {
						await initFrontEndControlRoutes();
					}
					next({path: to.path, query: to.query});
				} catch (error) {
					pendingLoading = false;
					NextLoading.done();
					throw error;
				}
			} else {
				next();
			}
		}
	}
});


router.afterEach((to) => {
	NProgress.done();
	const publicPaths = ['/login', '/register', '/forget-password'];
	if (pendingLoading || (window.nextLoading && !publicPaths.includes(to.path))) {
		nextTick(() => {
			NextLoading.done();
			pendingLoading = false;
		});
	}
});


export default router;
