import request from '/@/utils/request';

/**
 * 团购规则接口
 * @method getList 列表（keyword 支持商品编号/名称/商品ID）
 * @method getDetail 详情
 * @method saveOrUpdate 新增或编辑
 * @method deleted 删除（物理删除）
 * @method exportExcel 导出 xlsx
 */
export function useGroupRuleApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/groupRule/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/groupRule/detail',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate: (data?: object) => {
      return request({
        url: '/groupRule/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/groupRule/deleted',
        method: 'POST',
        data,
      });
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/groupRule/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
