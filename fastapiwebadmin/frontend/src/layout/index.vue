<template>
  <div class="h100">
    <component :is="layouts[themeConfig.layout]"/>
    <AiAssistant v-if="userInfos.id && !themeConfig.isLockScreen" :key="userInfos.id" />
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'layout' })
import {defineAsyncComponent, onBeforeMount, onUnmounted} from 'vue';
import {storeToRefs} from "/@/stores";
import {useThemeConfig} from '/@/stores/themeConfig';
import {useUserStore} from '/@/stores/user';
import {Local} from '/@/utils/storage';
import mittBus from '/@/utils/mitt';
import {initLayoutChangeFun} from '/@/layout/navBars/topBar/settings/index';
import AiAssistant from '/@/views/system/aiAssistant/index.vue';


const layouts = {
  defaults: defineAsyncComponent(() => import('/@/layout/main/defaults.vue')),
  classic: defineAsyncComponent(() => import('/@/layout/main/classic.vue')),
  transverse: defineAsyncComponent(() => import('/@/layout/main/transverse.vue')),
  columns: defineAsyncComponent(() => import('/@/layout/main/columns.vue')),
};


const storesThemeConfig = useThemeConfig();
const {themeConfig} = storeToRefs(storesThemeConfig);
const {userInfos} = storeToRefs(useUserStore());


const onLayoutResize = () => {
  if (!Local.get('oldLayout')) Local.set('oldLayout', themeConfig.value.layout);
  const clientWidth = document.body.clientWidth;
  if (clientWidth < 1000) {
    themeConfig.value.isCollapse = false;
    themeConfig.value.layout = 'defaults';
    initLayoutChangeFun();
    mittBus.emit('layoutMobileResize', {
      layout: 'defaults',
      clientWidth,
    });
  } else {
    const layout = Local.get('oldLayout') ? Local.get('oldLayout') : themeConfig.value.layout;
    themeConfig.value.layout = layout;
    initLayoutChangeFun();
    mittBus.emit('layoutMobileResize', {
      layout,
      clientWidth,
    });
  }
};

onBeforeMount(() => {
  if (!Local.get('frequency')) {
    initLayoutChangeFun();
    Local.set('frequency', 1);
  }
  onLayoutResize();
  window.addEventListener('resize', onLayoutResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', onLayoutResize);
});
</script>
