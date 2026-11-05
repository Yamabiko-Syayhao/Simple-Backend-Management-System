import request from '/@/utils/request';
/** 商品管理接口，所有修改由后端持久化。 */
export function useGoodsApi() {
  const post = (path: string, data: object = {}) =>
    request({ url: `/goods/${path}`, method: 'POST', data });
  return {
    getList: (data: object) => post('list', data),
    getDetail: (data: object) => post('detail', data),
    saveOrUpdate: (data: object) => post('saveOrUpdate', data),
    deleted: (data: object) => post('deleted', data),
    batchDeleted: (data: object) => post('batchDeleted', data),
    saveChild: (kind: string, data: object) => post(`${kind}/save`, data),
    deleteAttribute: (data: object) => post('attribute/deleted', data),
    exportExcel: (data: object) =>
      request({
        url: '/goods/export',
        method: 'POST',
        data,
        responseType: 'blob',
      }),
  };
}
