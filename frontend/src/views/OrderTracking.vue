<script setup>
import { ref } from "vue";

const identifier = ref("");
const orders = ref([]);
const loading = ref(false);
const error = ref(null);
const searched = ref(false);

const formatPrice = (price) => {
  return parseFloat(price).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

const trackOrder = async () => {
  if (!identifier.value) return;

  loading.value = true;
  error.value = null;
  orders.value = [];
  searched.value = true;

  try {
    const response = await fetch("http://localhost:8000/orders/track", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ identifier: identifier.value }),
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error("No orders found with that information.");
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
      <h1 class="page-title mb-3">Track Your Order</h1>
      <p class="text-muted">
        Enter your email or order ID to check the status of your order.
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
            placeholder="Email or Order ID"
            required
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
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="text-center py-5 text-danger fade-in-up">
      {{ error }}
    </div>

    <div
      v-else-if="searched && orders.length === 0"
      class="text-center py-5 text-muted fade-in-up"
    >
      No orders found.
    </div>

    <div v-else class="orders-list fade-in-up">
      <div v-for="order in orders" :key="order.id" class="card glass-card mb-4">
        <div class="card-header bg-transparent border-bottom p-4">
          <div
            class="d-flex justify-content-between align-items-center flex-wrap gap-3"
          >
            <div>
              <span class="text-muted small d-block"
                >Order #{{ order.id }}</span
              >
              <span class="fw-bold" v-if="order.tracking_number">
                Tracking: {{ order.tracking_number }}
              </span>
            </div>
            <div>
              <span class="text-muted small d-block">Placed On</span>
              <span class="fw-bold">{{ formatDate(order.created_at) }}</span>
            </div>
            <div>
              <span class="text-muted small d-block">Total</span>
              <span class="fw-bold"
                >${{ formatPrice(order.total_amount) }}</span
              >
            </div>
            <div>
              <span
                class="badge rounded-pill"
                :class="{
                  'bg-success': order.status === 'DELIVERED',
                  'bg-info': order.status === 'SHIPPED',
                  'bg-primary': order.status === 'PAID',
                  'bg-secondary': order.status === 'PENDING',
                  'bg-danger': order.status === 'CANCELLED',
                }"
              >
                {{ order.status }}
              </span>
            </div>
          </div>
        </div>
        <div class="card-body p-4">
          <h5 class="mb-3">Items</h5>
          <div class="table-responsive">
            <table class="table table-borderless">
              <tbody>
                <tr v-for="item in order.items" :key="item.id">
                  <td>{{ item.product_name }}</td>
                  <td class="text-end">x{{ item.quantity }}</td>
                  <td class="text-end">
                    ${{ formatPrice(item.price_at_purchase) }}
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
  padding-top: 2rem;
  padding-bottom: 4rem;
  min-height: 60vh;
}

.page-title {
  font-family: var(--font-mono);
  font-weight: 700;
}

.form-control {
  background: color-mix(in srgb, var(--background), transparent 50%);
  border: 1px solid var(--border);
  color: var(--foreground);
  font-size: 0.9rem;
  padding: 0.625rem 0.75rem;
  line-height: 1.5;
  display: flex;
  align-items: center;
}

.form-control::placeholder {
  color: var(--muted-foreground);
  font-size: 0.9rem;
}

.form-control:focus {
  background: var(--background);
  border-color: var(--primary);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary), transparent 80%);
}

:deep(.btn-lg) {
  padding: 0.625rem 1rem;
  height: auto;
}
</style>
