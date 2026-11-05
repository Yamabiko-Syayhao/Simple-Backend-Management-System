<template><TopicForm mode="edit" :topic-id="topicId" /></template>
<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import TopicForm from './TopicForm.vue';
defineOptions({ name: 'promotionTopicEdit' });
const route = useRoute();
const topicId = computed(() => {
  const raw = route.query.id;
  if (typeof raw !== 'string' || !/^\d+$/.test(raw)) return undefined;
  const id = Number(raw);
  return Number.isSafeInteger(id) && id > 0 ? id : undefined;
});
</script>
