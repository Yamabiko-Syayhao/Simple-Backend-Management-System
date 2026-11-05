<template>
  <div class="stat-page">
    <div class="stat-card">
      <div class="stat-head">
        <span class="stat-title">用户统计</span>
        <el-radio-group v-model="days" size="small" @change="load">
          <el-radio-button :label="7">近 7 天</el-radio-button>
          <el-radio-button :label="30">近 30 天</el-radio-button>
          <el-radio-button :label="90">近 90 天</el-radio-button>
          <el-radio-button :label="0">全部</el-radio-button>
        </el-radio-group>
      </div>

      <div v-loading="loading" class="stat-body">
        <statistic-chart v-if="dates.length" :option="option"></statistic-chart>
        <el-empty v-else-if="!loading" description="暂无用户统计数据"></el-empty>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'statisticsUser' })
import { computed, onMounted, ref } from 'vue';
import StatisticChart from '/@/components/statisticChart/index.vue';
import { useStatisticsApi } from '/@/api/useSystemApi/statistic';

const days = ref(0);
const loading = ref(false);
const dates = ref<string[]>([]);
const userCount = ref<number[]>([]);

const load = async () => {
  loading.value = true;
  try {
    const res: any = await useStatisticsApi().userChart({ days: days.value });
    const data = res.data || {};
    dates.value = data.dates || [];
    userCount.value = (data.series && data.series.user_count) || [];
  } finally {
    loading.value = false;
  }
};

const option = computed(() => ({
  color: ['#13c2a3'],
  tooltip: { trigger: 'axis' },
  legend: { top: 0, data: ['用户增长数'] },
  grid: { left: 60, right: 30, top: 56, bottom: 48 },
  xAxis: {
    type: 'category',
    boundaryGap: true,
    data: dates.value,
    axisTick: { show: false },
    axisLine: { lineStyle: { color: '#e5e5e5' } },
    axisLabel: { color: '#8c8c8c' },
  },
  yAxis: {
    type: 'value',
    minInterval: 1,
    splitLine: { lineStyle: { color: '#f0f0f0' } },
    axisLabel: { color: '#8c8c8c' },
  },
  series: [
    {
      name: '用户增长数',
      type: 'bar',
      data: userCount.value,
      label: { show: true, position: 'top', color: '#13c2a3' },
      itemStyle: { borderRadius: [2, 2, 0, 0] },
    },
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

@media screen and (max-width: 900px) {
  .stat-page {
    padding: 10px;
  }
}
</style>
