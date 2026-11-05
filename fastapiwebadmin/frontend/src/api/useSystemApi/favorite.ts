import request from '/@/utils/request';

/**
 * 会员收藏接口
 * @method getList 收藏列表（分页 + 用户ID/商品ID筛选）
 * @method getDetail 收藏详情
 * @method saveOrUpdate 新增或编辑收藏
 * @method deleted 删除收藏
 * @method exportExcel 导出收藏 xlsx
 */
export function useFavoriteApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/favorite/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/favorite/detail',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate: (data?: object) => {
      return request({
        url: '/favorite/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/favorite/deleted',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/favorite/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
