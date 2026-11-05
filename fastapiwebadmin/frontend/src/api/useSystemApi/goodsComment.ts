import request from '/@/utils/request';

/**
 * 商品评论接口
 * @method getList 列表（用户ID / 商品ID 筛选）
 * @method reply 回复评论（一条只能回复一次）
 * @method deleted 删除评论（物理删除）
 * @method exportExcel 导出 xlsx
 */
export function useGoodsCommentApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/goodsComment/list',
        method: 'POST',
        data,
      });
    },
    reply: (data?: object) => {
      return request({
        url: '/goodsComment/reply',
        method: 'POST',
        data,
        silent: true,
      } as any);
    },
    deleted: (data?: object) => {
      return request({
        url: '/goodsComment/deleted',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/goodsComment/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
