<script setup>
import { ref, nextTick, onMounted, watch, computed } from "vue";
import MarkdownIt from "markdown-it";
import { API_BASE_URL } from "../config/api";

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
});

const isOpen = ref(false);
const isExpanded = ref(false);
const messages = ref([]);
const inputMessage = ref("");
const isLoading = ref(false);
const showResetHighlight = ref(false);
const chatContainer = ref(null);
const chatId = ref(localStorage.getItem("chatId"));

const toolNameMap = {
  get_products: {
    start: "Getting product details...",
    end: "Retrieved product details ✔",
  },
  get_product: {
    start: "Getting product details...",
    end: "Retrieved product details ✔",
  },
  list_products: {
    start: "Listing products...",
    end: "Retrieved product list ✔",
  },
  web_search: { start: "Searching the web...", end: "Web search completed ✔" },
  keyword_search: {
    start: "Searching documents...",
    end: "Document search completed ✔",
  },
  list_documents: {
    start: "Listing documents...",
    end: "Retrieved document list ✔",
  },
  list_sections: {
    start: "Listing sections...",
    end: "Retrieved section list ✔",
  },
  read_sections: {
    start: "Reading documents...",
    end: "Retrieved document content ✔",
  },
};

const toggleChat = () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    scrollToBottom();
  }
};

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value;
  nextTick(() => {
    scrollToBottom();
  });
};

const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

const resetChat = async () => {
  try {
    const url = new URL(`${API_BASE_URL}/chat`);
    if (chatId.value) {
      url.searchParams.append("chat_id", chatId.value);
    }

    await fetch(url, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
      },
    });

    messages.value = [];
    chatId.value = null;
    localStorage.removeItem("chatId");
  } catch (error) {
    console.error("Failed to reset chat:", error);
  }
};

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return;

  const userMsg = inputMessage.value.trim();
  inputMessage.value = "";

  messages.value.push({
    role: "user",
    content: userMsg,
  });

  isLoading.value = true;
  scrollToBottom();

  let assistantMessageIndex = -1;

  try {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
      },
      body: JSON.stringify({
        message: userMsg,
        chat_id: chatId.value,
      }),
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);

          try {
            const event = JSON.parse(data);

            if (event.type === "chat_id" && !chatId.value) {
              chatId.value = event.chat_id;
              localStorage.setItem("chatId", event.chat_id);
            } else if (event.type === "content") {
              if (assistantMessageIndex === -1) {
                isLoading.value = false;
                assistantMessageIndex = messages.value.length;
                messages.value.push({
                  role: "assistant",
                  content: "",
                  toolMessages: [],
                  isStreaming: true,
                });
              }
              messages.value[assistantMessageIndex].content += event.content;
              scrollToBottom();
            } else if (event.type === "tool_call_start") {
              if (assistantMessageIndex === -1) {
                isLoading.value = false;
                assistantMessageIndex = messages.value.length;
                messages.value.push({
                  role: "assistant",
                  content: "",
                  toolMessages: [],
                  isStreaming: true,
                });
              }
              const toolMsg =
                toolNameMap[event.tool_name]?.start ||
                `Using tool: ${event.tool_name}`;
              messages.value[assistantMessageIndex].toolMessages.push(toolMsg);
              scrollToBottom();
            } else if (event.type === "tool_call_end") {
              const toolMsg =
                toolNameMap[event.tool_name]?.end ||
                `Tool ${event.tool_name} completed`;
              messages.value[assistantMessageIndex].toolMessages.push(toolMsg);
              scrollToBottom();
            } else if (event.type === "done") {
              if (assistantMessageIndex !== -1) {
                messages.value[assistantMessageIndex].isStreaming = false;
              }
              isLoading.value = false;
              scrollToBottom();
            } else if (event.type === "error") {
              if (assistantMessageIndex === -1) {
                isLoading.value = false;
                assistantMessageIndex = messages.value.length;
                messages.value.push({
                  role: "assistant",
                  content: "",
                  toolMessages: [],
                  isStreaming: false,
                });
              }
              messages.value[
                assistantMessageIndex
              ].content = `Error: ${event.error}`;
              messages.value[assistantMessageIndex].isStreaming = false;
              isLoading.value = false;
              scrollToBottom();
            }
          } catch (parseError) {
            console.error("Failed to parse SSE data:", parseError);
          }
        }
      }
    }

    if (assistantMessageIndex !== -1) {
      messages.value[assistantMessageIndex].isStreaming = false;
    }
    isLoading.value = false;
  } catch (error) {
    console.error("Error sending message:", error);
    if (assistantMessageIndex === -1) {
      isLoading.value = false;
      assistantMessageIndex = messages.value.length;
      messages.value.push({
        role: "assistant",
        content: "",
        toolMessages: [],
        isStreaming: false,
      });
    }
    messages.value[assistantMessageIndex].content =
      "Sorry, something went wrong. Please try again.";
    messages.value[assistantMessageIndex].isStreaming = false;
    isLoading.value = false;
  } finally {
    isLoading.value = false;
    scrollToBottom();
  }
};

const renderMarkdown = (content) => {
  return md.render(content);
};

const loadChatHistory = async () => {
  if (!chatId.value) return;

  try {
    const url = new URL(`${API_BASE_URL}/chat/history`);
    url.searchParams.append("chat_id", chatId.value);

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to load chat history");
    }

    const data = await response.json();
    messages.value = data.messages;
    scrollToBottom();
  } catch (error) {
    console.error("Error loading chat history:", error);
    chatId.value = null;
    localStorage.removeItem("chatId");
  }
};

onMounted(() => {
  loadChatHistory();
});

// Initial welcome message (optional, handled by empty state in UI)
</script>

<template>
  <div class="chat-widget">
    <!-- Chat Button -->
    <button
      class="chat-toggle-btn"
      @click="toggleChat"
      :class="{ hidden: isOpen }"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M12 6V2H8" />
        <path d="M15 11v2" />
        <path d="M2 12h2" />
        <path d="M20 12h2" />
        <path
          d="M20 16a2 2 0 0 1-2 2H8.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 4 20.286V8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2z"
        />
        <path d="M9 11v2" />
      </svg>
    </button>

    <!-- Chat Interface -->
    <div v-if="isOpen" class="chat-window" :class="{ expanded: isExpanded }">
      <div class="chat-header">
        <div class="header-content">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="header-icon"
          >
            <path d="M12 6V2H8" />
            <path d="M15 11v2" />
            <path d="M2 12h2" />
            <path d="M20 12h2" />
            <path
              d="M20 16a2 2 0 0 1-2 2H8.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 4 20.286V8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2z"
            />
            <path d="M9 11v2" />
          </svg>
          <h3>AI Advisor</h3>
        </div>
        <div class="header-actions">
          <button @click="resetChat" class="action-btn" title="Reset Chat">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
              <path d="M3 3v5h5" />
            </svg>
          </button>
          <button
            @click="toggleExpand"
            class="action-btn expand-btn"
            :title="isExpanded ? 'Minimize' : 'Expand'"
          >
            <span
              class="icon-mask"
              :class="isExpanded ? 'minimize-icon' : 'expand-icon'"
            ></span>
          </button>
          <button @click="toggleChat" class="action-btn" title="Close">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M18 6 6 18" />
              <path d="m6 6 12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div class="chat-messages" ref="chatContainer">
        <div v-if="messages.length === 0" class="empty-state">
          <p>
            Hello! I'm your AI advisor. How can I help you find the perfect GPU
            today?
          </p>
        </div>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message"
          :class="msg.role"
        >
          <div
            v-if="msg.toolMessages && msg.toolMessages.length > 0"
            class="tool-messages"
          >
            <div
              v-for="(toolMsg, toolIndex) in msg.toolMessages"
              :key="toolIndex"
              class="tool-message"
            >
              {{ toolMsg }}
            </div>
          </div>
          <div
            v-if="msg.content"
            class="message-content"
            v-html="renderMarkdown(msg.content)"
          ></div>
          <div v-if="msg.isStreaming && !isLoading" class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>

        <div v-if="isLoading" class="message assistant loading">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <form @submit.prevent="sendMessage">
          <input
            v-model="inputMessage"
            type="text"
            placeholder="Ask about GPUs..."
            :disabled="isLoading"
          />
          <button type="submit" :disabled="!inputMessage.trim() || isLoading">
            <img src="/icons/arrow-up.svg" alt="Send" />
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-widget {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 1000;
}

.chat-toggle-btn {
  width: 50px;
  height: 50px;
  border-radius: 0;
  background: var(--secondary);
  border: 1px solid var(--border);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-lg);
  transition: transform 0.2s, opacity 0.2s;
  color: var(--primary);
}

.chat-toggle-btn:hover {
  transform: scale(1.05);
}

.chat-toggle-btn.hidden {
  opacity: 0;
  pointer-events: none;
  transform: scale(0.8);
}

.chat-toggle-btn svg {
  width: 24px;
  height: 24px;
}

.chat-window {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 380px;
  height: 600px;
  background: var(--background);
  border-radius: 0;
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
  border: 1px solid var(--border);
  transition: width 0.3s ease-out, height 0.3s ease-out, top 0.3s ease-out,
    left 0.3s ease-out, right 0.3s ease-out, bottom 0.3s ease-out,
    transform 0.3s ease-out, position 0.3s ease-out;
}

.chat-window.expanded {
  position: fixed;
  top: 50%;
  left: 50%;
  right: auto;
  bottom: auto;
  transform: translate(-50%, -50%);
  width: 800px;
  height: 700px;
  max-width: 90vw;
  max-height: 90vh;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.chat-header {
  padding: 1rem;
  background: var(--card);
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-icon {
  width: 24px;
  height: 24px;
  color: var(--primary);
}

.chat-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--foreground);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s, background 0.2s;
  border-radius: 0;
  color: var(--foreground);
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  opacity: 1;
  background: var(--muted);
}

.action-btn svg {
  width: 20px;
  height: 20px;
}

.icon-mask {
  width: 20px;
  height: 20px;
  display: block;
  background-color: var(--foreground);
  -webkit-mask-size: contain;
  mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  mask-repeat: no-repeat;
  -webkit-mask-position: center;
  mask-position: center;
}

.expand-icon {
  -webkit-mask-image: url("/icons/expand.svg");
  mask-image: url("/icons/expand.svg");
}

.minimize-icon {
  -webkit-mask-image: url("/icons/minimize.svg");
  mask-image: url("/icons/minimize.svg");
}

.chat-messages {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  background: var(--muted);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: relative;
}

.empty-state {
  text-align: center;
  color: var(--muted-foreground);
  padding: 0 1rem;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
}

.message {
  max-width: 85%;
  padding: 0.75rem 1rem;
  border-radius: 0;
  font-size: 0.95rem;
  line-height: 1.5;
}

.message-content {
  overflow-wrap: break-word;
  word-wrap: break-word;
}

.message.user {
  background: var(--primary);
  color: var(--primary-foreground);
  align-self: flex-end;
}

.message.assistant {
  background: var(--card);
  color: var(--card-foreground);
  border: 1px solid var(--border);
  align-self: flex-start;
}

.message-content :deep(p) {
  margin: 0;
}

.message-content :deep(p + p) {
  margin-top: 0.5rem;
}

.message-content :deep(ul),
.message-content :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.message-content :deep(li) {
  margin: 0.25rem 0;
}

.message-content :deep(code) {
  background: var(--muted);
  padding: 0.125rem 0.25rem;
  font-family: var(--font-mono);
  font-size: 0.875em;
}

.message-content :deep(pre) {
  background: var(--muted);
  padding: 0.5rem;
  overflow-x: auto;
  margin: 0.5rem 0;
}

.message-content :deep(pre code) {
  background: none;
  padding: 0;
}

.message-content :deep(strong) {
  font-weight: 600;
}

.message-content :deep(em) {
  font-style: italic;
}

.tool-messages {
  margin-bottom: 0.5rem;
}

.tool-message {
  color: var(--muted-foreground);
  font-style: italic;
  font-size: 0.9em;
  margin: 0.25rem 0;
}

.message-content :deep(a) {
  color: var(--primary);
  text-decoration: underline;
}

.message-content :deep(h1),
.message-content :deep(h2),
.message-content :deep(h3),
.message-content :deep(h4),
.message-content :deep(h5),
.message-content :deep(h6) {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.message-content :deep(h1:first-child),
.message-content :deep(h2:first-child),
.message-content :deep(h3:first-child),
.message-content :deep(h4:first-child),
.message-content :deep(h5:first-child),
.message-content :deep(h6:first-child) {
  margin-top: 0;
}

.message-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.5rem 0;
  border: 1px solid var(--border);
}

.message-content :deep(th),
.message-content :deep(td) {
  border: 1px solid var(--border);
  padding: 0.5rem;
  text-align: left;
}

.message-content :deep(th) {
  background: var(--muted);
  font-weight: 600;
}

.message-content :deep(tr:nth-child(even)) {
  background: var(--muted);
}

.chat-input-area {
  padding: 1rem;
  background: var(--card);
  border-top: 1px solid var(--border);
}

.chat-input-area form {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.chat-input-area input {
  flex: 1;
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 0;
  outline: none;
  font-size: 0.95rem;
  background: var(--background);
  color: var(--foreground);
}

.chat-input-area input:focus {
  border-color: var(--ring);
}

.chat-input-area button {
  width: 40px;
  height: 40px;
  border-radius: 0;
  background: var(--primary);
  border: none;
  color: var(--primary-foreground);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.chat-input-area button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chat-input-area button img {
  width: 16px;
  height: 16px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: var(--muted-foreground);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}
.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

@media (max-width: 768px) {
  .chat-widget {
    bottom: 1rem;
    right: 1rem;
    left: 1rem;
  }

  .chat-window {
    width: 100%;
    height: 500px;
    max-width: 100%;
    left: 0;
    right: 0;
  }

  .chat-toggle-btn {
    margin-left: auto;
  }

  .expand-btn {
    display: none;
  }

  .chat-window.expanded {
    width: 100%;
    height: 500px;
    max-width: 100%;
    left: 0;
    right: 0;
    top: auto;
    bottom: 0;
    transform: none;
    position: absolute;
  }
}
</style>
