import request from '/@/utils/request';

/**
 * 搜索关键词接口
 * @method getList 列表（分页 + 关键词/跳转链接筛选 + 排序）
 * @method getDetail 详情
 * @method saveOrUpdate 新增或编辑
 * @method deleted 删除（物理删除）
 * @method exportExcel 导出 xlsx
 */
export function useKeywordApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/keyword/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/keyword/detail',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate: (data?: object) => {
      return request({
        url: '/keyword/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/keyword/deleted',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/keyword/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
