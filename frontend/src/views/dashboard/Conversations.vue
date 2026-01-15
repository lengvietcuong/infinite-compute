<script setup>
import { ref, onMounted, computed } from "vue";
import MarkdownIt from "markdown-it";
import { useAuth } from "../../composables/useAuth";
import { useToast } from "../../composables/useToast";
import Table from "../../components/ui/table/Table.vue";
import TableHeader from "../../components/ui/table/TableHeader.vue";
import TableRow from "../../components/ui/table/TableRow.vue";
import TableHead from "../../components/ui/table/TableHead.vue";
import TableBody from "../../components/ui/table/TableBody.vue";
import TableCell from "../../components/ui/table/TableCell.vue";
import Modal from "../../components/ui/Modal.vue";
import Skeleton from "../../components/Skeleton.vue";

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
});

const { token } = useAuth();
const { showToast } = useToast();
const conversations = ref([]);
const isLoading = ref(false);
const conversationToDelete = ref(null);
const isDeleteModalOpen = ref(false);
const isViewModalOpen = ref(false);
const selectedConversation = ref(null);

const searchQuery = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const sortColumn = ref("");
const sortDirection = ref("asc");

const fetchConversations = async () => {
  isLoading.value = true;
  try {
    const response = await fetch("/api/conversations", {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    if (response.ok) {
      conversations.value = await response.json();
    }
  } catch (error) {
    console.error("Failed to fetch conversations:", error);
  } finally {
    isLoading.value = false;
  }
};

const fetchStats = async () => {
  try {
    const response = await fetch("/api/conversations/stats", {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    if (response.ok) {
      await response.json();
    }
  } catch (error) {
    console.error("Failed to fetch conversation stats:", error);
  }
};

onMounted(() => {
  fetchConversations();
  fetchStats();
});

const filteredConversations = computed(() => {
  let result = [...conversations.value];

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(
      (conv) =>
        conv.user_name?.toLowerCase().includes(query) ||
        conv.user_email?.toLowerCase().includes(query) ||
        conv.id.toLowerCase().includes(query)
    );
  }

  if (sortColumn.value) {
    result.sort((a, b) => {
      let valA = a[sortColumn.value];
      let valB = b[sortColumn.value];

      if (typeof valA === "string") valA = valA.toLowerCase();
      if (typeof valB === "string") valB = valB.toLowerCase();

      if (valA < valB) return sortDirection.value === "asc" ? -1 : 1;
      if (valA > valB) return sortDirection.value === "asc" ? 1 : -1;
      return 0;
    });
  } else {
    result.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
  }

  return result;
});

const totalPages = computed(
  () => Math.ceil(filteredConversations.value.length / pageSize.value) || 1
);

const paginatedConversations = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredConversations.value.slice(start, start + pageSize.value);
});

const handleSort = (column) => {
  if (sortColumn.value === column) {
    if (sortDirection.value === "asc") {
      sortDirection.value = "desc";
    } else if (sortDirection.value === "desc") {
      sortColumn.value = "";
      sortDirection.value = "asc";
    }
  } else {
    sortColumn.value = column;
    sortDirection.value = "asc";
  }
};

const goToFirstPage = () => {
  if (currentPage.value !== 1) currentPage.value = 1;
};

const goToLastPage = () => {
  if (currentPage.value !== totalPages.value)
    currentPage.value = totalPages.value;
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++;
};

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--;
};

const openViewModal = async (conversation) => {
  try {
    const response = await fetch(`/api/conversations/${conversation.id}`, {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    if (response.ok) {
      selectedConversation.value = await response.json();
      isViewModalOpen.value = true;
    } else {
      showToast("Failed to load conversation details", "error");
    }
  } catch (error) {
    console.error("Error loading conversation:", error);
    showToast("An error occurred", "error");
  }
};

const closeViewModal = () => {
  isViewModalOpen.value = false;
  selectedConversation.value = null;
};

const openDeleteModal = (conversation) => {
  conversationToDelete.value = conversation;
  isDeleteModalOpen.value = true;
};

const closeDeleteModal = () => {
  isDeleteModalOpen.value = false;
  conversationToDelete.value = null;
};

const deleteConversation = async () => {
  if (!conversationToDelete.value) return;

  try {
    const response = await fetch(
      `/api/conversations/${conversationToDelete.value.id}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      }
    );

    if (response.ok) {
      await fetchConversations();
      closeDeleteModal();
      showToast("Conversation deleted successfully", "success");
    } else {
      showToast("Failed to delete conversation", "error");
    }
  } catch (error) {
    console.error("Error deleting conversation:", error);
    showToast("An error occurred", "error");
  }
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const renderMarkdown = (content) => {
  return md.render(content);
};
</script>

<template>
  <div>
    <div class="flex items-center justify-between gap-3 header-row flex-wrap">
      <div class="flex items-center gap-3 md:gap-4 flex-1 min-w-0">
        <h2 class="text-2xl font-bold tracking-tight">Conversations</h2>
        <div class="search-wrapper">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="search-icon"
          >
            <path d="m21 21-4.34-4.34" />
            <circle cx="11" cy="11" r="8" />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search conversations..."
            class="search-input"
          />
        </div>
      </div>
    </div>

    <div
      class="border bg-card text-card-foreground shadow-sm border-color table-wrapper table-wrapper-scroll"
      role="region"
      aria-label="Conversations table"
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>User</TableHead>
            <TableHead
              @click="handleSort('message_count')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Messages
                <svg
                  v-if="sortColumn !== 'message_count'"
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon"
                >
                  <path d="m21 16-4 4-4-4" />
                  <path d="M17 20V4" />
                  <path d="m3 8 4-4 4 4" />
                  <path d="M7 4v16" />
                </svg>
                <svg
                  v-else-if="sortDirection === 'asc'"
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon sort-icon-active"
                >
                  <path d="m5 12 7-7 7 7" />
                  <path d="M12 19V5" />
                </svg>
                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon sort-icon-active"
                >
                  <path d="M12 5v14" />
                  <path d="m19 12-7 7-7-7" />
                </svg>
              </div>
            </TableHead>
            <TableHead>Created</TableHead>
            <TableHead>Last Updated</TableHead>
            <TableHead class="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody v-if="isLoading">
          <TableRow v-for="i in pageSize" :key="i">
            <TableCell><Skeleton class="h-4 w-32" /></TableCell>
            <TableCell><Skeleton class="h-4 w-16" /></TableCell>
            <TableCell><Skeleton class="h-4 w-24" /></TableCell>
            <TableCell><Skeleton class="h-4 w-24" /></TableCell>
            <TableCell><Skeleton class="h-8 w-20 ml-auto" /></TableCell>
          </TableRow>
        </TableBody>
        <TableBody v-else-if="paginatedConversations.length === 0">
          <TableRow>
            <TableCell colspan="5" class="text-center">
              No conversations found
            </TableCell>
          </TableRow>
        </TableBody>
        <TableBody v-else>
          <TableRow
            v-for="conversation in paginatedConversations"
            :key="conversation.id"
          >
            <TableCell>
              <div>
                <div class="font-medium">
                  {{ conversation.user_name || "Guest" }}
                </div>
                <div class="text-sm text-muted-foreground">
                  {{ conversation.user_email || conversation.id.slice(0, 8) }}
                </div>
              </div>
            </TableCell>
            <TableCell>{{ conversation.message_count }}</TableCell>
            <TableCell>{{ formatDate(conversation.created_at) }}</TableCell>
            <TableCell>{{ formatDate(conversation.updated_at) }}</TableCell>
            <TableCell class="text-right">
              <div class="flex justify-end gap-2">
                <button
                  @click="openViewModal(conversation)"
                  class="action-btn"
                  title="View"
                  aria-label="View conversation"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                </button>
                <button
                  @click="openDeleteModal(conversation)"
                  class="action-btn delete-btn"
                  title="Delete"
                  aria-label="Delete conversation"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M3 6h18" />
                    <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                    <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                  </svg>
                </button>
              </div>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <div class="pagination" v-if="totalPages > 1">
      <button
        @click="goToFirstPage"
        :disabled="currentPage === 1"
        class="btn btn-outline btn-sm"
        aria-label="Go to first page"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="m11 17-5-5 5-5" />
          <path d="m18 17-5-5 5-5" />
        </svg>
      </button>
      <button
        @click="prevPage"
        :disabled="currentPage === 1"
        class="btn btn-outline btn-sm"
        aria-label="Go to previous page"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="m15 18-6-6 6-6" />
        </svg>
      </button>
      <span class="pagination-info">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      <button
        @click="nextPage"
        :disabled="currentPage === totalPages"
        class="btn btn-outline btn-sm"
        aria-label="Go to next page"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="m9 18 6-6-6-6" />
        </svg>
      </button>
      <button
        @click="goToLastPage"
        :disabled="currentPage === totalPages"
        class="btn btn-outline btn-sm"
        aria-label="Go to last page"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="m6 17 5-5-5-5" />
          <path d="m13 17 5-5-5-5" />
        </svg>
      </button>
    </div>

    <Modal :isOpen="isViewModalOpen" @close="closeViewModal" size="large">
      <template #header>
        Conversation Details
        <div class="text-sm font-normal text-muted-foreground mt-1">
          {{ selectedConversation?.user_name || "Guest" }}
          <span v-if="selectedConversation?.user_email">
            ({{ selectedConversation.user_email }})
          </span>
        </div>
      </template>
      <template #default>
        <div class="conversation-messages">
          <div
            v-for="message in selectedConversation?.messages"
            :key="message.id"
            :class="[
              'message-bubble',
              message.role === 'user' ? 'message-user' : 'message-assistant',
            ]"
          >
            <div class="message-header">
              <span class="message-role">{{
                message.role === "user" ? "User" : "Assistant"
              }}</span>
              <span class="message-time">{{
                formatDate(message.created_at)
              }}</span>
            </div>
            <div
              class="message-content"
              v-html="renderMarkdown(message.content)"
            ></div>
          </div>
          <div
            v-if="!selectedConversation?.messages?.length"
            class="text-center text-muted-foreground"
          >
            No messages in this conversation
          </div>
        </div>
      </template>
      <template #footer>
        <button @click="closeViewModal" class="btn btn-outline">Close</button>
      </template>
    </Modal>

    <Modal :isOpen="isDeleteModalOpen" @close="closeDeleteModal">
      <template #header>Delete Conversation</template>
      <template #default>
        <p>
          Are you sure you want to delete this conversation? This action cannot
          be undone.
        </p>
      </template>
      <template #footer>
        <button @click="closeDeleteModal" class="btn btn-outline">
          Cancel
        </button>
        <button @click="deleteConversation" class="btn btn-destructive">
          Delete
        </button>
      </template>
    </Modal>
  </div>
</template>

<style scoped>
.header-row {
  margin-bottom: var(--spacing-lg);
}

.search-wrapper {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: var(--spacing-sm);
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted-foreground);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-sm) var(--spacing-sm)
    var(--spacing-xl);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background-color: var(--background);
  color: var(--foreground);
  font-size: var(--text-sm);
  transition: all var(--transition-base);
}

.search-input:focus {
  outline: none;
  border-color: var(--ring);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--ring), transparent 50%);
}

.filter-wrapper {
  flex-shrink: 0;
}

.form-select {
  padding: var(--spacing-sm) var(--spacing-lg) var(--spacing-sm)
    var(--spacing-sm);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background-color: var(--background);
  color: var(--foreground);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--transition-base);
}

.form-select:focus {
  outline: none;
  border-color: var(--ring);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--ring), transparent 50%);
}

.table-wrapper {
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: var(--spacing-lg);
}

.table-wrapper-scroll {
  overflow-x: auto;
}

.sort-icon {
  flex-shrink: 0;
  opacity: 0.4;
  transition: opacity var(--transition-base);
}

.sort-icon-active {
  opacity: 1;
  color: var(--primary);
}

.cursor-pointer {
  cursor: pointer;
}

.select-none {
  user-select: none;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.pagination-info {
  font-size: var(--text-sm);
  color: var(--muted-foreground);
  margin: 0 var(--spacing-xs);
}

.conversation-messages {
  max-height: 500px;
  overflow-y: auto;
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.message-bubble {
  padding: 0.75rem 1rem;
  border-radius: 0;
  border: 1px solid var(--border);
}

.message-user {
  background: var(--primary);
  color: var(--primary-foreground);
  border-left: none;
}

.message-user .message-header,
.message-user .message-role,
.message-user .message-time {
  color: var(--primary-foreground);
}

.message-assistant {
  background: var(--card);
  color: var(--card-foreground);
  border-left: none;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
  font-size: var(--text-xs);
}

.message-role {
  font-weight: 600;
  text-transform: uppercase;
  color: var(--foreground);
}

.message-time {
  color: var(--muted-foreground);
}

.message-content {
  font-size: 0.95rem;
  line-height: 1.5;
  overflow-wrap: break-word;
  word-wrap: break-word;
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

.message-content :deep(a) {
  color: var(--primary);
  text-decoration: underline;
}

.message-content :deep(blockquote) {
  border-left: 3px solid var(--muted-foreground);
  padding-left: 1rem;
  margin: 0.5rem 0;
  color: var(--muted-foreground);
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

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  padding: 0;
  background-color: transparent;
  border: none;
  cursor: pointer;
  border-radius: var(--radius);
  transition: all var(--transition-base);
  color: var(--foreground);
}

.action-btn:hover {
  background-color: var(--accent);
  color: var(--primary);
}

.action-btn.delete-btn:hover {
  color: var(--destructive);
  background-color: color-mix(in srgb, var(--destructive), transparent 90%);
}

.action-btn svg {
  pointer-events: none;
}

@media (max-width: 767px) {
  .search-wrapper {
    max-width: none;
  }

  .header-row {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-wrapper {
    width: 100%;
  }

  .form-select {
    width: 100%;
  }
}
</style>
