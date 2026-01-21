<script setup>
import { ref, onMounted, computed } from "vue";
import { useAuth } from "../../composables/useAuth";
import { useToast } from "../../composables/useToast";
import { API_BASE_URL } from "../../config/api";
import Table from "../../components/ui/table/Table.vue";
import TableHeader from "../../components/ui/table/TableHeader.vue";
import TableRow from "../../components/ui/table/TableRow.vue";
import TableHead from "../../components/ui/table/TableHead.vue";
import TableBody from "../../components/ui/table/TableBody.vue";
import TableCell from "../../components/ui/table/TableCell.vue";
import Modal from "../../components/ui/Modal.vue";
import Skeleton from "../../components/Skeleton.vue";

const { token, user } = useAuth();
const { showToast } = useToast();
const newsArticles = ref([]);
const isLoading = ref(false);
const isModalOpen = ref(false);
const isEditing = ref(false);
const newsToDelete = ref(null);
const isDeleteModalOpen = ref(false);

const searchQuery = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const sortColumn = ref("");
const sortDirection = ref("asc");

const formData = ref({
  title: "",
  content: "",
  category: "",
  summary: "",
  published_date: "",
  source: "",
  image_url: "",
});

const canCreate = computed(() => user.value?.role === "admin" || user.value?.role === "staff");
const canDelete = computed(() => user.value?.role === "admin");

const fetchNews = async () => {
  isLoading.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/news?limit=1000`, {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    if (response.ok) {
      const data = await response.json();
      newsArticles.value = data.items || [];
    }
  } catch (error) {
    console.error("Failed to fetch news:", error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchNews);

const filteredNews = computed(() => {
  let result = [...newsArticles.value];

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(
      (article) =>
        (article.title && article.title.toLowerCase().includes(query)) ||
        (article.content && article.content.toLowerCase().includes(query)) ||
        (article.category && article.category.toLowerCase().includes(query)) ||
        (article.source && article.source.toLowerCase().includes(query))
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
    result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  }

  return result;
});

const totalPages = computed(
  () => Math.ceil(filteredNews.value.length / pageSize.value) || 1
);

const paginatedNews = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredNews.value.slice(start, start + pageSize.value);
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

const openCreate = () => {
  isEditing.value = false;
  formData.value = {
    title: "",
    content: "",
    category: "AI Hardware",
    summary: "",
    published_date: new Date().toISOString().split("T")[0],
    source: "",
    image_url: "",
  };
  isModalOpen.value = true;
};

const openEdit = (article) => {
  isEditing.value = true;
  formData.value = {
    id: article.id,
    title: article.title || "",
    content: article.content || "",
    category: article.category || "",
    summary: article.summary || "",
    published_date: article.published_date || "",
    source: article.source || "",
    image_url: article.image_url || "",
  };
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const saveNews = async () => {
  try {
    const url = isEditing.value
      ? `${API_BASE_URL}/news/${formData.value.id}`
      : `${API_BASE_URL}/news`;

    const method = isEditing.value ? "PATCH" : "POST";

    const payload = { ...formData.value };
    if (!isEditing.value) {
      delete payload.id;
    }

    const response = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token.value}`,
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      await fetchNews();
      closeModal();
      showToast(
        isEditing.value
          ? "News article updated successfully"
          : "News article created successfully",
        "success"
      );
    } else {
      const data = await response.json();
      showToast(
        data.detail ||
          (isEditing.value
            ? "Failed to update news article"
            : "Failed to create news article"),
        "error"
      );
    }
  } catch (error) {
    console.error("Error saving news:", error);
  }
};

const openDeleteModal = (article) => {
  newsToDelete.value = article;
  isDeleteModalOpen.value = true;
};

const closeDeleteModal = () => {
  isDeleteModalOpen.value = false;
  newsToDelete.value = null;
};

const deleteNews = async () => {
  if (!newsToDelete.value) return;

  try {
    const response = await fetch(
      `${API_BASE_URL}/news/${newsToDelete.value.id}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      }
    );

    if (response.ok) {
      newsArticles.value = newsArticles.value.filter(
        (article) => article.id !== newsToDelete.value.id
      );
      closeDeleteModal();
      showToast("News article deleted successfully", "success");
    } else {
      showToast("Failed to delete news article", "error");
    }
  } catch (error) {
    console.error("Error deleting news:", error);
  }
};

const formatDate = (dateString) => {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

const truncateText = (text, maxLength = 100) => {
  if (!text) return "";
  return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
};
</script>

<template>
  <div>
    <div class="flex items-center justify-between gap-3 header-row flex-wrap">
      <div class="flex items-center gap-3 md:gap-4 flex-1 min-w-0">
        <h2 class="text-2xl font-bold tracking-tight">News</h2>
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
            placeholder="Search news..."
            class="search-input"
          />
        </div>
      </div>
      <button
        v-if="canCreate"
        @click="openCreate"
        class="btn btn-primary gap-2 whitespace-nowrap"
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
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        <span class="d-none d-sm-inline">Add Article</span>
        <span class="d-sm-none">Add</span>
      </button>
    </div>

    <div
      class="border bg-card text-card-foreground shadow-sm border-color table-wrapper table-wrapper-scroll"
      role="region"
      aria-label="News table"
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Image</TableHead>
            <TableHead
              @click="handleSort('title')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Title
                <svg
                  v-if="sortColumn !== 'title'"
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
            <TableHead
              @click="handleSort('category')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Category
                <svg
                  v-if="sortColumn !== 'category'"
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
            <TableHead>Summary</TableHead>
            <TableHead>Content</TableHead>
            <TableHead
              @click="handleSort('published_date')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Published
                <svg
                  v-if="sortColumn !== 'published_date'"
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
            <TableHead class="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <template v-if="isLoading">
            <TableRow v-for="i in 5" :key="i">
              <TableCell><Skeleton class="h-10 w-10" /></TableCell>
              <TableCell><Skeleton class="h-4 w-48" /></TableCell>
              <TableCell><Skeleton class="h-4 w-24" /></TableCell>
              <TableCell><Skeleton class="h-4 w-64" /></TableCell>
              <TableCell><Skeleton class="h-4 w-64" /></TableCell>
              <TableCell><Skeleton class="h-4 w-24" /></TableCell>
              <TableCell class="text-right">
                <div class="flex justify-end gap-2">
                  <Skeleton class="h-8 w-8" />
                  <Skeleton class="h-8 w-8" />
                </div>
              </TableCell>
            </TableRow>
          </template>
          <template v-else-if="paginatedNews.length === 0">
            <TableRow>
              <TableCell colspan="7" class="text-center py-8 text-muted-foreground">
                No news articles found.
              </TableCell>
            </TableRow>
          </template>
          <template v-else>
            <TableRow v-for="article in paginatedNews" :key="article.id">
              <TableCell>
                <div class="product-image-preview">
                  <img
                    v-if="article.image_url"
                    :src="article.image_url"
                    :alt="article.title"
                    class="news-image"
                    @error="$event.target.src = '/images/placeholder-product.png'"
                  />
                  <div v-else class="placeholder-image">
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
                      class="text-muted-foreground opacity-50"
                    >
                      <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
                      <circle cx="8.5" cy="8.5" r="1.5" />
                      <path d="m21 15-5-5L5 21" />
                    </svg>
                  </div>
                </div>
              </TableCell>
              <TableCell class="font-medium">
                {{ truncateText(article.title, 60) }}
              </TableCell>
              <TableCell>
                {{ article.category || "N/A" }}
              </TableCell>
              <TableCell class="text-xs text-muted-foreground">
                {{ truncateText(article.summary, 80) || "N/A" }}
              </TableCell>
              <TableCell class="text-xs text-muted-foreground">
                {{ truncateText(article.content, 80) || "N/A" }}
              </TableCell>
              <TableCell>{{ formatDate(article.published_date) }}</TableCell>
              <TableCell class="text-right">
                <div class="flex justify-end gap-2">
                  <button
                    @click="openEdit(article)"
                    class="action-btn"
                    aria-label="Edit article"
                    title="Edit"
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
                      <path
                        d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"
                      />
                      <path
                        d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
                      />
                    </svg>
                  </button>
                  <button
                    v-if="canDelete"
                    @click="openDeleteModal(article)"
                    class="action-btn delete-btn"
                    aria-label="Delete article"
                    title="Delete"
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
          </template>
        </TableBody>
      </Table>
    </div>

    <div class="pagination-wrapper">
      <button
        @click="goToFirstPage"
        :disabled="currentPage <= 1"
        class="btn-pagination"
        aria-label="Go to first page"
      >
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
          <path d="m18 17-5-5 5-5" />
          <path d="m11 17-5-5 5-5" />
        </svg>
      </button>
      <button
        @click="prevPage"
        :disabled="currentPage <= 1"
        class="btn-pagination"
        aria-label="Go to previous page"
      >
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
          <path d="m15 18-6-6 6-6" />
        </svg>
      </button>
      <span class="d-flex align-items-center font-mono text-muted"
        >Page {{ currentPage }}/{{ totalPages }}</span
      >
      <button
        @click="nextPage"
        :disabled="currentPage >= totalPages"
        class="btn-pagination"
        aria-label="Go to next page"
      >
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
          <path d="m9 18 6-6-6-6" />
        </svg>
      </button>
      <button
        @click="goToLastPage"
        :disabled="currentPage >= totalPages"
        class="btn-pagination"
        aria-label="Go to last page"
      >
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
          <path d="m6 17 5-5-5-5" />
          <path d="m13 17 5-5-5-5" />
        </svg>
      </button>
    </div>

    <Modal
      :isOpen="isModalOpen"
      :title="isEditing ? 'Edit News Article' : 'Add News Article'"
      @close="closeModal"
    >
      <div class="modal-content-padding">
        <div class="space-y-4 max-h-[70vh] overflow-y-auto">
          <div>
            <label class="form-label">Title *</label>
            <input v-model="formData.title" class="form-control" required />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="form-label">Category</label>
              <input
                v-model="formData.category"
                class="form-control"
                placeholder="e.g., AI Hardware, GPU Technology"
              />
            </div>
            <div>
              <label class="form-label">Published Date</label>
              <input
                type="date"
                v-model="formData.published_date"
                class="form-control"
              />
            </div>
          </div>
          <div>
            <label class="form-label">Source</label>
            <input
              v-model="formData.source"
              class="form-control"
              placeholder="e.g., TechCrunch, NVIDIA Blog"
            />
          </div>
          <div>
            <label class="form-label">Image URL</label>
            <input
              v-model="formData.image_url"
              class="form-control"
              placeholder="https://..."
            />
          </div>
          <div>
            <label class="form-label">Summary</label>
            <textarea
              v-model="formData.summary"
              rows="3"
              class="form-control"
              placeholder="Brief summary of the article..."
            ></textarea>
          </div>
          <div>
            <label class="form-label">Content *</label>
            <textarea
              v-model="formData.content"
              rows="8"
              class="form-control"
              placeholder="Full article content..."
              required
            ></textarea>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeModal" class="btn btn-outline">Cancel</button>
          <button @click="saveNews" class="btn btn-primary">
            Save Changes
          </button>
        </div>
      </div>
    </Modal>

    <Modal
      :isOpen="isDeleteModalOpen"
      title="Delete News Article"
      @close="closeDeleteModal"
    >
      <div class="modal-content-padding">
        <p>
          Are you sure you want to delete
          <strong>{{ newsToDelete?.title }}</strong
          >? This action cannot be undone.
        </p>
        <div class="modal-actions">
          <button @click="closeDeleteModal" class="btn btn-outline">
            Cancel
          </button>
          <button @click="deleteNews" class="btn btn-destructive">
            Delete
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<style scoped>
:deep(.border-b) {
  border-color: var(--border);
}

.search-wrapper {
  position: relative;
  display: inline-block;
  flex: 1;
  max-width: 300px;
  min-width: 0;
}

@media (max-width: 640px) {
  .search-wrapper {
    max-width: 100%;
    width: 100%;
  }
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted-foreground);
  pointer-events: none;
}

.search-input {
  height: 2.375rem;
  width: 100%;
  border-radius: var(--radius);
  border: 1px solid var(--input);
  background: var(--background);
  padding: var(--spacing-xs) var(--spacing-sm) var(--spacing-xs)
    calc(var(--spacing-xl) + var(--spacing-xs));
  font-size: var(--text-sm);
  box-shadow: var(--shadow-sm);
  transition: color var(--transition-base), box-shadow var(--transition-base);
  outline: none;
  color: var(--foreground);
}

.search-input::placeholder {
  color: var(--muted-foreground);
}

.search-input:focus-visible {
  border-color: var(--ring);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--ring), transparent 50%);
}

.sort-icon {
  color: var(--muted-foreground);
  flex-shrink: 0;
}

.sort-icon-active {
  color: var(--primary);
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding: 1rem;
  padding-bottom: 1rem;
  background-color: transparent;
}

.btn-pagination {
  width: calc(var(--spacing-xl) + var(--spacing-xs));
  height: calc(var(--spacing-xl) + var(--spacing-xs));
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all var(--transition-base);
  color: var(--muted-foreground);
  padding: 0;
  font-size: var(--text-xs);
}

.btn-pagination svg {
  width: 20px;
  height: 20px;
}

.btn-pagination:hover:not(:disabled) {
  color: var(--primary);
  border-color: var(--border);
}

.btn-pagination:disabled {
  cursor: not-allowed;
  opacity: 0.4;
  border-color: var(--border);
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: var(--spacing-xl);
  height: var(--spacing-xl);
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

.action-btn svg {
  pointer-events: none;
}

.action-btn.delete-btn:hover {
  color: var(--destructive);
  background-color: color-mix(in srgb, var(--destructive), transparent 90%);
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  margin-bottom: var(--spacing-xs);
}

.form-control {
  background: color-mix(in srgb, var(--background), transparent 50%);
  border: 1px solid var(--border);
  color: var(--foreground);
  padding: var(--spacing-sm) var(--spacing-sm);
  height: auto;
  font-size: var(--text-sm);
  border-radius: var(--radius);
  transition: all var(--transition-base);
  width: 100%;
}

.form-control::placeholder {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
}

.form-control:focus {
  background: var(--background);
  border-color: var(--primary);
  outline: none;
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary), transparent 80%);
}

textarea.form-control {
  min-height: calc(var(--spacing-xl) * 2.5);
  resize: vertical;
}

.modal-content-padding {
  padding: 0 var(--spacing-lg) var(--spacing-lg) var(--spacing-lg);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
}

.header-row {
  margin-bottom: var(--spacing-sm);
}

.table-wrapper {
  margin-top: var(--spacing-md);
}

.table-wrapper-scroll {
  overflow-x: auto;
}

.product-image-preview {
  width: 40px;
  height: 40px;
  border-radius: var(--radius);
  overflow: hidden;
  background-color: var(--secondary);
  border: 1px solid var(--border);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.news-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.placeholder-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--secondary);
}

.text-wrap {
  white-space: normal;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

@media (max-width: 1023px) {
  .header-row {
    margin-bottom: var(--spacing-sm);
  }
}

@media (max-width: 640px) {
  .header-row {
    margin-bottom: var(--spacing-sm);
  }

  .table-wrapper {
    margin-top: var(--spacing-md);
  }

  .grid.grid-cols-2 {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }

  .modal-actions .btn {
    width: 100%;
  }
}
</style>
