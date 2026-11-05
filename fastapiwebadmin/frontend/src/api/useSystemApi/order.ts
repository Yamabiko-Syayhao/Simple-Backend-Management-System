import request from '/@/utils/request';

/**
 * 订单管理接口
 * @method getList 订单列表（支持用户昵称/收货人/订单编号/时间范围/状态）
 * @method getDetail 订单详情（含商品明细）
 * @method deleted 删除订单（物理删除）
 * @method collect 线下收款
 * @method deliver 发货
 * @method refund 退款
 * @method exportExcel 导出 xlsx
 *
 * 说明：collect / deliver / refund 三个动作当前只是占位，后端会返回业务错误，
 *      所以传 silent: true 关掉全局 toast，由页面自己弹「失败」通知。
 */
export function useOrderApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/order/list',
        method: 'POST',
        data,
      });
    },
    getDetail: (data?: object) => {
      return request({
        url: '/order/detail',
        method: 'POST',
        data,
      });
    },
    deleted: (data?: object) => {
      return request({
        url: '/order/deleted',
        method: 'POST',
        data,
      });
    },
    collect: (data?: object) => {
      return request({
        url: '/order/collect',
        method: 'POST',
        data,
        silent: true,
      } as any);
    },
    deliver: (data?: object) => {
      return request({
        url: '/order/deliver',
        method: 'POST',
        data,
        silent: true,
      } as any);
    },
    refund: (data?: object) => {
      return request({
        url: '/order/refund',
        method: 'POST',
        data,
        silent: true,
      } as any);
    },
    exportExcel: (data?: object) => {
      return request({
        url: '/order/export',
        method: 'POST',
        data,
        responseType: 'blob',
      });
    },
  };
}
