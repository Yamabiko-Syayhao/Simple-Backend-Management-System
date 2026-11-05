import request from '/@/utils/request';

/**
 * 售后管理接口
 * @method getList 售后列表（支持售后编号 / 订单ID / 状态）
 * @method getDetail 售后详情
 * @method audit 批量通过 / 批量拒绝
 * @method exportExcel 导出 xlsx
 */
export function useAfterSaleApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/afterSale/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/afterSale/detail',
        method: 'POST',
        data,
      });
    },
    audit: (data?: object) => {
      return request({
        url: '/afterSale/audit',
        method: 'POST',
        data,
        silent: true,
      } as any);
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/afterSale/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
