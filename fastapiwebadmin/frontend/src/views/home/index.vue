<template>
  <div class="home-container">
    <el-card class="home-welcome-card" shadow="never">
      <div class="home-welcome-content">
        <div class="home-welcome-left">
          <h2 class="home-welcome-title">你好，{{ userInfo.nickname || userInfo.username || '管理员' }}</h2>
          <p class="home-welcome-desc">{{ greetingText }}，欢迎回来！</p>
        </div>
        <div class="home-welcome-right">
          <span>{{ currentDate }}</span>
          <time>{{ currentTime }}</time>
        </div>
      </div>
    </el-card>

    <section class="home-stats-section" aria-label="商城数据统计" :aria-busy="loading">
      <el-row :gutter="16" class="home-stats-row">
        <el-col v-for="card in metricCards" :key="card.key" :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
          <el-card shadow="hover" class="home-stat-card">
            <div class="home-stat-content">
              <div class="home-stat-icon" :class="'home-stat-icon--' + card.key" aria-hidden="true">
                <el-icon :size="32"><component :is="card.icon" /></el-icon>
              </div>
              <div class="home-stat-info">
                <div class="home-stat-value">{{ stats ? stats[card.key].toLocaleString('zh-CN') : '—' }}</div>
                <div class="home-stat-label">{{ card.label }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <div v-if="failed" class="home-stats-error" role="status">
        <span>统计数据加载失败</span>
        <el-button type="primary" link :loading="loading" @click="loadStats">重新加载</el-button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onActivated, onDeactivated, onMounted, onUnmounted, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { Avatar, Clock, Menu, User } from '@element-plus/icons-vue';
import { useStatisticsApi } from '/@/api/useSystemApi/statistic';
import { useUserStore } from '/@/stores/user';
import { Session } from '/@/utils/storage';

defineOptions({ name: 'home' });

type HomeStats = { users: number; goods: number; products: number; orders: number };
const { userInfos: userInfo } = storeToRefs(useUserStore());
const metricCards = [
  { key: 'users', label: '用户数量', icon: User },
  { key: 'goods', label: '商品数量', icon: Menu },
  { key: 'products', label: '货品数量', icon: Avatar },
  { key: 'orders', label: '订单数量', icon: Clock },
] as const;
const stats = ref<HomeStats | null>(null);
const loading = ref(false);
const failed = ref(false);
const now = ref(new Date());
let timer: ReturnType<typeof setInterval> | undefined;
let active = true;
let requestVersion = 0;

const currentDate = computed(() => now.value.toLocaleDateString('zh-CN', {
  year: 'numeric', month: 'long', day: 'numeric', weekday: 'long',
}));
const currentTime = computed(() => now.value.toLocaleTimeString('zh-CN', { hour12: false }));
const greetingText = computed(() => {
  const hour = now.value.getHours();
  if (hour < 6) return '凌晨好';
  if (hour < 9) return '早上好';
  if (hour < 12) return '上午好';
  if (hour < 14) return '中午好';
  if (hour < 17) return '下午好';
  if (hour < 19) return '傍晚好';
  if (hour < 22) return '晚上好';
  return '夜深了';
});

const loadStats = async () => {
  if (!active || loading.value) return;
  const version = ++requestVersion;
  const token = Session.get('token');
  loading.value = true;
  failed.value = false;
  // 刷新期间不把上次数据当作当前结果，也不以 0 冒充加载失败。
  stats.value = null;
  try {
    const res = await useStatisticsApi().countStatistic();
    if (!active || version !== requestVersion || token !== Session.get('token')) return;
    const data = res.data;
    if (!data || metricCards.some(({ key }) => !Number.isSafeInteger(data[key]) || data[key] < 0)) {
      throw new Error('统计数据格式不正确');
    }
    stats.value = data;
  } catch (error) {
    if (active && version === requestVersion && token === Session.get('token')) failed.value = true;
  } finally {
    if (version === requestVersion) loading.value = false;
  }
};
const start = () => {
  active = true;
  now.value = new Date();
  if (!timer) timer = setInterval(() => { now.value = new Date(); }, 1000);
  loadStats();
};
const stop = () => {
  active = false;
  requestVersion += 1;
  loading.value = false;
  if (timer) clearInterval(timer);
  timer = undefined;
};
onMounted(start);
onActivated(start);
onDeactivated(stop);
onUnmounted(stop);
</script>

<style scoped lang="scss">
.home-container {
  min-height: calc(100vh - 50px);
  padding: 16px;
  background: #f0f2f5;
}
.home-welcome-card {
  margin-bottom: 16px;
  border-radius: 8px;
  :deep(.el-card__body) { padding: 20px; }
}
.home-welcome-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}
.home-welcome-left { min-width: 0; }
.home-welcome-title {
  margin: 0 0 8px;
  color: #303133;
  font-size: 24px;
  font-weight: 500;
  overflow-wrap: anywhere;
}
.home-welcome-desc { margin: 0; color: #909399; font-size: 14px; }
.home-welcome-right {
  display: flex;
  flex-shrink: 0;
  flex-direction: column;
  gap: 6px;
  color: #606266;
  text-align: right;
  font-size: 14px;
  time { color: #909399; font-variant-numeric: tabular-nums; }
}
.home-stats-section {
  margin-bottom: 16px;
}
.home-stat-card {
  margin-bottom: 16px;
  border-radius: 8px;
  transition: all 0.3s;
  &:hover { transform: translateY(-4px); }
  :deep(.el-card__body) { padding: 20px; }
}
.home-stat-content { display: flex; align-items: center; }
.home-stat-icon {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  margin-right: 16px;
  border-radius: 8px;
  color: #fff;
  &--users { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
  &--goods { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
  &--products { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
  &--orders { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
}
.home-stat-info { flex: 1; min-width: 0; text-align: left; }
.home-stat-label { color: #909399; font-size: 14px; }
.home-stat-value { margin-bottom: 8px; color: #303133; font-size: 28px; font-weight: 600; line-height: 1; overflow-wrap: anywhere; }
.home-stats-error { display: flex; align-items: center; justify-content: center; gap: 12px; margin-top: 24px; color: #909399; font-size: 13px; }
@media (max-width: 560px) {
  .home-welcome-card :deep(.el-card__body) { padding: 18px 16px; }
  .home-welcome-content { align-items: flex-start; flex-direction: column; gap: 16px; }
  .home-welcome-title { font-size: 22px; }
  .home-welcome-right { text-align: left; font-size: 12px; }
}
</style>

