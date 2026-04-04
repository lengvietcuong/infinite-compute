<script setup>
import { ref, onMounted, watchEffect, computed } from "vue";
import { useCart } from "../composables/useCart";
import { useAuth } from "../composables/useAuth";
import { useRouter } from "vue-router";
import { formatPrice } from "../utils/format";
import { API_BASE_URL } from "@/config/api";

const { cart, cartTotal, clearCart } = useCart();
const { user, isAuthenticated } = useAuth();
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

const discountApplied = ref(false);
const discountPercent = ref(0);
const discountError = ref(null);
const discountSuccess = ref(null);
const isCheckingDiscount = ref(false);
const copied = ref(false);

const copyTrackingNumber = async () => {
  try {
    await navigator.clipboard.writeText(orderId.value);
    copied.value = true;
    setTimeout(() => (copied.value = false), 2000);
  } catch {
    // Fallback for older browsers
    const textarea = document.createElement("textarea");
    textarea.value = orderId.value;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
    copied.value = true;
    setTimeout(() => (copied.value = false), 2000);
  }
};

const discountAmount = computed(() => {
  return cartTotal.value * (discountPercent.value / 100);
});

const finalTotal = computed(() => {
  return cartTotal.value - discountAmount.value;
});

const applyDiscount = async () => {
  if (!form.value.discountCode) return;

  isCheckingDiscount.value = true;
  discountError.value = null;
  discountSuccess.value = null;

  try {
    const response = await fetch(
      `${API_BASE_URL}/orders/validate-coupon/${form.value.discountCode}`
    );

    if (!response.ok) {
      throw new Error("Invalid discount code");
    }

    const data = await response.json();
    discountPercent.value = parseFloat(data.discount_percent);
    discountApplied.value = true;
    discountSuccess.value = `Discount applied: ${data.discount_percent}% off`;
  } catch (err) {
    discountError.value = "Invalid discount code";
    discountApplied.value = false;
    discountPercent.value = 0;
  } finally {
    isCheckingDiscount.value = false;
  }
};

const removeDiscount = () => {
  form.value.discountCode = "";
  discountApplied.value = false;
  discountPercent.value = 0;
  discountSuccess.value = null;
  discountError.value = null;
};

// Auto-fill user data
watchEffect(() => {
  if (user.value) {
    form.value.email = user.value.email || "";
    form.value.name = user.value.full_name || "";
  }
});

const isProcessing = ref(false);
const showModal = ref(false);
const orderId = ref(null);
const error = ref(null);

const validationErrors = ref({
  name: null,
  email: null,
  expiry: null,
  cvc: null,
});

const validateName = () => {
  if (!form.value.name.trim()) {
    validationErrors.value.name = null;
    return true;
  }
  const hasNumbers = /\d/.test(form.value.name);
  if (hasNumbers) {
    validationErrors.value.name = "Name cannot contain numbers";
    return false;
  }
  validationErrors.value.name = null;
  return true;
};

const validateEmail = () => {
  if (!form.value.email.trim()) {
    validationErrors.value.email = null;
    return true;
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(form.value.email)) {
    validationErrors.value.email = "Please enter a valid email address";
    return false;
  }
  validationErrors.value.email = null;
  return true;
};

const validateExpiry = () => {
  if (!form.value.expiry.trim()) {
    validationErrors.value.expiry = null;
    return true;
  }
  const digitsOnly = form.value.expiry.replace(/\D/g, "");
  if (digitsOnly.length !== 4) {
    validationErrors.value.expiry = "Expiry date must have 4 digits (MM/YY)";
    return false;
  }
  validationErrors.value.expiry = null;
  return true;
};

const validateCvc = () => {
  if (!form.value.cvc.trim()) {
    validationErrors.value.cvc = null;
    return true;
  }
  const digitsOnly = form.value.cvc.replace(/\D/g, "");
  if (digitsOnly.length !== 3) {
    validationErrors.value.cvc = "CVC must have 3 digits";
    return false;
  }
  validationErrors.value.cvc = null;
  return true;
};

const formatCvc = (e) => {
  const value = e.target.value.replace(/\D/g, "").slice(0, 3);
  e.target.value = value;
  form.value.cvc = value;
};

const validateForm = () => {
  const isNameValid = validateName();
  const isEmailValid = validateEmail();
  const isExpiryValid = validateExpiry();
  const isCvcValid = validateCvc();

  return isNameValid && isEmailValid && isExpiryValid && isCvcValid;
};

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
  if (!validateForm()) {
    error.value = "Please fix the validation errors before submitting";
    return;
  }

  // Validate stock before placing order
  for (const item of cart.value) {
    if (item.stock_quantity !== undefined && item.stock_quantity <= 0) {
      error.value = `${item.name} is out of stock. Please remove it from your cart.`;
      return;
    }
    if (
      item.stock_quantity !== undefined &&
      item.quantity > item.stock_quantity
    ) {
      error.value = `Insufficient stock for ${item.name}. Only ${item.stock_quantity} units available.`;
      return;
    }
  }

  isProcessing.value = true;
  error.value = null;

  try {
    const orderData = {
      guest_email: isAuthenticated.value ? null : form.value.email,
      shipping_address: `${form.value.name}\n${form.value.address}, ${form.value.city}, ${form.value.zip}`,
      items: cart.value.map((item) => ({
        product_id: item.id,
        quantity: item.quantity,
      })),
      discount_code: form.value.discountCode || null,
    };

    const token = localStorage.getItem("token");
    const headers = {
      "Content-Type": "application/json",
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/orders`, {
      method: "POST",
      headers: headers,
      body: JSON.stringify(orderData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to place order");
    }

    const order = await response.json();
    orderId.value = order.tracking_number;
    showModal.value = true;
    clearCart();
  } catch (err) {
    error.value = err.message;
    console.error("Order placement error:", err);
  } finally {
    isProcessing.value = false;
  }
};

const handleOverlayClick = () => {
  router.push("/");
};
</script>

<template>
  <div class="checkout-page container">
    <h1
      class="page-title mb-5 d-flex align-items-center justify-content-center gap-3"
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

    <div class="row g-5">
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
            <div
              v-if="discountApplied"
              class="d-flex justify-content-between mb-2 text-success"
            >
              <span class="summary-label"
                >Discount ({{ discountPercent }}%)</span
              >
              <span class="summary-value"
                >-${{ formatPrice(discountAmount) }}</span
              >
            </div>
            <div class="d-flex justify-content-between mb-2">
              <span class="summary-label">Shipping</span>
              <span class="summary-value">Free</span>
            </div>
            <div
              class="d-flex justify-content-between fw-bold mt-3 fs-5 total-row"
            >
              <span>Total</span>
              <span>${{ formatPrice(finalTotal) }}</span>
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
                :class="{ 'is-invalid': validationErrors.name }"
                placeholder="John Doe"
                required
                @blur="validateName"
              />
              <div
                v-if="validationErrors.name"
                class="text-destructive mt-1 small"
              >
                {{ validationErrors.name }}
              </div>
            </div>
            <div class="col-sm-6">
              <label class="form-label">Email</label>
              <input
                v-model="form.email"
                type="email"
                class="form-control"
                :class="{ 'is-invalid': validationErrors.email }"
                placeholder="john@example.com"
                required
                @blur="validateEmail"
              />
              <div
                v-if="validationErrors.email"
                class="text-destructive mt-1 small"
              >
                {{ validationErrors.email }}
              </div>
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
                  :disabled="discountApplied"
                  @keyup.enter="applyDiscount"
                />
                <button
                  v-if="!discountApplied"
                  type="button"
                  class="btn btn-outline"
                  @click="applyDiscount"
                  :disabled="isCheckingDiscount || !form.discountCode"
                >
                  <span
                    v-if="isCheckingDiscount"
                    class="spinner-border spinner-border-sm"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  {{ isCheckingDiscount ? "Checking..." : "Apply" }}
                </button>
                <button
                  v-else
                  type="button"
                  class="btn btn-outline-destructive"
                  @click="removeDiscount"
                >
                  Remove
                </button>
              </div>
              <div v-if="discountError" class="text-destructive mt-1 small">
                {{ discountError }}
              </div>
              <div v-if="discountSuccess" class="text-primary mt-1 small">
                {{ discountSuccess }}
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
                :class="{ 'is-invalid': validationErrors.expiry }"
                placeholder="MM/YY"
                maxlength="5"
                required
                @blur="validateExpiry"
              />
              <div
                v-if="validationErrors.expiry"
                class="text-destructive mt-1 small"
              >
                {{ validationErrors.expiry }}
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">CVC</label>
              <input
                :value="form.cvc"
                @input="formatCvc"
                type="text"
                class="form-control"
                :class="{ 'is-invalid': validationErrors.cvc }"
                placeholder="123"
                maxlength="3"
                required
                @blur="validateCvc"
              />
              <div
                v-if="validationErrors.cvc"
                class="text-destructive mt-1 small"
              >
                {{ validationErrors.cvc }}
              </div>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="alert alert-danger mt-3" role="alert">
            {{ error }}
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
      <div class="modal-content glass-card p-5 text-center" @click.stop>
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
        <p class="text-muted mb-4 d-flex align-items-center justify-content-center gap-2 flex-wrap">
          <span>Your Tracking Number:</span>
          <strong>{{ orderId }}</strong>
          <button
            class="btn-copy"
            @click="copyTrackingNumber"
            :title="copied ? 'Copied!' : 'Copy tracking number'"
            type="button"
          >
            <svg
              v-if="!copied"
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
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
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
            >
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </button>
        </p>
        <div class="d-flex gap-2 justify-content-center">
          <router-link
            :to="{ path: '/track-order', query: { q: orderId } }"
            class="btn btn-outline d-inline-flex align-items-center gap-2"
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
              <path
                d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"
              />
              <circle cx="7" cy="18" r="2" />
              <path d="M15 18H9" />
              <path
                d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.63l-1.02-1.53a1 1 0 0 0-.84-.37H14"
              />
              <circle cx="17" cy="18" r="2" />
            </svg>
            Track Order
          </router-link>
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
  font-size: 0.875rem;
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

.form-control.is-invalid {
  border-color: var(--destructive);
}

.form-control.is-invalid:focus {
  border-color: var(--destructive);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--destructive), transparent 80%);
}

.text-success {
  color: var(--primary);
}

.text-destructive {
  color: var(--destructive);
}

.btn-outline-destructive {
  background-color: var(--background);
  color: var(--destructive);
  border: 1px solid var(--destructive);
  box-shadow: var(--shadow-sm);
}

.btn-outline-destructive:hover {
  background-color: color-mix(in srgb, var(--destructive), transparent 90%);
  color: var(--destructive);
}

.btn-outline:disabled {
  opacity: 1;
  border-color: var(--border);
  color: color-mix(in srgb, var(--foreground), transparent 50%);
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

.alert-danger {
  color: var(--destructive);
  background-color: color-mix(in srgb, var(--destructive), transparent 90%);
  border: 1px solid color-mix(in srgb, var(--destructive), transparent 80%);
  padding: var(--spacing-sm);
  border-radius: var(--radius);
}

.btn-copy {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--muted), transparent 50%);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 4px 6px;
  cursor: pointer;
  color: var(--muted-foreground);
  transition: all 0.2s;
}

.btn-copy:hover {
  background: var(--muted);
  color: var(--foreground);
}
</style>
