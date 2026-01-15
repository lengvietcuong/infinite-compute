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
import Select from "../../components/ui/select/Select.vue";
import Skeleton from "../../components/Skeleton.vue";
import { formatPrice } from "../../utils/format";

const { token, user } = useAuth();
const { showToast } = useToast();
const products = ref([]);
const isLoading = ref(false);
const isModalOpen = ref(false);
const isEditing = ref(false);
const productToDelete = ref(null);
const isDeleteModalOpen = ref(false);

// Search, Sort, Pagination
const searchQuery = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const sortColumn = ref("");
const sortDirection = ref("asc");

const formData = ref({
  name: "",
  price: 0,
  stock_quantity: 0,
  product_line: "",
  architecture: "",
  memory: "",
  memory_type: "",
  cuda_cores: null,
  tensor_cores: null,
  rt_cores: null,
  boost_clock: "",
  tdp: "",
  memory_bandwidth: "",
  description: "",
  image_url: "",
});

const canCreate = computed(() => user.value?.role === "admin");
const canDelete = computed(() => user.value?.role === "admin");

const fetchProducts = async () => {
  isLoading.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/products`, {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    if (response.ok) {
      products.value = await response.json();
    }
  } catch (error) {
    console.error("Failed to fetch products:", error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchProducts);

const filteredProducts = computed(() => {
  let result = [...products.value];

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(
      (product) =>
        (product.name && product.name.toLowerCase().includes(query)) ||
        (product.product_line &&
          product.product_line.toLowerCase().includes(query)) ||
        (product.architecture &&
          product.architecture.toLowerCase().includes(query))
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
    // Default sort by id (creation order proxy) or name
    result.sort((a, b) => b.id - a.id);
  }

  return result;
});

const totalPages = computed(
  () => Math.ceil(filteredProducts.value.length / pageSize.value) || 1
);

const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredProducts.value.slice(start, start + pageSize.value);
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
    name: "",
    price: 0,
    stock_quantity: 0,
    product_line: "Consumer Desktop",
    architecture: "",
    memory: "",
    memory_type: "",
    cuda_cores: null,
    tensor_cores: null,
    rt_cores: null,
    boost_clock: "",
    tdp: "",
    memory_bandwidth: "",
    description: "",
    image_url: "",
  };
  isModalOpen.value = true;
};

const openEdit = (product) => {
  isEditing.value = true;
  formData.value = {
    id: product.id,
    name: product.name || "",
    price: product.price || 0,
    stock_quantity: product.stock_quantity || 0,
    product_line: product.product_line || "",
    architecture: product.architecture || "",
    memory: product.memory || "",
    memory_type: product.memory_type || "",
    cuda_cores: product.cuda_cores ?? null,
    tensor_cores: product.tensor_cores ?? null,
    rt_cores: product.rt_cores ?? null,
    boost_clock: product.boost_clock || "",
    tdp: product.tdp || "",
    memory_bandwidth: product.memory_bandwidth || "",
    description: product.description || "",
    image_url: product.image_url || "",
  };
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const saveProduct = async () => {
  try {
    const url = isEditing.value
      ? `${API_BASE_URL}/products/${formData.value.id}`
      : `${API_BASE_URL}/products`;

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
      await fetchProducts();
      closeModal();
      showToast(
        isEditing.value
          ? "Product updated successfully"
          : "Product created successfully",
        "success"
      );
    } else {
      const data = await response.json();
      showToast(
        data.detail ||
          (isEditing.value
            ? "Failed to update product"
            : "Failed to create product"),
        "error"
      );
    }
  } catch (error) {
    console.error("Error saving product:", error);
  }
};

const openDeleteModal = (product) => {
  productToDelete.value = product;
  isDeleteModalOpen.value = true;
};

const closeDeleteModal = () => {
  isDeleteModalOpen.value = false;
  productToDelete.value = null;
};

const deleteProduct = async () => {
  if (!productToDelete.value) return;

  try {
    const response = await fetch(
      `${API_BASE_URL}/products/${productToDelete.value.id}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      }
    );

    if (response.ok) {
      products.value = products.value.filter(
        (p) => p.id !== productToDelete.value.id
      );
      closeDeleteModal();
      showToast("Product deleted successfully", "success");
    } else {
      showToast("Failed to delete product", "error");
    }
  } catch (error) {
    console.error("Error deleting product:", error);
  }
};
</script>

<template>
  <div>
    <div class="flex items-center justify-between gap-3 header-row flex-wrap">
      <div class="flex items-center gap-3 md:gap-4 flex-1 min-w-0">
        <h2 class="text-2xl font-bold tracking-tight">Products</h2>
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
            placeholder="Search products..."
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
        <span class="d-none d-sm-inline">Add Product</span>
        <span class="d-sm-none">Add</span>
      </button>
    </div>

    <div
      class="border bg-card text-card-foreground shadow-sm border-color table-wrapper table-wrapper-scroll"
      role="region"
      aria-label="Products table"
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Image</TableHead>
            <TableHead
              @click="handleSort('name')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Name
                <svg
                  v-if="sortColumn !== 'name'"
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
              @click="handleSort('price')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Price
                <svg
                  v-if="sortColumn !== 'price'"
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
              @click="handleSort('stock_quantity')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Stock
                <svg
                  v-if="sortColumn !== 'stock_quantity'"
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
              @click="handleSort('product_line')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Line
                <svg
                  v-if="sortColumn !== 'product_line'"
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
              @click="handleSort('architecture')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Architecture
                <svg
                  v-if="sortColumn !== 'architecture'"
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
            <TableHead>Memory</TableHead>
            <TableHead>CUDA Cores</TableHead>
            <TableHead class="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-if="isLoading" v-for="n in 5" :key="'skeleton-' + n">
            <TableCell
              ><Skeleton class="h-10 w-10" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-48" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-16" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-12" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-36" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-24" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-20" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-16" :rounded="false"
            /></TableCell>
            <TableCell class="text-right"
              ><div class="flex justify-end gap-2">
                <Skeleton class="h-8 w-8" :rounded="false" /><Skeleton
                  class="h-8 w-8"
                  :rounded="false"
                /></div
            ></TableCell>
          </TableRow>
          <TableRow
            v-for="product in paginatedProducts"
            :key="product.id"
            v-if="!isLoading"
          >
            <TableCell>
              <img
                :src="product.image_url || '/placeholder.png'"
                class="h-10 w-10 object-cover"
                :alt="product.name || 'Product image'"
              />
            </TableCell>
            <TableCell class="font-medium">{{ product.name }}</TableCell>
            <TableCell>${{ formatPrice(product.price) }}</TableCell>
            <TableCell>
              <span
                :class="{ 'text-destructive': product.stock_quantity === 0 }"
              >
                {{ product.stock_quantity }}
              </span>
            </TableCell>
            <TableCell>{{ product.product_line }}</TableCell>
            <TableCell>{{ product.architecture || "-" }}</TableCell>
            <TableCell>{{ product.memory || "-" }}</TableCell>
            <TableCell>{{ product.cuda_cores || "-" }}</TableCell>
            <TableCell class="text-right">
              <div class="flex justify-end gap-2">
                <button
                  @click="openEdit(product)"
                  class="action-btn"
                  title="Edit"
                  aria-label="Edit product"
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
                    <path
                      d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"
                    ></path>
                  </svg>
                </button>
                <button
                  v-if="canDelete"
                  @click="openDeleteModal(product)"
                  class="action-btn delete-btn"
                  title="Delete"
                  aria-label="Delete product"
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
          <TableRow v-if="products.length === 0 && !isLoading">
            <TableCell
              colspan="9"
              class="text-center h-24 text-muted-foreground"
            >
              No products found.
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
      :isOpen="isModalOpen"
      :title="isEditing ? 'Edit Product' : 'Add Product'"
      @close="closeModal"
    >
      <div class="modal-content-padding">
        <div class="space-y-4 max-h-[70vh] overflow-y-auto">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="form-label">Name *</label>
              <input v-model="formData.name" class="form-control" required />
            </div>
            <div>
              <label class="form-label">Product Line</label>
              <Select v-model="formData.product_line" class-name="border-color">
                <option value="">Select...</option>
                <option value="Consumer Desktop">Consumer Desktop</option>
                <option value="Consumer Laptop">Consumer Laptop</option>
                <option value="Data Center">Data Center</option>
                <option value="Professional Desktop">
                  Professional Desktop
                </option>
              </Select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="form-label">Price *</label>
              <input
                type="number"
                step="0.01"
                v-model.number="formData.price"
                class="form-control"
                required
              />
            </div>
            <div>
              <label class="form-label">Stock Quantity *</label>
              <input
                type="number"
                v-model.number="formData.stock_quantity"
                class="form-control"
                required
              />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="form-label">Architecture</label>
              <input
                v-model="formData.architecture"
                class="form-control"
                placeholder="e.g. Ada Lovelace"
              />
            </div>
            <div>
              <label class="form-label">Memory</label>
              <input
                v-model="formData.memory"
                class="form-control"
                placeholder="e.g. 24GB"
              />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="form-label">Memory Type</label>
              <input
                v-model="formData.memory_type"
                class="form-control"
                placeholder="e.g. GDDR6X"
              />
            </div>
            <div>
              <label class="form-label">Memory Bandwidth</label>
              <input
                v-model="formData.memory_bandwidth"
                class="form-control"
                placeholder="e.g. 936 GB/s"
              />
            </div>
          </div>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="form-label">CUDA Cores</label>
              <input
                type="number"
                v-model.number="formData.cuda_cores"
                class="form-control"
                placeholder="e.g. 18432"
              />
            </div>
            <div>
              <label class="form-label">Tensor Cores</label>
              <input
                type="number"
                v-model.number="formData.tensor_cores"
                class="form-control"
                placeholder="e.g. 576"
              />
            </div>
            <div>
              <label class="form-label">RT Cores</label>
              <input
                type="number"
                v-model.number="formData.rt_cores"
                class="form-control"
                placeholder="e.g. 144"
              />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="form-label">Boost Clock</label>
              <input
                v-model="formData.boost_clock"
                class="form-control"
                placeholder="e.g. 2.52 GHz"
              />
            </div>
            <div>
              <label class="form-label">TDP</label>
              <input
                v-model="formData.tdp"
                class="form-control"
                placeholder="e.g. 450W"
              />
            </div>
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
            <label class="form-label">Description</label>
            <textarea
              v-model="formData.description"
              rows="4"
              class="form-control"
              placeholder="Product description..."
            ></textarea>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeModal" class="btn btn-outline">Cancel</button>
          <button @click="saveProduct" class="btn btn-primary">
            Save Changes
          </button>
        </div>
      </div>
    </Modal>

    <Modal
      :isOpen="isDeleteModalOpen"
      title="Delete Product"
      @close="closeDeleteModal"
    >
      <div class="modal-content-padding">
        <p>
          Are you sure you want to delete
          <strong>{{ productToDelete?.name }}</strong
          >? This action cannot be undone.
        </p>
        <div class="modal-actions">
          <button @click="closeDeleteModal" class="btn btn-outline">
            Cancel
          </button>
          <button @click="deleteProduct" class="btn btn-destructive">
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
}

@media (max-width: 1023px) {
  .btn.btn-primary {
    height: 2.375rem;
  }
}

@media (max-width: 640px) {
  .table-wrapper {
    margin-top: 1rem;
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

  .grid.grid-cols-2 {
    grid-template-columns: 1fr;
  }

  .grid.grid-cols-3 {
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
