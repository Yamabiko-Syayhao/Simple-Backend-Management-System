import request from '/@/utils/request';

/**
 * 会员足迹接口
 * @method getList 足迹列表（分页 + 用户ID/商品ID筛选）
 * @method getDetail 足迹详情
 * @method saveOrUpdate 新增或编辑足迹
 * @method deleted 删除足迹
 * @method exportExcel 导出足迹 xlsx
 */
export function useFootprintApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/footprint/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/footprint/detail',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate: (data?: object) => {
      return request({
        url: '/footprint/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/footprint/deleted',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/footprint/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
