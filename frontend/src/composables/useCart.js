import { ref, computed, watch } from 'vue';

const cart = ref([]);
const isCartOpen = ref(false);

// Load cart from local storage
const loadCart = () => {
  const savedCart = localStorage.getItem('cart');
  if (savedCart) {
    cart.value = JSON.parse(savedCart);
  }
};

// Save cart to local storage
const saveCart = () => {
  localStorage.setItem('cart', JSON.stringify(cart.value));
};

export function useCart() {
  // Initialize cart on first use
  if (cart.value.length === 0) {
    loadCart();
  }

  // Watch for changes and save
  watch(cart, saveCart, { deep: true });

  const addToCart = (product) => {
    const existingItem = cart.value.find((item) => item.id === product.id);
    if (existingItem) {
      existingItem.quantity += 1;
    } else {
      cart.value.push({
        id: product.id,
        name: product.name,
        price: product.price,
        image_url: product.image_url,
        quantity: 1,
      });
    }
    isCartOpen.value = true;
  };

  const removeFromCart = (productId) => {
    cart.value = cart.value.filter((item) => item.id !== productId);
  };

  const updateQuantity = (productId, quantity) => {
    const item = cart.value.find((item) => item.id === productId);
    if (item) {
      item.quantity = quantity;
      if (item.quantity <= 0) {
        removeFromCart(productId);
      }
    }
  };

  const clearCart = () => {
    cart.value = [];
  };

  const cartTotal = computed(() => {
    return cart.value.reduce((total, item) => total + item.price * item.quantity, 0);
  });

  const cartItemCount = computed(() => {
    return cart.value.reduce((count, item) => count + item.quantity, 0);
  });

  const toggleCart = () => {
    isCartOpen.value = !isCartOpen.value;
  };

  return {
    cart,
    isCartOpen,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    cartTotal,
    cartItemCount,
    toggleCart,
  };
}
