<template>
  <GoodsForm mode="edit" :goods-id="goodsId" />
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import GoodsForm from './GoodsForm.vue';

defineOptions({ name: 'goodsEdit' });
const route = useRoute();
const goodsId = computed(() => {
  const id = route.query.id;
  return typeof id === 'string' && /^\d+$/.test(id) ? Number(id) : undefined;
});
</script>
