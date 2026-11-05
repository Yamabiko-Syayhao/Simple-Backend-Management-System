<template>
  <div class="ai-assistant" @keydown.esc.stop="closeChat">
    <section
      v-if="open"
      id="ai-assistant-chat"
      class="ai-assistant-panel"
      role="dialog"
      aria-labelledby="ai-assistant-title"
    >
      <header class="ai-assistant-header">
        <h2 id="ai-assistant-title">Yuno 商品查询助手</h2>
        <div>
          <el-button text size="small" @click="startNewChat">新对话</el-button>
          <el-button :icon="Close" circle text aria-label="关闭对话" @click="closeChat" />
        </div>
      </header>

      <div ref="transcript" class="ai-assistant-messages" role="log" aria-label="对话消息" tabindex="0">
        <p v-if="!messages.length" class="ai-assistant-hint">
          你好！你可以问我有多少商品、某个商品的信息、谁下了单，或订单现在是什么状态。
        </p>
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="ai-assistant-message"
          :class="`ai-assistant-message--${message.role}`"
        >
          <span>{{ message.role === 'user' ? '你' : 'Yuno 商品查询助手' }}</span>
          <p>{{ message.content }}</p>
        </div>
        <div v-if="partialReply" class="ai-assistant-message">
          <span>Yuno 商品查询助手</span>
          <p>{{ partialReply }}</p>
        </div>
        <p v-if="statusMessage" class="ai-assistant-hint">{{ statusMessage }}</p>
      </div>

      <form class="ai-assistant-compose" @submit.prevent="send">
        <p v-if="errorMessage" class="ai-assistant-error" role="alert">{{ errorMessage }}</p>
        <el-input
          ref="composer"
          v-model="draft"
          type="textarea"
          :rows="2"
          :maxlength="4000"
          resize="none"
          aria-label="输入问题"
          placeholder="输入问题，Enter 发送，Shift + Enter 换行"
          :readonly="sending"
          @keydown.enter="onEnter"
        />
        <div class="ai-assistant-actions">
          <span>关闭窗口后清空对话</span>
          <el-button type="primary" native-type="submit" :loading="sending" :disabled="!draft.trim()">发送</el-button>
        </div>
      </form>
    </section>

    <button
      ref="launcher"
      class="ai-assistant-launcher"
      type="button"
      :aria-expanded="open"
      :aria-controls="open ? 'ai-assistant-chat' : undefined"
      @click="toggleChat"
    >
      <el-icon><ChatDotRound /></el-icon>
      Yuno 商品查询助手
    </button>
  </div>
</template>

<script setup lang="ts">
import { ChatDotRound, Close } from '@element-plus/icons-vue';
import { nextTick, onBeforeUnmount, ref } from 'vue';
import { useAiAssistantApi, type AssistantMessage } from '/@/api/useSystemApi/aiAssistant';

const api = useAiAssistantApi();
const open = ref(false);
const messages = ref<AssistantMessage[]>([]);
const draft = ref('');
const sending = ref(false);
const errorMessage = ref('');
const partialReply = ref('');
const statusMessage = ref('');
const transcript = ref<HTMLDivElement>();
const launcher = ref<HTMLButtonElement>();
const composer = ref<{ focus: () => void }>();
let pendingRequest: AbortController | undefined;

function resetChat() {
  pendingRequest?.abort();
  pendingRequest = undefined;
  messages.value = [];
  draft.value = '';
  errorMessage.value = '';
  partialReply.value = '';
  statusMessage.value = '';
  sending.value = false;
}

function closeChat() {
  if (!open.value) return;
  open.value = false;
  resetChat();
  launcher.value?.focus();
}

async function toggleChat() {
  if (open.value) {
    closeChat();
    return;
  }
  open.value = true;
  await nextTick();
  composer.value?.focus();
}

function startNewChat() {
  resetChat();
  composer.value?.focus();
}

async function scrollToLatest() {
  await nextTick();
  if (transcript.value) transcript.value.scrollTop = transcript.value.scrollHeight;
}

function onEnter(event: KeyboardEvent) {
  if (event.isComposing || event.keyCode === 229 || event.shiftKey) return;
  event.preventDefault();
  void send();
}

async function send() {
  const content = draft.value.trim();
  if (!open.value || sending.value || !content) return;
  if ([...content].length > 2000) {
    errorMessage.value = '每条问题最多输入 2000 个字符。';
    return;
  }

  const previousMessages = messages.value;
  const conversation: AssistantMessage[] = [...previousMessages, { role: 'user', content }];
  const controller = new AbortController();
  pendingRequest = controller;
  errorMessage.value = '';
  messages.value = conversation;
  draft.value = '';
  sending.value = true;
  statusMessage.value = '正在等待回复…';
  void scrollToLatest();

  const timeout = window.setTimeout(() => controller.abort(), 65_000);
  try {
    await api.chat(conversation, controller.signal, (update) => {
      if (controller.signal.aborted) return;
      if (update.type === 'status') {
        if (update.reset === true) partialReply.value = '';
        statusMessage.value = update.text;
      } else {
        statusMessage.value = '';
        partialReply.value += update.text;
      }
      void scrollToLatest();
    });
    if (pendingRequest !== controller) return;
    const reply = partialReply.value;
    if (!reply.trim()) throw new Error('没有收到有效回复，请重试。');
    messages.value.push({ role: 'assistant', content: reply });
  } catch (error) {
    if (pendingRequest !== controller) return;
    messages.value = previousMessages;
    draft.value = content;
    if (controller.signal.aborted) {
      errorMessage.value = '等待回复超时，请重试。';
    } else if (error instanceof Error && error.name === 'Error') {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = '暂时无法取得回复，请稍后重试。';
    }
  } finally {
    window.clearTimeout(timeout);
    if (pendingRequest === controller) {
      pendingRequest = undefined;
      sending.value = false;
      partialReply.value = '';
      statusMessage.value = '';
      void scrollToLatest();
    }
  }
}

onBeforeUnmount(resetChat);
</script>

<style scoped lang="scss">
.ai-assistant {
  position: fixed;
  right: max(16px, env(safe-area-inset-right));
  bottom: max(16px, env(safe-area-inset-bottom));
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.ai-assistant-launcher {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: 0;
  border-radius: 24px;
  color: var(--el-color-white);
  background: var(--el-color-primary);
  box-shadow: var(--el-box-shadow-light);
  font-weight: 600;
  cursor: pointer;

  &:hover {
    background: var(--el-color-primary-light-3);
  }

  &:focus-visible {
    box-shadow: 0 0 0 3px var(--el-color-primary-light-5);
  }
}

.ai-assistant-panel {
  display: flex;
  flex-direction: column;
  width: min(392px, calc(100vw - 32px));
  height: min(520px, calc(100vh - 96px));
  height: min(520px, calc(100dvh - 96px));
  border: 1px solid var(--el-border-color-light);
  border-radius: 16px;
  overflow: hidden;
  color: var(--el-text-color-primary);
  background: var(--el-bg-color-overlay);
  box-shadow: var(--el-box-shadow);
}

.ai-assistant-header,
.ai-assistant-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.ai-assistant-header {
  flex: none;
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-light);

  h2 {
    margin: 0;
    font-size: 16px;
  }
}

.ai-assistant-messages {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
  overflow-y: auto;
  padding: 16px;
}

.ai-assistant-hint,
.ai-assistant-actions span,
.ai-assistant-message span {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.ai-assistant-message {
  align-self: flex-start;
  max-width: 92%;

  p {
    margin: 4px 0 0;
    padding: 8px 12px;
    border-radius: 10px;
    background: var(--el-fill-color-light);
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    line-height: 1.5;
  }
}

.ai-assistant-message--user {
  align-self: flex-end;
  text-align: right;

  p {
    background: var(--el-color-primary-light-9);
    text-align: left;
  }
}

.ai-assistant-compose {
  flex: none;
  padding: 12px 16px;
  border-top: 1px solid var(--el-border-color-light);
}

.ai-assistant-actions {
  margin-top: 8px;
}

.ai-assistant-error {
  margin: 0 0 8px;
  color: var(--el-color-danger);
  font-size: 13px;
}
</style>
