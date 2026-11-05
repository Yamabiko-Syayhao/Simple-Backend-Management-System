<template>
  <div class="layout-breadcrumb-setting">
    <el-drawer title="偏好设置" v-model="getThemeConfig.isDrawer" direction="rtl" destroy-on-close size="390px"
               @close="onDrawerClose">
      <template #header>
        <span>偏好设置</span>
      </template>

      <el-scrollbar>
        <div class="layout-breadcrumb-setting-bar p15">
          <el-segmented v-model="segmentedValue" :options="segmentedOptions" block size="default">
            <template #default="{item}">
              <!--            <el-button>{{ item.label }}</el-button>-->
              <span>{{ item.label }}</span>
            </template>
          </el-segmented>
          <!-- 全局主题 -->
          <div class="m4">
            <Appearance v-if="segmentedValue == 'appearance'"></Appearance>
            <Layout v-if="segmentedValue == 'layout'"></Layout>
            <General v-if="segmentedValue == 'general'"></General>
          </div>
        </div>
      </el-scrollbar>

      <template #footer>
        <div class="copy-config">
          <el-button size="default" class="copy-config-btn" type="primary" ref="copyConfigBtnRef"
                     @click="onCopyConfigClick">
            <el-icon class="mr5">
              <ele-CopyDocument/>
            </el-icon>
            一键复制配置
          </el-button>
          <el-button size="default" class="copy-config-btn-reset" type="info" @click="onResetConfigClick">
            <el-icon class="mr5">
              <ele-RefreshRight/>
            </el-icon>
            一键恢复默认
          </el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import {onMounted, onUnmounted, reactive, ref} from 'vue';
import {storeToRefs} from 'pinia';
import {Local} from '/@/utils/storage';
import {useThemeConfig} from '/@/stores/themeConfig';
import other from '/@/utils/other';
import mittBus from '/@/utils/mitt';
import Appearance from "./component/appearance.vue";
import Layout from "./component/layout.vue";
import General from "./component/general.vue";
import {
  initLayoutChangeFun,
  onCopyConfigClick,
  onDrawerClose,
  onResetConfigClick,
} from "/@/layout/navBars/topBar/settings/index";

defineOptions({name: "layoutBreadcrumbSetting"})

const { themeConfig: getThemeConfig } = storeToRefs(useThemeConfig());


const state = reactive({
  isMobile: false,
});

const segmentedValue = ref("appearance")
const segmentedOptions = [
  {label: '外观', value: 'appearance'},
  {label: '布局', value: 'layout'},
  {label: '通用', value: 'general'},
]

onMounted(() => {
  mittBus.on('layoutMobileResize', (res) => {
    getThemeConfig.value.layout = res.layout;
    getThemeConfig.value.isDrawer = false;
    initLayoutChangeFun();
    state.isMobile = other.isMobile();
  });
});
onUnmounted(() => {
  mittBus.off('layoutMobileResize', () => {
  });
});


const openDrawer = () => {
  getThemeConfig.value.isDrawer = true;
};

defineExpose({
  openDrawer,
});
</script>

<style lang="scss" scoped>
@use "./index" as *;

</style>
