<script setup>
import { ref, onMounted, computed } from "vue";
import { useAuth } from "../../composables/useAuth";
import { useToast } from "../../composables/useToast";
import Table from "../../components/ui/table/Table.vue";
import TableHeader from "../../components/ui/table/TableHeader.vue";
import TableRow from "../../components/ui/table/TableRow.vue";
import TableHead from "../../components/ui/table/TableHead.vue";
import TableBody from "../../components/ui/table/TableBody.vue";
import TableCell from "../../components/ui/table/TableCell.vue";
import Select from "../../components/ui/select/Select.vue";
import Modal from "../../components/ui/Modal.vue";
import Skeleton from "../../components/Skeleton.vue";
import { formatPrice } from "../../utils/format";

const { token, user } = useAuth();
const { showToast } = useToast();
const orders = ref([]);
const isLoading = ref(false);
const orderToDelete = ref(null);
const isDeleteModalOpen = ref(false);
const isEditModalOpen = ref(false);
const orderToEdit = ref(null);
const orderToView = ref(null);
const isViewModalOpen = ref(false);

const formData = ref({
  user_id: null,
  guest_email: "",
  status: "PAID",
  total_amount: "",
  shipping_address: "",
  tracking_number: "",
});

// Search, Sort, Pagination
const searchQuery = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const sortColumn = ref("");
const sortDirection = ref("asc");

const canDelete = computed(() => user.value?.role === "admin");

const fetchOrders = async () => {
  isLoading.value = true;
  try {
    const response = await fetch("/api/orders", {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    if (response.ok) {
      orders.value = await response.json();
    }
  } catch (error) {
    console.error("Failed to fetch orders:", error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchOrders);

const filteredOrders = computed(() => {
  let result = [...orders.value];

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(
      (order) =>
        (order.tracking_number &&
          order.tracking_number.toLowerCase().includes(query)) ||
        (order.customer_name &&
          order.customer_name.toLowerCase().includes(query)) ||
        (order.guest_email &&
          order.guest_email.toLowerCase().includes(query)) ||
        (order.status && order.status.toLowerCase().includes(query))
    );
  }

  if (sortColumn.value) {
    result.sort((a, b) => {
      let valA = a[sortColumn.value];
      let valB = b[sortColumn.value];

      // Handle specific fields if needed
      if (sortColumn.value === "customer") {
        valA = a.customer_name || a.guest_email || "";
        valB = b.customer_name || b.guest_email || "";
      }

      if (valA < valB) return sortDirection.value === "asc" ? -1 : 1;
      if (valA > valB) return sortDirection.value === "asc" ? 1 : -1;
      return 0;
    });
  } else {
    // Default sort by date desc
    result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  }

  return result;
});

const totalPages = computed(
  () => Math.ceil(filteredOrders.value.length / pageSize.value) || 1
);

const paginatedOrders = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredOrders.value.slice(start, start + pageSize.value);
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

const updateStatus = async (order, newStatus) => {
  if (order.status === newStatus) return;

  try {
    const response = await fetch(`/api/orders/${order.id}/status`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token.value}`,
      },
      body: JSON.stringify({ status: newStatus }),
    });

    if (response.ok) {
      const updatedOrder = await response.json();
      const index = orders.value.findIndex((o) => o.id === order.id);
      if (index !== -1) {
        orders.value[index] = updatedOrder;
      }
      showToast("Order status updated successfully", "success");
    } else {
      showToast("Failed to update order status", "error");
      await fetchOrders();
    }
  } catch (error) {
    console.error("Error updating order:", error);
  }
};

const openDeleteModal = (order) => {
  orderToDelete.value = order;
  isDeleteModalOpen.value = true;
};

const closeDeleteModal = () => {
  isDeleteModalOpen.value = false;
  orderToDelete.value = null;
};

const deleteOrder = async () => {
  if (!orderToDelete.value) return;

  try {
    const response = await fetch(`/api/orders/${orderToDelete.value.id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });

    if (response.ok) {
      orders.value = orders.value.filter(
        (o) => o.id !== orderToDelete.value.id
      );
      closeDeleteModal();
      showToast("Order deleted successfully", "success");
    } else {
      showToast("Failed to delete order", "error");
    }
  } catch (error) {
    console.error("Error deleting order:", error);
  }
};

const openEditModal = (order) => {
  orderToEdit.value = order;
  formData.value = {
    user_id: order.user_id || null,
    guest_email: order.guest_email || "",
    status: order.status,
    total_amount: order.total_amount?.toString() || "",
    shipping_address: order.shipping_address || "",
    tracking_number: order.tracking_number || "",
  };
  isEditModalOpen.value = true;
};

const closeEditModal = () => {
  isEditModalOpen.value = false;
  orderToEdit.value = null;
};

const openViewModal = (order) => {
  orderToView.value = order;
  isViewModalOpen.value = true;
};

const closeViewModal = () => {
  isViewModalOpen.value = false;
  orderToView.value = null;
};

const saveOrder = async () => {
  if (!orderToEdit.value) return;

  if (
    !formData.value.shipping_address ||
    !formData.value.shipping_address.trim()
  ) {
    showToast("Shipping address is required", "error");
    return;
  }

  if (
    formData.value.total_amount === "" ||
    isNaN(parseFloat(formData.value.total_amount)) ||
    parseFloat(formData.value.total_amount) < 0
  ) {
    showToast("Please enter a valid total amount", "error");
    return;
  }

  try {
    const updateData = {};

    if (formData.value.user_id !== orderToEdit.value.user_id) {
      updateData.user_id = formData.value.user_id || null;
    }

    if (formData.value.guest_email !== (orderToEdit.value.guest_email || "")) {
      updateData.guest_email = formData.value.guest_email?.trim() || null;
    }

    if (formData.value.status !== orderToEdit.value.status) {
      updateData.status = formData.value.status;
    }

    if (
      formData.value.total_amount !== orderToEdit.value.total_amount?.toString()
    ) {
      updateData.total_amount = parseFloat(formData.value.total_amount);
    }

    if (
      formData.value.shipping_address !== orderToEdit.value.shipping_address
    ) {
      updateData.shipping_address = formData.value.shipping_address.trim();
    }

    if (
      formData.value.tracking_number !==
      (orderToEdit.value.tracking_number || "")
    ) {
      updateData.tracking_number =
        formData.value.tracking_number?.trim() || null;
    }

    const response = await fetch(`/api/orders/${orderToEdit.value.id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token.value}`,
      },
      body: JSON.stringify(updateData),
    });

    if (response.ok) {
      const updatedOrder = await response.json();
      const index = orders.value.findIndex(
        (o) => o.id === orderToEdit.value.id
      );
      if (index !== -1) {
        orders.value[index] = updatedOrder;
      }
      closeEditModal();
      showToast("Order updated successfully", "success");
    } else {
      const errorData = await response
        .json()
        .catch(() => ({ detail: "Failed to update order" }));
      showToast(errorData.detail || "Failed to update order", "error");
    }
  } catch (error) {
    console.error("Error updating order:", error);
    alert("Failed to update order");
  }
};
</script>

<template>
  <div>
    <div class="flex items-center justify-between gap-3 header-row flex-wrap">
      <div class="flex items-center gap-3 md:gap-4 flex-1 min-w-0">
        <h2 class="text-2xl font-bold tracking-tight">Orders</h2>
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
            placeholder="Search orders..."
            class="search-input"
          />
        </div>
      </div>
    </div>

    <div
      class="border bg-card text-card-foreground shadow-sm border-color table-wrapper"
      role="region"
      aria-label="Orders table"
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead
              @click="handleSort('tracking_number')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Tracking Number
                <svg
                  v-if="sortColumn !== 'tracking_number'"
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
              @click="handleSort('created_at')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Date
                <svg
                  v-if="sortColumn !== 'created_at'"
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
              @click="handleSort('customer')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Customer
                <svg
                  v-if="sortColumn !== 'customer'"
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
              @click="handleSort('total_amount')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Total
                <svg
                  v-if="sortColumn !== 'total_amount'"
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
              @click="handleSort('status')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Status
                <svg
                  v-if="sortColumn !== 'status'"
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
              ><Skeleton class="h-4 w-28" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-24" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-32" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-16" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-8 w-40" :rounded="false"
            /></TableCell>
            <TableCell class="text-right"
              ><Skeleton class="h-8 w-8 ml-auto" :rounded="false"
            /></TableCell>
          </TableRow>
          <TableRow
            v-for="order in paginatedOrders"
            :key="order.id"
            v-if="!isLoading"
          >
            <TableCell class="font-medium">{{
              order.tracking_number || order.id
            }}</TableCell>
            <TableCell>{{
              new Date(order.created_at).toLocaleDateString()
            }}</TableCell>
            <TableCell>
              {{ order.customer_name || order.guest_email || "Guest" }}
            </TableCell>
            <TableCell>${{ formatPrice(order.total_amount) }}</TableCell>
            <TableCell>
              <Select
                :modelValue="order.status"
                @update:modelValue="(val) => updateStatus(order, val)"
                class-name="h-8 w-[160px] border-color bg-background text-foreground"
              >
                <option value="PAID">PAID</option>
                <option value="SHIPPED">SHIPPED</option>
                <option value="DELIVERED">DELIVERED</option>
                <option value="CANCELLED">CANCELLED</option>
              </Select>
            </TableCell>
            <TableCell class="text-right">
              <div class="flex justify-end gap-2">
                <button
                  @click="openViewModal(order)"
                  class="action-btn"
                  title="View Details"
                  aria-label="View order details"
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
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                </button>
                <button
                  @click="openEditModal(order)"
                  class="action-btn"
                  title="Edit"
                  aria-label="Edit order"
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
                  @click="openDeleteModal(order)"
                  class="action-btn delete-btn"
                  title="Delete"
                  aria-label="Delete order"
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
          <TableRow v-if="orders.length === 0 && !isLoading">
            <TableCell
              colspan="6"
              class="text-center h-24 text-muted-foreground"
            >
              No orders found.
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

    <Modal :isOpen="isEditModalOpen" title="Edit Order" @close="closeEditModal">
      <div class="modal-content-padding">
        <div class="space-y-4 max-h-[70vh] overflow-y-auto">
          <div>
            <label class="form-label">User ID</label>
            <input
              v-model.number="formData.user_id"
              type="number"
              class="form-control"
              placeholder="Leave empty for guest orders"
            />
          </div>
          <div>
            <label class="form-label">Guest Email</label>
            <input
              v-model="formData.guest_email"
              type="email"
              class="form-control"
              placeholder="Leave empty for registered user orders"
            />
          </div>
          <div>
            <label class="form-label">Tracking Number</label>
            <input v-model="formData.tracking_number" class="form-control" />
          </div>
          <div>
            <label class="form-label">Total Amount</label>
            <input
              v-model.number="formData.total_amount"
              type="number"
              step="0.01"
              min="0"
              class="form-control"
            />
          </div>
          <div>
            <label class="form-label">Shipping Address</label>
            <textarea
              v-model="formData.shipping_address"
              rows="3"
              class="form-control"
            ></textarea>
          </div>
          <div>
            <label class="form-label">Status</label>
            <Select
              v-model="formData.status"
              class-name="h-10 w-full border-color bg-background text-foreground"
            >
              <option value="PAID">PAID</option>
              <option value="SHIPPED">SHIPPED</option>
              <option value="DELIVERED">DELIVERED</option>
              <option value="CANCELLED">CANCELLED</option>
            </Select>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeEditModal" class="btn btn-outline">
            Cancel
          </button>
          <button @click="saveOrder" class="btn btn-primary">
            Save Changes
          </button>
        </div>
      </div>
    </Modal>

    <Modal
      :isOpen="isDeleteModalOpen"
      title="Delete Order"
      @close="closeDeleteModal"
    >
      <div class="modal-content-padding">
        <p>
          Are you sure you want to delete this order? This action cannot be
          undone.
        </p>
        <div class="modal-actions">
          <button @click="closeDeleteModal" class="btn btn-outline">
            Cancel
          </button>
          <button @click="deleteOrder" class="btn btn-destructive">
            Delete
          </button>
        </div>
      </div>
    </Modal>

    <Modal
      :isOpen="isViewModalOpen"
      title="Order Details"
      @close="closeViewModal"
    >
      <div class="modal-content-padding">
        <div v-if="orderToView" class="max-h-[70vh] overflow-y-auto">
          <div>
            <h4 class="text-sm font-semibold mb-2 text-muted-foreground uppercase tracking-wide">Order Items</h4>
            <div class="border border-color rounded-lg overflow-hidden">
              <table class="w-full">
                <thead class="bg-muted/50">
                  <tr>
                    <th class="text-left p-3 text-sm font-medium">Product</th>
                    <th class="text-right p-3 text-sm font-medium">Quantity</th>
                    <th class="text-right p-3 text-sm font-medium">Price</th>
                    <th class="text-right p-3 text-sm font-medium">Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="item in orderToView.items || []"
                    :key="item.id"
                    class="border-t border-color"
                  >
                    <td class="p-3 text-sm">
                      {{ item.product_name || `Product #${item.product_id || 'N/A'}` }}
                    </td>
                    <td class="p-3 text-sm text-right">{{ item.quantity }}</td>
                    <td class="p-3 text-sm text-right">${{ formatPrice(item.price_at_purchase) }}</td>
                    <td class="p-3 text-sm text-right font-medium">
                      ${{ formatPrice(item.price_at_purchase * item.quantity) }}
                    </td>
                  </tr>
                  <tr v-if="!orderToView.items || orderToView.items.length === 0">
                    <td colspan="4" class="p-3 text-sm text-center text-muted-foreground">
                      No items found
                    </td>
                  </tr>
                </tbody>
                <tfoot class="bg-muted/50 border-t-2 border-color">
                  <tr>
                    <td colspan="3" class="p-3 text-sm font-semibold text-right">Total:</td>
                    <td class="p-3 text-sm font-semibold text-right">
                      ${{ formatPrice(orderToView.total_amount) }}
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <div class="shipping-address-section">
            <h4 class="text-sm font-semibold mb-2 text-muted-foreground uppercase tracking-wide">Shipping Address</h4>
            <div class="border border-color rounded-lg p-4 bg-muted/50">
              <pre class="text-sm whitespace-pre-wrap font-mono">{{ orderToView.shipping_address || 'No shipping address provided' }}</pre>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeViewModal" class="btn btn-outline">
            Close
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

.form-control:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.shipping-address-section {
  margin-top: var(--spacing-xl);
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
