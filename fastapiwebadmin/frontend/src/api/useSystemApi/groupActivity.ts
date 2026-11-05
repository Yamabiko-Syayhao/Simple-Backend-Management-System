import request from '/@/utils/request';

/**
 * 团购活动接口（后台只读）
 * @method getList 列表（按团购规则ID筛选，返回每条活动的参与成员）
 * @method exportExcel 导出 xlsx
 */
export function useGroupActivityApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/groupActivity/list',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/groupActivity/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
