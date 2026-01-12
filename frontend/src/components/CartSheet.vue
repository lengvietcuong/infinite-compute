<script setup>
import { useCart } from "../composables/useCart";
import { useRouter } from "vue-router";

const {
  cart,
  isCartOpen,
  removeFromCart,
  updateQuantity,
  cartTotal,
  toggleCart,
} = useCart();
const router = useRouter();

const formatPrice = (price) => {
  return parseFloat(price).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

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
      <button class="close-btn" @click="toggleCart">
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
        >
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <div class="cart-body">
      <div v-if="cart.length === 0" class="empty-cart">
        <p>Your cart is empty.</p>
        <button class="btn btn-outline-primary btn-sm mt-3" @click="toggleCart">
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
            <div class="item-controls">
              <div class="quantity-control">
                <button
                  class="qty-btn"
                  @click="updateQuantity(item.id, item.quantity - 1)"
                >
                  -
                </button>
                <span class="qty-val">{{ item.quantity }}</span>
                <button
                  class="qty-btn"
                  @click="updateQuantity(item.id, item.quantity + 1)"
                >
                  +
                </button>
              </div>
              <button class="remove-btn" @click="removeFromCart(item.id)">
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
  z-index: 1040;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s ease, visibility 0.3s ease;
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
  z-index: 1050;
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--border);
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.15);
}

.cart-sheet.open {
  transform: translateX(0);
}

.cart-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cart-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: var(--muted-foreground);
  cursor: pointer;
  padding: 0.25rem;
  transition: color 0.2s;
}

.close-btn:hover {
  color: var(--foreground);
}

.cart-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.empty-cart {
  text-align: center;
  color: var(--muted-foreground);
  padding-top: 2rem;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.cart-item {
  display: flex;
  gap: 1rem;
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
  font-size: 0.95rem;
  margin: 0 0 0.25rem 0;
  line-height: 1.3;
}

.item-price {
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--primary);
  margin: 0;
}

.item-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
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
  padding: 0.25rem 0.5rem;
  color: var(--foreground);
  cursor: pointer;
}

.qty-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.qty-val {
  padding: 0 0.5rem;
  font-size: 0.85rem;
  min-width: 1.5rem;
  text-align: center;
}

.remove-btn {
  background: none;
  border: none;
  color: var(--destructive, #ef4444);
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0;
}

.remove-btn:hover {
  text-decoration: underline;
}

.cart-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--border);
  background: var(--background);
}

.cart-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.total-amount {
  font-family: var(--font-mono);
  color: var(--primary);
}

.checkout-btn {
  font-weight: 600;
  padding: 0.75rem;
}
</style>
