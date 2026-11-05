import request from '/@/utils/request';

/**
 * 行政区域接口（基础字典数据，无需登录即可访问）
 * @method getTree 完整的省 / 市 / 区三级树
 * @method getChildren 查询某个区域的直接下级（客户端做省市级联时用）
 */
export function useRegionApi() {
  return {
    getTree: () => {
      return request({
        url: '/region/tree',
        method: 'POST',
        data: {},
      });
    },
    getChildren: (data?: object) => {
      return request({
        url: '/region/children',
        method: 'POST',
        data,
      });
    },
  };
}
