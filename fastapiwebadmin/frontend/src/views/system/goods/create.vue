<template>
  <GoodsForm mode="create" />
</template>

<script setup lang="ts">
import GoodsForm from './GoodsForm.vue';

// 列表“添加”和侧栏“商品上架”共用此新增页，与编辑页分开。
defineOptions({ name: 'goodsCreate' });
</script>
