import request from '/@/utils/request';

/**
 * 品牌制造商接口
 * @method getList 品牌商列表（分页 + ID/名称筛选）
 * @method getDetail 品牌商详情
 * @method saveOrUpdate 新增或编辑
 * @method deleted 删除
 * @method exportExcel 导出 xlsx
 */
export function useBrandApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/brand/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/brand/detail',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate: (data?: object) => {
      return request({
        url: '/brand/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/brand/deleted',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/brand/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
