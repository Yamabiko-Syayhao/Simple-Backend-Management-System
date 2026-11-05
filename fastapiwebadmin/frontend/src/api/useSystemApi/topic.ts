import request from '/@/utils/request';

/**
 * 专题管理接口
 * @method getList 标题/子标题筛选、三种服务端排序及分页
 * @method getDetail 专题文章与关联商品详情
 * @method saveOrUpdate 创建或编辑专题及商品关联
 * @method deleted 单条物理删除
 * @method batchDeleted 批量物理删除
 * @method exportExcel 按筛选和排序导出 xlsx
 */
export function useTopicApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/topic/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/topic/detail',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate: (data?: object) => {
      return request({
        url: '/topic/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/topic/deleted',
        method: 'POST',
        data,
      });
    },
    batchDeleted: (data?: object) => {
      return request({
        url: '/topic/batchDeleted',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/topic/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
