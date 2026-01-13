<script setup>
import { ref } from "vue";
import { formatPrice, formatDate } from "../utils/format";

const identifier = ref("");
const orders = ref([]);
const loading = ref(false);
const error = ref(null);
const searched = ref(false);

const trackOrder = async () => {
  if (!identifier.value) return;

  loading.value = true;
  error.value = null;
  orders.value = [];
  searched.value = true;

  try {
    const token = localStorage.getItem("token");
    const headers = {
      "Content-Type": "application/json",
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch("http://localhost:8000/orders/track", {
      method: "POST",
      headers: headers,
      body: JSON.stringify({ identifier: identifier.value }),
    });

    if (!response.ok) {
      if (response.status === 404) {
        error.value = null;
        searched.value = true;
        return;
      }
      throw new Error("Failed to track order. Please try again.");
    }

    orders.value = await response.json();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="tracking-page container">
    <div class="tracking-header text-center mb-2 fade-in-up-fast">
      <h1
        class="page-title mb-3 d-flex align-items-center justify-content-center gap-2"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="title-icon"
        >
          <path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2" />
          <circle cx="7" cy="18" r="2" />
          <path d="M15 18H9" />
          <path
            d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.63l-1.02-1.53a1 1 0 0 0-.84-.37H14"
          />
          <circle cx="17" cy="18" r="2" />
        </svg>
        Track Your Order
      </h1>
      <p class="text-muted">
        Enter your email or tracking number to check the status of your order.
      </p>
    </div>

    <div class="row justify-content-center fade-in-up-fast delay-100-fast">
      <div class="col-lg-6">
        <form
          @submit.prevent="trackOrder"
          class="d-flex gap-2 mb-5 align-items-center"
        >
          <input
            v-model="identifier"
            type="text"
            class="form-control form-control-lg rounded-0"
            placeholder="Email or Tracking Number (e.g. ORD-ABC123)"
            required
            aria-label="Email or Tracking Number"
          />
          <button
            type="submit"
            class="btn btn-primary btn-lg rounded-0"
            :disabled="loading"
          >
            Track
          </button>
        </form>
      </div>
    </div>

    <!-- Results -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border spinner-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="text-center py-5 error-message">
      {{ error }}
    </div>

    <div
      v-else-if="searched && orders.length === 0"
      class="text-center py-5 no-results-message"
    >
      No orders found. Please double check your input.
    </div>

    <div v-else class="orders-list fade-in-up">
      <div v-for="order in orders" :key="order.id" class="card glass-card mb-4">
        <div class="card-header bg-transparent border-bottom p-4">
          <div
            class="d-flex justify-content-between align-items-center flex-wrap gap-3"
          >
            <div>
              <span class="text-muted-foreground small d-block">Status</span>
              <span class="text-foreground fw-bold">{{ order.status }}</span>
            </div>
            <div>
              <span class="text-muted-foreground small d-block">Total</span>
              <span class="text-foreground fw-bold"
                >${{ formatPrice(order.total_amount) }}</span
              >
            </div>
            <div>
              <span class="text-muted-foreground small d-block">Placed On</span>
              <span class="text-foreground fw-bold">{{
                formatDate(order.created_at)
              }}</span>
            </div>
          </div>
        </div>
        <div class="card-body p-4">
          <div class="table-container">
            <table class="order-table">
              <thead>
                <tr class="table-header-row">
                  <th class="table-head">Product</th>
                  <th class="table-head text-center">Quantity</th>
                  <th class="table-head text-end">Price</th>
                  <th class="table-head text-end">Total</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in order.items"
                  :key="item.id"
                  class="table-row"
                >
                  <td class="table-cell text-foreground">
                    {{ item.product_name }}
                  </td>
                  <td class="table-cell text-center text-foreground">
                    {{ item.quantity }}
                  </td>
                  <td class="table-cell text-end text-foreground">
                    ${{ formatPrice(item.price_at_purchase) }}
                  </td>
                  <td class="table-cell text-end text-foreground">
                    ${{ formatPrice(item.price_at_purchase * item.quantity) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tracking-page {
  padding-top: var(--spacing-xl);
  padding-bottom: var(--spacing-2xl);
  min-height: 60vh;
}

.page-title {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: var(--text-5xl);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
}

.title-icon {
  width: 48px;
  height: 48px;
  color: var(--primary);
}

@media (max-width: 768px) {
  .page-title {
    font-size: var(--text-3xl);
  }

  .title-icon {
    width: 32px;
    height: 32px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: var(--text-2xl);
  }

  .title-icon {
    width: 28px;
    height: 28px;
  }
}

.form-control {
  background: color-mix(in srgb, var(--background), transparent 50%);
  border: 1px solid var(--border);
  color: var(--foreground);
  font-size: var(--text-sm);
  padding: var(--spacing-sm) var(--spacing-sm);
  line-height: 1.5;
  display: flex;
  align-items: center;
}

.form-control::placeholder {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
}

.form-control:focus {
  background: var(--background);
  border-color: var(--primary);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary), transparent 80%);
}

:deep(.btn-lg) {
  padding: var(--spacing-sm) var(--spacing-md);
  height: auto;
}

.spinner-primary {
  color: var(--primary);
}

.error-message {
  color: var(--foreground);
}

.no-results-message {
  color: var(--foreground);
}

/* Table Styles */
.table-container {
  position: relative;
  width: 100%;
  overflow-x: auto;
}

.order-table {
  width: 100%;
  font-size: var(--text-sm);
  border-collapse: collapse;
}

.table-header-row {
  border-bottom: 1px solid var(--border);
}

.table-head {
  color: var(--foreground);
  height: 2.5rem;
  padding: 0.5rem;
  text-align: left;
  font-weight: 500;
  white-space: nowrap;
}

.table-row {
  border-bottom: 1px solid var(--border);
  transition: background-color 0.2s;
}

.table-row:hover {
  background-color: color-mix(in srgb, var(--muted), transparent 50%);
}

.table-row:last-child {
  border-bottom: 1px solid var(--border);
}

.table-cell {
  padding: 0.5rem;
  vertical-align: middle;
  white-space: nowrap;
}

.text-center {
  text-align: center;
}

.text-end {
  text-align: right;
}

.text-foreground {
  color: var(--foreground);
}

.text-muted-foreground {
  color: var(--muted-foreground);
}

.card-header {
  border-color: var(--border) !important;
}

.orders-list {
  animation: fadeInUp 0.4s ease-out forwards;
}

.table-row:last-child {
  border-bottom: 0;
}
</style>
