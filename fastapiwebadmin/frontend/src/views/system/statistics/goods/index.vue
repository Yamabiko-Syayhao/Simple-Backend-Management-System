<template>
  <div class="stat-page">
    <div class="stat-card">
      <div class="stat-head">
        <span class="stat-title">商品统计</span>
        <el-radio-group v-model="days" size="small" @change="load">
          <el-radio-button :label="7">近 7 天</el-radio-button>
          <el-radio-button :label="30">近 30 天</el-radio-button>
          <el-radio-button :label="90">近 90 天</el-radio-button>
          <el-radio-button :label="0">全部</el-radio-button>
        </el-radio-group>
      </div>

      <div v-loading="loading" class="stat-body">
        <statistic-chart v-if="dates.length" :option="option"></statistic-chart>
        <el-empty v-else-if="!loading" description="暂无商品统计数据"></el-empty>
      </div>
    </div>

    <div class="stat-tips">
      <span>订单量＝当日下单笔数（去重）；下单货品数量＝当日订单明细数量合计；下单货品总额＝当日明细「单价 × 数量」合计。</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'statisticsGoods' })
import { computed, onMounted, ref } from 'vue';
import StatisticChart from '/@/components/statisticChart/index.vue';
import { useStatisticsApi } from '/@/api/useSystemApi/statistic';

const days = ref(0);
const loading = ref(false);
const dates = ref<string[]>([]);
const series = ref<Record<string, number[]>>({
  order_count: [],
  goods_quantity: [],
  goods_amount: [],
});

const load = async () => {
  loading.value = true;
  try {
    const res: any = await useStatisticsApi().goodsChart({ days: days.value });
    const data = res.data || {};
    dates.value = data.dates || [];
    series.value = data.series || {};
  } finally {
    loading.value = false;
  }
};

const line = (name: string, data: number[], color: string) => ({
  name,
  type: 'line',
  smooth: true,
  symbolSize: 6,
  showSymbol: true,
  data,
  lineStyle: { width: 2, color },
  itemStyle: { color },
});

const option = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { top: 0, data: ['订单量', '下单货品数量', '下单货品总额'] },
  grid: { left: 60, right: 40, top: 56, bottom: 48 },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: dates.value,
    axisTick: { show: false },
    axisLine: { lineStyle: { color: '#e5e5e5' } },
    axisLabel: { color: '#8c8c8c' },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#f0f0f0' } },
    axisLabel: { color: '#8c8c8c' },
  },
  series: [
    line('订单量', series.value.order_count || [], '#13c2a3'),
    line('下单货品数量', series.value.goods_quantity || [], '#4facfe'),
    line('下单货品总额', series.value.goods_amount || [], '#f56c6c'),
  ],
}));

onMounted(load);
</script>

<style scoped lang="scss">
.stat-page {
  padding: 16px;
}

.stat-card {
  background: #ffffff;
  border-radius: 4px;
  padding: 16px 18px 8px;
}

.stat-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 8px;
}

.stat-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.stat-body {
  min-height: 320px;
}

.stat-tips {
  margin-top: 10px;
  font-size: 12px;
  line-height: 20px;
  color: #909399;
}

@media screen and (max-width: 900px) {
  .stat-page {
    padding: 10px;
  }
}
</style>
