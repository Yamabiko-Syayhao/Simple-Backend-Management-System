import { getApiBaseUrl } from '/@/utils/config';
import { showSessionExpiredDialog } from '/@/utils/request';
import { Session } from '/@/utils/storage';

export interface AssistantMessage {
  role: 'user' | 'assistant';
  content: string;
}

type AssistantUpdate =
  | { type: 'status'; text: string; reset?: true }
  | { type: 'delta'; text: string };

async function readChatStream(body: ReadableStream<Uint8Array>, onUpdate: (update: AssistantUpdate) => void) {
  const reader = body.getReader();
  const decoder = new TextDecoder('utf-8', { fatal: true });
  let pending = '';

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) throw new Error('回复连接提前关闭，请重试。');

      // 网络分块可能落在多字节字符或一行 JSON 的中间。
      const lines = (pending + decoder.decode(value, { stream: true })).split('\n');
      pending = lines.pop() ?? '';
      for (const line of lines) {
        if (!line.trim()) continue;
        const frame = JSON.parse(line);
        if (frame?.type === 'done') return;
        if (frame?.type === 'error' && typeof frame.message === 'string') {
          throw new Error(frame.message || '暂时无法取得回复，请稍后重试。');
        }
        if ((frame?.type === 'status' || frame?.type === 'delta') && typeof frame.text === 'string') {
          onUpdate(frame);
        } else {
          throw new Error('收到无法识别的回复，请重试。');
        }
      }
    }
  } finally {
    void reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}

export function useAiAssistantApi() {
  return {
    async chat(messages: AssistantMessage[], signal: AbortSignal, onUpdate: (update: AssistantUpdate) => void) {
      // UTF-8 编码支持中文，并将对话内容放在 GET 请求头中。
      const bytes = new TextEncoder().encode(JSON.stringify(messages));
      if (messages.length > 40 || Math.ceil(bytes.length * 4 / 3) > 7500) {
        throw new Error('对话内容超过长度上限，请缩短本次问题或开始新对话。');
      }

      const conversation = btoa(String.fromCharCode(...bytes))
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');
      const token = Session.get('token');
      const response = await fetch(`${getApiBaseUrl().replace(/\/+$/, '')}/ai-assistant/chat`, {
        method: 'GET',
        headers: {
          Accept: 'application/x-ndjson, application/json',
          'X-AI-Conversation': conversation,
          ...(token ? { token } : {}),
        },
        cache: 'no-store',
        signal,
      });
      const contentType = response.headers.get('Content-Type')?.split(';', 1)[0].trim().toLowerCase();
      if (response.ok && contentType === 'application/x-ndjson' && response.body) {
        return readChatStream(response.body, onUpdate);
      }

      if (contentType === 'application/json') {
        const result = await response.json().catch(() => null);
        if (result?.code === 11000 && !signal.aborted) showSessionExpiredDialog();
        if (typeof result?.msg === 'string' && result.msg) throw new Error(result.msg);
      }
      throw new Error('无法连接 Yuno 商品查询助手，请稍后重试。');
    },
  };
}
