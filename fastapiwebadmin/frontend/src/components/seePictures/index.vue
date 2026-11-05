<template>
  <div>
    <el-dialog title="更换头像"
               destroy-on-close
               v-model="state.isShowDialog"
               width="769px"
               @closed="onClosed">
      <template #header>
        <div style="display:flex;">
          <span style="margin-right: 10px">更换头像</span>
          <slot>
            <el-upload :before-upload="beforeUpload" :showUploadList="false" accept="image/*">
              <el-button type="primary">选择图片</el-button>
            </el-upload>
          </slot>
        </div>
      </template>
      <div class="cropper-warp">
        <div class="cropper-warp-left">
          <img :src="state.cropperImg || EMPTY_IMG" class="cropper-warp-left-img" id="AvatarRef"/>
          <div v-if="!state.cropperImg" class="cropper-warp-left-tip">点击上方「选择图片」</div>
        </div>
        <div class="cropper-warp-right">
          <div class="cropper-warp-right-title">预览</div>
          <div class="cropper-warp-right-item">
            <div class="cropper-warp-right-value"></div>
            <div class="cropper-warp-right-label">100 x 100</div>
          </div>
          <div class="cropper-warp-right-item">
            <div class="cropper-warp-right-value cropper-warp-right-value--sm"></div>
            <div class="cropper-warp-right-label">50 x 50</div>
          </div>
        </div>
      </div>
      <template #footer>
				<span class="dialog-footer">
					<el-button @click="onCancel" size="default">取 消</el-button>
					<el-button type="primary" @click="onSubmit" size="default">更 换</el-button>
				</span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'cropper' })
import {reactive, nextTick} from 'vue';
import {ElMessage} from 'element-plus';
import Cropper from 'cropperjs';
import 'cropperjs/dist/cropper.css';

const emit = defineEmits(['updateAvatar'])

// 1x1 透明图：没有头像时占位，避免 <img src=""> 显示裂图
const EMPTY_IMG = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';

const state = reactive({
  isShowDialog: false,
  cropperImg: '',
  blobUrl: '',
  cropper: null as any,
});

// 打开弹窗
const openDialog = (imgs: string) => {
  state.cropperImg = imgs || '';
  state.isShowDialog = true;
  nextTick(() => {
    initCropper();
  });
};

// 关闭弹窗
const closeDialog = () => {
  state.isShowDialog = false;
};

const destroyCropper = () => {
  if (state.cropper) {
    state.cropper.destroy();
    state.cropper = null;
  }
  if (state.blobUrl) {
    URL.revokeObjectURL(state.blobUrl);
    state.blobUrl = '';
  }
};

const onClosed = () => {
  destroyCropper();
  state.cropperImg = '';
};

// 取消
const onCancel = () => {
  closeDialog();
};

// 更换：输出 200x200 的 JPEG，避免 base64 过大
const onSubmit = () => {
  if (!state.cropper || !state.cropperImg) {
    ElMessage.warning('请先选择图片');
    return;
  }
  const canvas = state.cropper.getCroppedCanvas({
    width: 200,
    height: 200,
    imageSmoothingEnabled: true,
    imageSmoothingQuality: 'high',
  });
  if (!canvas) {
    ElMessage.error('图片处理失败，请重新选择');
    return;
  }
  const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
  emit('updateAvatar', dataUrl);
  closeDialog();
};

// 初始化 cropperjs 图片裁剪
const initCropper = () => {
  const img = document.getElementById('AvatarRef') as HTMLImageElement | null;
  if (!img) return;
  destroyCropper();
  state.cropper = new Cropper(img, {
    viewMode: 1,
    dragMode: 'move',
    initialAspectRatio: 1,
    aspectRatio: 1,
    preview: '.cropper-warp-right-value',
    background: false,
    autoCropArea: 0.8,
    zoomOnWheel: true,
  });
};

// 选择本地图片
const beforeUpload = (file: File) => {
  if (!file || !file.type || !file.type.startsWith('image/')) {
    ElMessage.warning('请选择图片文件');
    return false;
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.warning('图片不能超过 5MB');
    return false;
  }

  const url = URL.createObjectURL(file);
  if (state.blobUrl) URL.revokeObjectURL(state.blobUrl);
  state.blobUrl = url;
  state.cropperImg = url;

  if (state.cropper) {
    state.cropper.replace(url);
  } else {
    nextTick(() => {
      const img = document.getElementById('AvatarRef') as HTMLImageElement | null;
      if (img) img.src = url;
      initCropper();
    });
  }
  return false;
};

// 暴露变量
defineExpose({
  openDialog,
  state,
});
</script>

<style scoped lang="scss">
.cropper-warp {
  display: flex;

  .cropper-warp-left {
    position: relative;
    display: inline-block;
    height: 350px;
    flex: 1;
    border: 1px solid var(--el-border-color);
    background: var(--el-color-white);
    overflow: hidden;
    background-repeat: no-repeat;
    cursor: move;
    border-radius: var(--el-border-radius-base);

    .cropper-warp-left-img {
      width: 100%;
      height: 100%;
      display: block;
      object-fit: contain;
    }

    .cropper-warp-left-tip {
      position: absolute;
      left: 0;
      right: 0;
      bottom: 12px;
      text-align: center;
      font-size: 12px;
      color: var(--el-text-color-secondary);
      pointer-events: none;
    }
  }

  .cropper-warp-right {
    width: 150px;
    height: 350px;

    .cropper-warp-right-title {
      text-align: center;
      height: 20px;
      line-height: 20px;
    }

    .cropper-warp-right-item {
      margin: 15px 0;

      .cropper-warp-right-value {
        width: 100px;
        height: 100px;
        overflow: hidden;
        margin: auto;
        border-radius: 50%;
        background: var(--el-fill-color-light);
      }

      .cropper-warp-right-value--sm {
        width: 50px;
        height: 50px;
      }

      .cropper-warp-right-label {
        text-align: center;
        font-size: 12px;
        color: var(--el-text-color-primary);
        height: 30px;
        line-height: 30px;
      }
    }
  }
}
</style>
