import request from '/@/utils/request';

/**
 * 优惠券管理接口
 * @method getList 分页列表、名称/类型/状态筛选及服务端排序
 * @method getDetail 详情与编辑回显（含分类/商品使用范围）
 * @method getUserList 优惠券领取记录（用户ID / 使用状态筛选）
 * @method saveOrUpdate 创建或编辑优惠券
 * @method deleted 物理删除优惠券及使用范围
 * @method exportExcel 按筛选条件导出 xlsx
 */
export function useCouponApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/coupon/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/coupon/detail',
        method: 'POST',
        data,
      });
    },
    getUserList: (data?: object) => {
      return request({
        url: '/coupon/userList',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate: (data?: object) => {
      return request({
        url: '/coupon/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/coupon/deleted',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/coupon/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
