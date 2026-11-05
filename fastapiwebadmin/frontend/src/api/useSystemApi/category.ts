import request from '/@/utils/request';

/**
 * 商品类目接口
 * @method getList 全量类目（前端组装成树）
 * @method getDetail 类目详情
 * @method saveOrUpdate 新增或编辑
 * @method deleted 删除（物理删除）
 */
export function useCategoryApi() {
  return {
    getList: () => {
      return request({
        url: '/category/list',
        method: 'POST',
        data: {},
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/category/detail',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate: (data?: object) => {
      return request({
        url: '/category/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/category/deleted',
        method: 'POST',
        data,
      });
    },
  };
}
