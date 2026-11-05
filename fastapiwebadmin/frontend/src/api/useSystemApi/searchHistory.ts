import request from '/@/utils/request';

/**
 * 会员搜索历史接口
 * @method getList 列表（分页 + 用户ID/关键字筛选）
 * @method getDetail 详情
 * @method saveOrUpdate 新增或编辑
 * @method deleted 删除
 * @method exportExcel 导出 xlsx
 */
export function useSearchHistoryApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/searchHistory/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/searchHistory/detail',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate: (data?: object) => {
      return request({
        url: '/searchHistory/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/searchHistory/deleted',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/searchHistory/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
