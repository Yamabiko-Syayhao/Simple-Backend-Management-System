<template>
  <el-config-provider :size="getGlobalComponentSize" :locale="zhCn">
    <router-view v-show="setLockScreen"/>
    <LockScreen v-if="themeConfig.isLockScreen"/>
    <Settings v-if="settingsMounted" ref="settingsRef" v-show="setLockScreen"/>
    <CloseFull v-if="!themeConfig.isLockScreen"/>
    <Upgrade v-if="getVersion"/>
  </el-config-provider>
</template>

<script setup lang="ts">
import { defineAsyncComponent, computed, ref, onBeforeMount, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useRoute } from 'vue-router';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { storeToRefs } from "/@/stores";
import { useTagsViewRoutes } from '/@/stores/tagsViewRoutes';
import { useThemeConfig } from '/@/stores/themeConfig';
import other from '/@/utils/other';
import { Local, Session } from '/@/utils/storage';
import { applyPrimaryThemeColor } from '/@/utils/theme';
import mittBus from '/@/utils/mitt';
import setIntroduction from '/@/utils/setIconfont';
import { syncDocumentThemeMode } from '/@/utils/themeTopBar';
import { initThemeStylesOnBoot } from '/@/utils/initThemeStyles';
import LockScreen from "/@/layout/lockScreen/index.vue"

defineOptions({ name: 'App' })

// 引入组件
// const LockScreen = defineAsyncComponent(() => import('/@/layout/lockScreen/index.vue'));
const Settings = defineAsyncComponent(() => import('/@/layout/navBars/topBar/settings/index.vue'));
const CloseFull = defineAsyncComponent(() => import('/@/layout/navBars/topBar/closeFull.vue'));
const Upgrade = defineAsyncComponent(() => import('/@/layout/upgrade/index.vue'));

// 定义变量内容
const settingsRef = ref();
const settingsMounted = ref(false);
const route = useRoute();
const stores = useTagsViewRoutes();
const storesThemeConfig = useThemeConfig();
const { themeConfig } = storeToRefs(storesThemeConfig);

// 设置锁屏时组件显示隐藏
const setLockScreen = computed(() => {
  // 防止锁屏后，刷新出现不相关界面
  return themeConfig.value.isLockScreen ? themeConfig.value.lockScreenTime > 1 : themeConfig.value.lockScreenTime >= 0;
});

// 获取版本号
const getVersion = computed(() => {
  let isVersion = false;
  if (route.path !== '/login') {
    // @ts-ignore
    if ((Local.get('version') && Local.get('version') !== __VERSION__) || !Local.get('version')) isVersion = true;
  }
  return isVersion;
});
// 获取全局组件大小
const getGlobalComponentSize = computed(() => {
  return other.globalComponentSize();
});
// 设置初始化，防止刷新时恢复默认
onBeforeMount(() => {
  // 设置批量第三方 icon 图标
  setIntroduction.cssCdn();
  // 设置批量第三方 js
  setIntroduction.jsCdn();
});
// 页面加载时
onMounted(() => {
  nextTick(() => {
    // 监听布局配'置弹窗点击打开
    mittBus.on('openSettingsDrawer', () => {
      if (!settingsMounted.value) settingsMounted.value = true;
      nextTick(() => settingsRef.value?.openDrawer());
    });
    // 获取缓存中的布局配置
    if (Local.get('themeConfig')) {
      const cached = Local.get('themeConfig') as Record<string, unknown>;
      let patched = false;
      if (cached.globalComponentSize === 'small') {
        cached.globalComponentSize = 'default';
        patched = true;
      }
      if (cached.primary === '#409eff') {
        cached.primary = '#5D87FF';
        patched = true;
      }
      if (patched) {
        Local.set('themeConfig', cached);
      }
      storesThemeConfig.setThemeConfig({ themeConfig: cached });
      if (Local.get('themeConfigStyle')) {
        document.documentElement.style.cssText = Local.get('themeConfigStyle');
      }
      const primary = applyPrimaryThemeColor((cached.primary as string) || '#5D87FF');
      themeConfig.value.primary = primary;
      Local.set('themeConfig', { ...cached, primary });
      syncDocumentThemeMode(
        themeConfig.value.isIsDark,
        themeConfig.value.topBar,
        themeConfig.value.topBarColor,
      );
    } else {
      themeConfig.value.primary = applyPrimaryThemeColor(themeConfig.value.primary || '#5D87FF');
      if (themeConfig.value.isIsDark) {
        syncDocumentThemeMode(true, themeConfig.value.topBar, themeConfig.value.topBarColor);
      }
    }
    initThemeStylesOnBoot(themeConfig.value);
    // 获取缓存中的全屏配置
    if (Session.get('isTagsViewCurrenFull')) {
      stores.setCurrenFullscreen(Session.get('isTagsViewCurrenFull'));
    }
  });
});
// 页面销毁时，关闭监听布局配置/i18n监听
onUnmounted(() => {
  mittBus.off('openSettingsDrawer', () => {
  });
});
// 监听路由的变化，设置网站标题
watch(
    () => route.path,
    () => {
      other.useTitle();
    },
    {
      deep: true,
    }
);
</script>
