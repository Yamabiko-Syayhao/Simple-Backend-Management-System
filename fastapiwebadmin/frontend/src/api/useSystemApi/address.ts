import request from '/@/utils/request';

/**
 * 收货地址接口
 * @method getList 收货地址列表（分页 + 用户ID/收货人筛选）
 * @method getDetail 收货地址详情
 * @method saveOrUpdate 新增或编辑收货地址
 * @method deleted 删除收货地址
 * @method exportExcel 导出收货地址 xlsx
 */
export function useAddressApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/address/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/address/detail',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate: (data?: object) => {
      return request({
        url: '/address/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/address/deleted',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/address/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
