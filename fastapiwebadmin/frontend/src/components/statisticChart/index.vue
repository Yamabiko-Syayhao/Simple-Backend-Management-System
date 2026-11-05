<template>
  <div ref="chartRef" class="statistic-chart"></div>
</template>

<script setup lang="ts">
defineOptions({ name: 'statisticChart' })
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  option: {
    type: Object,
    default: () => ({}),
  },
  height: {
    type: String,
    default: '520px',
  },
});

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

const render = () => {
  if (!chartRef.value) return;
  if (!chart) chart = echarts.init(chartRef.value);
  chart.setOption(props.option || {}, true);
};

const resize = () => chart?.resize();

onMounted(() => {
  render();
  window.addEventListener('resize', resize);
});

watch(
  () => props.option,
  () => nextTick(render),
  { deep: true }
);

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize);
  chart?.dispose();
  chart = null;
});
</script>

<style scoped lang="scss">
.statistic-chart {
  width: 100%;
  height: v-bind(height);
  min-height: 320px;
}
</style>
