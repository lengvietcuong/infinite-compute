<script setup>
import { ref } from "vue";
import { useCart } from "../composables/useCart";
import { useRouter } from "vue-router";
import { formatPrice } from "../utils/format";

const { cart, cartTotal, clearCart } = useCart();
const router = useRouter();

const form = ref({
  email: "",
  name: "",
  address: "",
  city: "",
  zip: "",
  discountCode: "",
  cardNumber: "",
  expiry: "",
  cvc: "",
});

const isProcessing = ref(false);
const showModal = ref(false);
const orderId = ref(null);

const formatExpiry = (e) => {
  let value = e.target.value.replace(/\D/g, "");
  const isDeleting =
    e.inputType === "deleteContentBackward" ||
    e.inputType === "deleteContentForward" ||
    e.inputType === "deleteByCut";

  if (
    isDeleting &&
    form.value.expiry.endsWith("/") &&
    value.length === form.value.expiry.replace(/\D/g, "").length
  ) {
    value = value.slice(0, -1);
  }

  if (value.length >= 2) {
    value = value.slice(0, 2) + "/" + value.slice(2, 4);
  }

  e.target.value = value;
  form.value.expiry = value;
};

const placeOrder = async () => {
  isProcessing.value = true;

  await new Promise((resolve) => setTimeout(resolve, 2000));

  isProcessing.value = false;
  showModal.value = true;
  orderId.value = "ORD-" + Math.floor(Math.random() * 1000000);
  clearCart();
};

const handleOverlayClick = () => {
  router.push("/");
};
</script>

<template>
  <div class="checkout-page container">
    <h1
      class="page-title mb-5 fade-in-up d-flex align-items-center justify-content-center gap-3"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="40"
        height="40"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="checkout-icon"
      >
        <path
          d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"
        />
        <line x1="7" y1="7" x2="7.01" y2="7" />
      </svg>
      Checkout
    </h1>

    <!-- Modal will be added at bottom -->

    <div class="row g-5 fade-in-up delay-100">
      <!-- Order Summary -->
      <div class="col-lg-5 order-lg-2">
        <div class="card glass-card p-4">
          <h3 class="h5 mb-4 summary-title">Order Summary</h3>
          <div class="checkout-items mb-4">
            <div
              v-for="item in cart"
              :key="item.id"
              class="d-flex justify-content-between mb-3"
            >
              <div>
                <h6 class="my-0 product-name">{{ item.name }}</h6>
                <small class="text-muted">Qty: {{ item.quantity }}</small>
              </div>
              <span class="text-muted"
                >${{ formatPrice(item.price * item.quantity) }}</span
              >
            </div>
          </div>
          <div class="border-top summary-border pt-3">
            <div class="d-flex justify-content-between mb-2">
              <span class="summary-label">Subtotal</span>
              <span class="summary-value">${{ formatPrice(cartTotal) }}</span>
            </div>
            <div class="d-flex justify-content-between mb-2">
              <span class="summary-label">Shipping</span>
              <span class="summary-value">Free</span>
            </div>
            <div
              class="d-flex justify-content-between fw-bold mt-3 fs-5 total-row"
            >
              <span>Total</span>
              <span>${{ formatPrice(cartTotal) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Checkout Form -->
      <div class="col-lg-7 order-lg-1">
        <form @submit.prevent="placeOrder">
          <h4 class="mb-3 section-heading">
            <img
              src="/icons/address.svg"
              alt=""
              width="24"
              height="24"
              class="section-icon"
            />
            Shipping Address
          </h4>
          <div class="row g-3">
            <div class="col-sm-6">
              <label class="form-label">Full Name</label>
              <input
                v-model="form.name"
                type="text"
                class="form-control"
                placeholder="John Doe"
                required
              />
            </div>
            <div class="col-sm-6">
              <label class="form-label">Email</label>
              <input
                v-model="form.email"
                type="email"
                class="form-control"
                placeholder="john@example.com"
                required
              />
            </div>
            <div class="col-12">
              <label class="form-label">Address</label>
              <input
                v-model="form.address"
                type="text"
                class="form-control"
                placeholder="123 Main Street"
                required
              />
            </div>
            <div class="col-md-6">
              <label class="form-label">City</label>
              <input
                v-model="form.city"
                type="text"
                class="form-control"
                placeholder="New York"
                required
              />
            </div>
            <div class="col-md-6">
              <label class="form-label">Zip Code</label>
              <input
                v-model="form.zip"
                type="text"
                class="form-control"
                placeholder="10001"
                required
              />
            </div>
          </div>

          <h4 class="mb-3 section-heading">
            <img
              src="/icons/discount.svg"
              alt=""
              width="24"
              height="24"
              class="section-icon"
            />
            Discount Code
          </h4>
          <div class="row g-3">
            <div class="col-12">
              <div class="d-flex gap-2">
                <input
                  v-model="form.discountCode"
                  type="text"
                  class="form-control"
                  placeholder="Enter discount code"
                />
                <button type="button" class="btn btn-outline">Apply</button>
              </div>
            </div>
          </div>

          <h4 class="mb-3 section-heading">
            <img
              src="/icons/credit-card.svg"
              alt=""
              width="24"
              height="24"
              class="section-icon"
            />
            Payment
          </h4>
          <div class="row g-3">
            <div class="col-12">
              <label class="form-label">Card Number</label>
              <input
                v-model="form.cardNumber"
                type="text"
                class="form-control"
                placeholder="0000 0000 0000 0000"
                required
              />
            </div>
            <div class="col-md-6">
              <label class="form-label">Expiration</label>
              <input
                :value="form.expiry"
                @input="formatExpiry"
                type="text"
                class="form-control"
                placeholder="MM/YY"
                maxlength="5"
                required
              />
            </div>
            <div class="col-md-6">
              <label class="form-label">CVC</label>
              <input
                v-model="form.cvc"
                type="text"
                class="form-control"
                placeholder="123"
                required
              />
            </div>
          </div>

          <button
            class="btn btn-primary btn-lg w-100 checkout-submit-btn mt-4"
            type="submit"
            :disabled="isProcessing || cart.length === 0"
          >
            <span
              v-if="isProcessing"
              class="spinner-border spinner-border-sm me-1"
              role="status"
              aria-hidden="true"
            ></span>
            {{ isProcessing ? "Processing..." : "Place Order" }}
          </button>
        </form>
      </div>
    </div>

    <!-- Success Modal -->
    <div v-if="showModal" class="modal-overlay" @click="handleOverlayClick">
      <div
        class="modal-content glass-card p-5 text-center fade-in-up"
        @click.stop
      >
        <div class="success-icon mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="64"
            height="64"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="text-primary"
          >
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        </div>
        <h2 class="h3 mb-3">Order Placed Successfully!</h2>
        <p class="text-muted mb-2">Thank you for your purchase.</p>
        <p class="text-muted mb-4">
          Your order ID is <strong>{{ orderId }}</strong
          >.
        </p>
        <router-link
          to="/"
          class="btn btn-primary d-inline-flex align-items-center gap-2"
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
            class="home-icon"
          >
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
          Back to Home
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.checkout-page {
  padding-top: var(--spacing-xl);
  padding-bottom: var(--spacing-2xl);
}

.page-title {
  font-family: var(--font-mono);
  font-weight: 700;
  text-align: center;
}

@media (max-width: 576px) {
  .page-title {
    font-size: var(--text-3xl);
    margin-bottom: var(--spacing-xl) !important;
  }

  .page-title svg {
    width: 32px !important;
    height: 32px !important;
  }

  .col-lg-5 {
    margin-bottom: var(--spacing-md);
  }
}

@media (max-width: 768px) {
  .page-title {
    font-size: var(--text-3xl);
    margin-bottom: 2.5rem !important;
  }

  .page-title svg {
    width: 36px !important;
    height: 36px !important;
  }

  .col-lg-5 {
    margin-bottom: var(--spacing-lg);
  }

  .col-lg-7 {
    margin-top: var(--spacing-md);
  }
}

.form-label {
  margin-bottom: var(--spacing-xs);
}

.form-control {
  background: color-mix(in srgb, var(--background), transparent 50%);
  border: 1px solid var(--border);
  color: var(--foreground);
  padding: var(--spacing-sm) var(--spacing-sm);
  height: auto;
}

.form-control::placeholder {
  color: var(--muted-foreground);
  font-size: 0.875rem;
}

.form-control:focus {
  background: var(--background);
  border-color: var(--primary);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary), transparent 80%);
}

.text-success {
  color: var(--success);
}

.summary-title,
.summary-label,
.product-name {
  color: var(--foreground);
}

.checkout-icon {
  color: var(--primary);
}

.total-row {
  color: var(--primary);
}

.summary-value {
  color: var(--foreground);
}

.section-heading {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-xl);
  margin-bottom: var(--spacing-md);
}

.section-heading:first-of-type {
  margin-top: 0;
}

.section-icon {
  filter: brightness(0) saturate(100%) invert(77%) sepia(45%) saturate(826%)
    hue-rotate(358deg) brightness(103%) contrast(96%);
}

body.light-mode .section-icon {
  filter: brightness(0) saturate(100%) invert(92%) sepia(99%) saturate(7489%)
    hue-rotate(337deg) brightness(99%) contrast(98%);
}

.summary-border {
  border-color: var(--border) !important;
}

.checkout-submit-btn:disabled {
  opacity: 1 !important;
  pointer-events: none;
  background-color: var(--primary) !important;
  border-color: transparent !important;
  color: var(--primary-foreground) !important;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: var(--z-modal);
}

.modal-content {
  max-width: 500px;
  width: 90%;
  border: 1px solid var(--border);
  backdrop-filter: blur(8px);
}

.home-icon {
  color: inherit;
}
</style>
