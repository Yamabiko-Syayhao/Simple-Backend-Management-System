import request from '/@/utils/request';

/**
 * 会员意见反馈接口
 * @method getList 列表（分页 + 用户名/反馈ID筛选）
 * @method getDetail 详情
 * @method saveOrUpdate 新增或编辑
 * @method deleted 删除
 * @method exportExcel 导出 xlsx
 */
export function useFeedbackApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/feedback/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/feedback/detail',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate: (data?: object) => {
      return request({
        url: '/feedback/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/feedback/deleted',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/feedback/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
