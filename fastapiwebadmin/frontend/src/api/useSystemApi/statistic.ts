import request from '/@/utils/request';

/**
 * 统计接口
 */
export function useStatisticsApi() {
  return {
    countStatistic: () => {
      return request({
        url: '/statistic/countStatistic',
        method: 'POST',
        data: {}
      });
    },
    /** 用户统计：每日新增会员数 */
    userChart: (data?: object) => {
      return request({
        url: '/statistic/userChart',
        method: 'POST',
        data: data || {}
      });
    },
    /** 订单统计：每日订单量 / 下单用户 / 订单总额 / 客单价 */
    orderChart: (data?: object) => {
      return request({
        url: '/statistic/orderChart',
        method: 'POST',
        data: data || {}
      });
    },
    /** 商品统计：每日订单量 / 下单货品数量 / 下单货品总额 */
    goodsChart: (data?: object) => {
      return request({
        url: '/statistic/goodsChart',
        method: 'POST',
        data: data || {}
      });
    },
  };
}
