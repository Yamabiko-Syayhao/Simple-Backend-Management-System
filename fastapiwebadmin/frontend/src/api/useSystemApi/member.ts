import request from '/@/utils/request';

/**
 * 会员管理接口
 * @method getList 会员列表（分页 + 用户名/用户ID/手机号筛选）
 * @method getDetail 会员详情
 * @method saveOrUpdate 新增或编辑会员
 * @method deleted 删除会员
 * @method exportExcel 导出会员列表 xlsx
 */
export function useMemberApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/member/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/member/detail',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate: (data?: object) => {
      return request({
        url: '/member/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/member/deleted',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/member/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
