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
const coupons = ref([]);
const isLoading = ref(false);
const isModalOpen = ref(false);
const isEditing = ref(false);
const couponToDelete = ref(null);
const isDeleteModalOpen = ref(false);

const { currentPage, pageSize, searchQuery, sortColumn, sortDirection } = useUrlPagination(10);

const formData = ref({
  code: "",
  discount_percent: 10,
});

const fetchCoupons = async () => {
  isLoading.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/coupons`, {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    if (response.ok) {
      coupons.value = await response.json();
    }
  } catch (error) {
    console.error("Failed to fetch coupons:", error);
  } finally {
    isLoading.value = false;
  }
};

const fetchStats = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/coupons/stats`, {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    if (response.ok) {
      await response.json();
    }
  } catch (error) {
    console.error("Failed to fetch coupon stats:", error);
  }
};

onMounted(() => {
  fetchCoupons();
  fetchStats();
});

const filteredCoupons = computed(() => {
  let result = [...coupons.value];

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter((coupon) =>
      coupon.code.toLowerCase().includes(query)
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
  () => Math.ceil(filteredCoupons.value.length / pageSize.value) || 1
);

const paginatedCoupons = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredCoupons.value.slice(start, start + pageSize.value);
});

watch(filteredCoupons, () => {
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

const openCreate = () => {
  isEditing.value = false;
  formData.value = {
    code: "",
    discount_percent: 10,
  };
  isModalOpen.value = true;
};

const openEdit = (coupon) => {
  isEditing.value = true;
  formData.value = {
    id: coupon.id,
    code: coupon.code,
    discount_percent: parseFloat(coupon.discount_percent),
  };
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const saveCoupon = async () => {
  try {
    const url = isEditing.value
      ? `${API_BASE_URL}/coupons/${formData.value.id}`
      : `${API_BASE_URL}/coupons`;

    const method = isEditing.value ? "PUT" : "POST";

    const payload = {
      code: formData.value.code,
      discount_percent: parseFloat(formData.value.discount_percent),
    };

    const response = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token.value}`,
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      await fetchCoupons();
      closeModal();
      showToast(
        isEditing.value
          ? "Coupon updated successfully"
          : "Coupon created successfully",
        "success"
      );
    } else {
      const data = await response.json();
      showToast(
        data.detail ||
          (isEditing.value
            ? "Failed to update coupon"
            : "Failed to create coupon"),
        "error"
      );
    }
  } catch (error) {
    console.error("Error saving coupon:", error);
    showToast("An error occurred", "error");
  }
};

const openDeleteModal = (coupon) => {
  couponToDelete.value = coupon;
  isDeleteModalOpen.value = true;
};

const closeDeleteModal = () => {
  isDeleteModalOpen.value = false;
  couponToDelete.value = null;
};

const deleteCoupon = async () => {
  if (!couponToDelete.value) return;

  try {
    const response = await fetch(
      `${API_BASE_URL}/coupons/${couponToDelete.value.id}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      }
    );

    if (response.ok) {
      await fetchCoupons();
      closeDeleteModal();
      showToast("Coupon deleted successfully", "success");
    } else {
      showToast("Failed to delete coupon", "error");
    }
  } catch (error) {
    console.error("Error deleting coupon:", error);
    showToast("An error occurred", "error");
  }
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};
</script>

<template>
  <div>
    <div class="flex items-center justify-between gap-3 header-row flex-wrap">
      <div class="flex items-center gap-3 md:gap-4 flex-1 min-w-0">
        <h2 class="text-2xl font-bold tracking-tight">Coupons</h2>
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
            placeholder="Search coupons..."
            class="search-input"
          />
        </div>
      </div>
      <button
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
        <span class="d-none d-sm-inline">Add Coupon</span>
        <span class="d-sm-none">Add</span>
      </button>
    </div>

    <div
      class="border bg-card text-card-foreground shadow-sm border-color table-wrapper table-wrapper-scroll"
      role="region"
      aria-label="Coupons table"
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead
              @click="handleSort('code')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Code
                <svg
                  v-if="sortColumn !== 'code'"
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
              @click="handleSort('discount_percent')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Discount
                <svg
                  v-if="sortColumn !== 'discount_percent'"
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
            <TableHead class="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody v-if="isLoading">
          <TableRow v-for="i in pageSize" :key="i">
            <TableCell><Skeleton class="h-4 w-24" /></TableCell>
            <TableCell><Skeleton class="h-4 w-16" /></TableCell>
            <TableCell><Skeleton class="h-4 w-20" /></TableCell>
            <TableCell><Skeleton class="h-8 w-20 ml-auto" /></TableCell>
          </TableRow>
        </TableBody>
        <TableBody v-else-if="paginatedCoupons.length === 0">
          <TableRow>
            <TableCell colspan="4" class="text-center">
              No coupons found
            </TableCell>
          </TableRow>
        </TableBody>
        <TableBody v-else>
          <TableRow v-for="coupon in paginatedCoupons" :key="coupon.id">
            <TableCell class="font-medium">{{ coupon.code }}</TableCell>
            <TableCell>{{ coupon.discount_percent }}%</TableCell>
            <TableCell>{{ formatDate(coupon.created_at) }}</TableCell>
            <TableCell class="text-right">
              <div class="flex justify-end gap-2">
                <button
                  @click="openEdit(coupon)"
                  class="action-btn"
                  title="Edit"
                  aria-label="Edit coupon"
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
                      d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"
                    />
                  </svg>
                </button>
                <button
                  @click="openDeleteModal(coupon)"
                  class="action-btn delete-btn"
                  title="Delete"
                  aria-label="Delete coupon"
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

    <Modal
      :isOpen="isModalOpen"
      :title="isEditing ? 'Edit Coupon' : 'Add Coupon'"
      @close="closeModal"
    >
      <div class="modal-content-padding">
        <div class="space-y-4 max-h-[70vh] overflow-y-auto">
          <div>
            <label class="form-label">Code *</label>
            <input
              v-model="formData.code"
              type="text"
              class="form-control"
              placeholder="e.g., SUMMER2026"
            />
          </div>
          <div>
            <label class="form-label">Discount Percent *</label>
            <input
              v-model.number="formData.discount_percent"
              type="number"
              min="0"
              max="100"
              step="0.01"
              class="form-control"
            />
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeModal" class="btn btn-outline">Cancel</button>
          <button @click="saveCoupon" class="btn btn-primary">
            {{ isEditing ? "Update" : "Create" }}
          </button>
        </div>
      </div>
    </Modal>

    <Modal
      :isOpen="isDeleteModalOpen"
      title="Delete Coupon"
      @close="closeDeleteModal"
    >
      <div class="modal-content-padding">
        <p>
          Are you sure you want to delete the coupon
          <strong>{{ couponToDelete?.code }}</strong
          >? This action cannot be undone.
        </p>
        <div class="modal-actions">
          <button @click="closeDeleteModal" class="btn btn-outline">
            Cancel
          </button>
          <button @click="deleteCoupon" class="btn btn-destructive">
            Delete
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<style scoped>
.header-row {
  margin-bottom: var(--spacing-sm);
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

.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.625rem;
  font-size: var(--text-xs);
  font-weight: 500;
  border-radius: var(--radius);
  white-space: nowrap;
}

.badge-success {
  background-color: color-mix(in srgb, var(--success), transparent 85%);
  color: var(--success);
}

.badge-secondary {
  background-color: var(--secondary);
  color: var(--secondary-foreground);
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

.space-y-4 > * + * {
  margin-top: var(--spacing-md);
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

.modal-content-padding {
  padding: 0 0 var(--spacing-lg) 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
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
  .search-wrapper {
    max-width: none;
  }

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
