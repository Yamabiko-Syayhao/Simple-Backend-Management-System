import request from '/@/utils/request';

/**
 * 通用问题（FAQ）接口
 * @method getList 列表（分页 + 问题关键字 + 排序）
 * @method getDetail 详情
 * @method saveOrUpdate 新增或编辑
 * @method deleted 删除（物理删除）
 * @method exportExcel 导出 xlsx
 */
export function useFaqApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/faq/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/faq/detail',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate: (data?: object) => {
      return request({
        url: '/faq/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/faq/deleted',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/faq/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
