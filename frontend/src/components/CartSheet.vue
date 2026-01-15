<script setup>
import { useCart } from "../composables/useCart";
import { useRouter } from "vue-router";
import { formatPrice } from "../utils/format";

const {
  cart,
  isCartOpen,
  removeFromCart,
  updateQuantity,
  cartTotal,
  toggleCart,
} = useCart();
const router = useRouter();

const handleCheckout = () => {
  toggleCart();
  const navbarToggler = document.querySelector(".navbar-toggler");
  if (navbarToggler) {
    const navbar = document.querySelector(".navbar");
    if (navbar && navbar.classList.contains("navbar-expanded")) {
      navbarToggler.click();
    }
  }
  router.push("/checkout");
};
</script>

<template>
  <div
    class="cart-sheet-overlay"
    :class="{ open: isCartOpen }"
    @click="toggleCart"
  ></div>
  <div class="cart-sheet" :class="{ open: isCartOpen }">
    <div class="cart-header">
      <h3>Shopping Cart</h3>
      <button class="close-btn" @click="toggleCart" aria-label="Close cart">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <div class="cart-body">
      <div v-if="cart.length === 0" class="empty-cart">
        <p>Your cart is empty.</p>
        <button class="btn btn-primary btn-sm mt-3" @click="toggleCart">
          Continue Shopping
        </button>
      </div>

      <div v-else class="cart-items">
        <div v-for="item in cart" :key="item.id" class="cart-item">
          <div class="item-image">
            <img
              :src="item.image_url || '/images/default-product.webp'"
              :alt="item.name"
            />
          </div>
          <div class="item-details">
            <h4 class="item-name">{{ item.name }}</h4>
            <p class="item-price">${{ formatPrice(item.price) }}</p>
            <p v-if="item.stock_quantity !== undefined" class="item-stock">
              <span v-if="item.stock_quantity <= 0" class="stock-error"
                >Out of Stock</span
              >
              <span
                v-else-if="item.quantity >= item.stock_quantity"
                class="stock-info"
                >Max stock reached</span
              >
              <span v-else class="stock-available"
                >{{ item.stock_quantity }} in stock</span
              >
            </p>
            <div class="item-controls">
              <div class="quantity-control" role="group" aria-label="Quantity">
                <button
                  class="qty-btn"
                  @click="updateQuantity(item.id, item.quantity - 1)"
                  aria-label="Decrease quantity"
                >
                  -
                </button>
                <span class="qty-val" aria-live="polite">{{
                  item.quantity
                }}</span>
                <button
                  class="qty-btn"
                  @click="updateQuantity(item.id, item.quantity + 1)"
                  :disabled="
                    item.stock_quantity !== undefined &&
                    item.quantity >= item.stock_quantity
                  "
                  aria-label="Increase quantity"
                >
                  +
                </button>
              </div>
              <button
                class="remove-btn"
                @click="removeFromCart(item.id)"
                :aria-label="`Remove ${item.name} from cart`"
              >
                Remove
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="cart-footer" v-if="cart.length > 0">
      <div class="cart-total">
        <span>Subtotal</span>
        <span class="total-amount">${{ formatPrice(cartTotal) }}</span>
      </div>
      <button
        class="btn btn-primary w-100 checkout-btn"
        @click="handleCheckout"
      >
        Proceed to Checkout
      </button>
    </div>
  </div>
</template>

<style scoped>
.cart-sheet-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: var(--z-modal-backdrop);
  opacity: 0;
  visibility: hidden;
  transition: opacity var(--transition-slow) ease,
    visibility var(--transition-slow) ease;
  backdrop-filter: blur(2px);
}

.cart-sheet-overlay.open {
  opacity: 1;
  visibility: visible;
}

.cart-sheet {
  position: fixed;
  top: 0;
  right: 0;
  width: 100%;
  max-width: 400px;
  height: 100%;
  background: var(--background);
  z-index: var(--z-modal);
  transform: translateX(100%);
  transition: transform var(--transition-slow) cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--border);
  box-shadow: var(--shadow-xl);
}

.cart-sheet.open {
  transform: translateX(0);
}

.cart-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cart-header h3 {
  margin: 0;
  font-size: var(--text-xl);
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: var(--muted-foreground);
  cursor: pointer;
  padding: var(--spacing-xs);
  transition: color var(--transition-base);
}

.close-btn:hover {
  color: var(--foreground);
}

.cart-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

.empty-cart {
  text-align: center;
  color: var(--muted-foreground);
  padding-top: var(--spacing-xl);
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.cart-item {
  display: flex;
  gap: var(--spacing-md);
}

.item-image {
  width: 80px;
  height: 80px;
  background: var(--card);
  border-radius: var(--radius);
  overflow: hidden;
  flex-shrink: 0;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.item-name {
  font-size: var(--text-base);
  margin: 0 0 0.25rem 0;
  line-height: 1.3;
}

.item-price {
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--primary);
  margin: 0;
}

.item-stock {
  font-size: var(--text-xs);
  margin: 0.25rem 0 0 0;
}

.item-stock .stock-error {
  color: var(--destructive);
}

.item-stock .stock-info {
  color: var(--muted-foreground);
}

.item-stock .stock-available {
  color: var(--muted-foreground);
}

.item-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-sm);
}

.quantity-control {
  display: flex;
  align-items: center;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.qty-btn {
  background: none;
  border: none;
  padding: var(--spacing-xs) var(--spacing-sm);
  color: var(--foreground);
  cursor: pointer;
}

.qty-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.qty-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.qty-val {
  padding: 0 var(--spacing-sm);
  font-size: var(--text-sm);
  min-width: 1.5rem;
  text-align: center;
}

.remove-btn {
  background: none;
  border: none;
  color: var(--destructive);
  font-size: var(--text-sm);
  cursor: pointer;
  padding: 0;
}

.remove-btn:hover {
  text-decoration: underline;
}

.cart-footer {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border);
  background: var(--background);
}

.cart-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  font-size: var(--text-lg);
  font-weight: 600;
}

.total-amount {
  font-family: var(--font-mono);
  color: var(--primary);
}

.checkout-btn {
  font-weight: 600;
  padding: var(--spacing-sm);
}
</style>
