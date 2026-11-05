import request from '/@/utils/request';

/**
 * 广告管理接口
 * @method getList 广告列表（标题 / 内容筛选、服务端排序）
 * @method getDetail 广告详情
 * @method saveOrUpdate 新增或编辑广告
 * @method deleted 删除广告（物理删除）
 * @method exportExcel 导出 xlsx
 */
export function useAdApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/ad/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/ad/detail',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate: (data?: object) => {
      return request({
        url: '/ad/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/ad/deleted',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/ad/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
