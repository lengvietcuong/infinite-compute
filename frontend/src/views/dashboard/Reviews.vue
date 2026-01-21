<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { useAuth } from "../../composables/useAuth";
import { useToast } from "../../composables/useToast";
import { useUrlPagination } from "../../composables/useUrlState";
import { API_BASE_URL } from "../../config/api";
import Table from "../../components/ui/table/Table.vue";
import TableHeader from "../../components/ui/table/TableHeader.vue";
import TableRow from "../../components/ui/table/TableRow.vue";
import TableHead from "../../components/ui/table/TableHead.vue";
import TableBody from "../../components/ui/table/TableBody.vue";
import TableCell from "../../components/ui/table/TableCell.vue";
import Modal from "../../components/ui/Modal.vue";
import Skeleton from "../../components/Skeleton.vue";

const { token } = useAuth();
const { showToast } = useToast();
const reviews = ref([]);
const isLoading = ref(false);
const reviewToDelete = ref(null);
const isDeleteModalOpen = ref(false);

const { currentPage, pageSize, searchQuery, sortColumn, sortDirection } = useUrlPagination(10);

const fetchReviews = async () => {
  isLoading.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/reviews`, {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    if (response.ok) {
      reviews.value = await response.json();
    }
  } catch (error) {
    console.error("Failed to fetch reviews:", error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchReviews);

const filteredReviews = computed(() => {
  let result = [...reviews.value];

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(
      (review) =>
        (review.user_name && review.user_name.toLowerCase().includes(query)) ||
        (review.product_name &&
          review.product_name.toLowerCase().includes(query)) ||
        (review.comment && review.comment.toLowerCase().includes(query))
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
    result.sort((a, b) => b.id - a.id);
  }

  return result;
});

const totalPages = computed(
  () => Math.ceil(filteredReviews.value.length / pageSize.value) || 1
);

const paginatedReviews = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredReviews.value.slice(start, start + pageSize.value);
});

watch(filteredReviews, () => {
  if (currentPage.value > totalPages.value) {
    currentPage.value = 1;
  }
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

const openDeleteModal = (review) => {
  reviewToDelete.value = review;
  isDeleteModalOpen.value = true;
};

const closeDeleteModal = () => {
  isDeleteModalOpen.value = false;
  reviewToDelete.value = null;
};

const deleteReview = async () => {
  if (!reviewToDelete.value) return;

  try {
    const response = await fetch(
      `${API_BASE_URL}/reviews/${reviewToDelete.value.id}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      }
    );

    if (response.ok) {
      reviews.value = reviews.value.filter(
        (r) => r.id !== reviewToDelete.value.id
      );
      closeDeleteModal();
      showToast("Review deleted successfully", "success");
    } else {
      showToast("Failed to delete review", "error");
    }
  } catch (error) {
    console.error("Error deleting review:", error);
  }
};
</script>

<template>
  <div>
    <div class="flex items-center justify-between gap-3 header-row flex-wrap">
      <div class="flex items-center gap-3 md:gap-4 flex-1 min-w-0">
        <h2 class="text-2xl font-bold tracking-tight">Reviews</h2>
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
            placeholder="Search reviews..."
            class="search-input"
          />
        </div>
      </div>
    </div>

    <div
      class="border bg-card text-card-foreground shadow-sm border-color table-wrapper"
      role="region"
      aria-label="Reviews table"
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead
              @click="handleSort('user_name')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                User
                <svg
                  v-if="sortColumn !== 'user_name'"
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
              @click="handleSort('product_name')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Product
                <svg
                  v-if="sortColumn !== 'product_name'"
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
              @click="handleSort('rating')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Rating
                <svg
                  v-if="sortColumn !== 'rating'"
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
              @click="handleSort('comment')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Comment
                <svg
                  v-if="sortColumn !== 'comment'"
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
          <TableRow v-if="isLoading" v-for="n in 5" :key="'skeleton-' + n">
            <TableCell
              ><Skeleton class="h-4 w-24" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-36" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-20" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-48" :rounded="false"
            /></TableCell>
            <TableCell class="text-right"
              ><Skeleton class="h-8 w-8 ml-auto" :rounded="false"
            /></TableCell>
          </TableRow>
          <TableRow
            v-for="review in paginatedReviews"
            :key="review.id"
            v-if="!isLoading"
          >
            <TableCell class="font-medium">{{
              review.user_name || "User " + review.user_id
            }}</TableCell>
            <TableCell>{{
              review.product_name || "Product #" + review.product_id
            }}</TableCell>
            <TableCell>
              <div class="flex items-center gap-0.5">
                <svg
                  v-for="i in 5"
                  :key="i"
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  :fill="i <= review.rating ? 'currentColor' : 'var(--muted)'"
                  :class="i <= review.rating ? 'text-warning' : 'text-muted'"
                  stroke="none"
                >
                  <polygon
                    points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
                  />
                </svg>
              </div>
            </TableCell>
            <TableCell class="max-w-xs truncate">{{
              review.comment
            }}</TableCell>
            <TableCell class="text-right">
              <div class="flex justify-end gap-2">
                <button
                  @click="openDeleteModal(review)"
                  class="action-btn delete-btn"
                  title="Delete"
                  aria-label="Delete review"
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
                    aria-hidden="true"
                  >
                    <path d="M3 6h18"></path>
                    <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                    <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                  </svg>
                </button>
              </div>
            </TableCell>
          </TableRow>
          <TableRow v-if="reviews.length === 0 && !isLoading">
            <TableCell
              colspan="5"
              class="text-center h-24 text-muted-foreground"
            >
              No reviews found.
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination-wrapper">
      <button
        @click="goToFirstPage"
        :disabled="currentPage === 1"
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
          <path d="m11 17-5-5 5-5" />
          <path d="m18 17-5-5 5-5" />
        </svg>
      </button>
      <button
        @click="prevPage"
        :disabled="currentPage === 1"
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
      :isOpen="isDeleteModalOpen"
      title="Delete Review"
      @close="closeDeleteModal"
    >
      <div class="modal-content-padding">
        <p>
          Are you sure you want to delete this review? This action cannot be
          undone.
        </p>
        <div class="modal-actions">
          <button @click="closeDeleteModal" class="btn btn-outline">
            Cancel
          </button>
          <button @click="deleteReview" class="btn btn-destructive">
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

.action-btn.delete-btn:hover {
  color: var(--destructive);
  background-color: color-mix(in srgb, var(--destructive), transparent 90%);
}

.action-btn svg {
  pointer-events: none;
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

  .flex.items-center.justify-between {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .flex.items-center.gap-4 {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
    gap: 0.75rem;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }

  .modal-actions .btn {
    width: 100%;
  }
}
</style>
