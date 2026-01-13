<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useCart } from "../composables/useCart";
import { useAuth } from "../composables/useAuth";
import { formatPrice } from "../utils/format";

const router = useRouter();
const { cartItemCount, toggleCart } = useCart();
const { isAuthenticated, user, isAdmin, logout } = useAuth();
const isVisible = ref(true);
const isScrolled = ref(false);
const isDarkMode = ref(true);
const isMenuExpanded = ref(false);
const searchQuery = ref("");
const searchResults = ref([]);
const showDropdown = ref(false);
const isLoading = ref(false);
let lastScrollPosition = 0;
let searchTimeout = null;

const handleScroll = () => {
  const currentScrollPosition = window.scrollY;

  if (currentScrollPosition < 0) {
    return;
  }

  if (currentScrollPosition < 10) {
    isVisible.value = true;
    isScrolled.value = false;
    return;
  }

  isScrolled.value = currentScrollPosition > 10;

  if (Math.abs(currentScrollPosition - lastScrollPosition) < 60) {
    return;
  }

  isVisible.value = currentScrollPosition < lastScrollPosition;
  lastScrollPosition = currentScrollPosition;
};

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
  if (isDarkMode.value) {
    document.body.classList.remove("light-mode");
    localStorage.setItem("theme", "dark");
  } else {
    document.body.classList.add("light-mode");
    localStorage.setItem("theme", "light");
  }
};

const collapseMenu = () => {
  const navbarToggler = document.querySelector(".navbar-toggler");
  if (navbarToggler && isMenuExpanded.value) {
    navbarToggler.click();
  }
};

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: "/products", query: { search: searchQuery.value } });
    showDropdown.value = false;
    collapseMenu();
  }
};

const fetchSearchResults = async () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = [];
    showDropdown.value = false;
    return;
  }

  isLoading.value = true;
  showDropdown.value = true;

  try {
    const params = new URLSearchParams({
      search: searchQuery.value,
      limit: 5,
    });
    const response = await fetch(
      `http://localhost:8000/products?${params.toString()}`
    );
    if (response.ok) {
      searchResults.value = await response.json();
    }
  } catch (error) {
    console.error("Search failed:", error);
    searchResults.value = [];
  } finally {
    isLoading.value = false;
  }
};

watch(searchQuery, () => {
  if (searchTimeout) clearTimeout(searchTimeout);
  if (!searchQuery.value.trim()) {
    searchResults.value = [];
    showDropdown.value = false;
    return;
  }
  searchTimeout = setTimeout(fetchSearchResults, 300);
});

const selectResult = (id) => {
  router.push(`/products/${id}`);
  searchQuery.value = "";
  showDropdown.value = false;
  collapseMenu();
};

const closeDropdown = () => {
  setTimeout(() => {
    showDropdown.value = false;
  }, 200);
};

onMounted(() => {
  window.addEventListener("scroll", handleScroll, { passive: true });

  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "light") {
    isDarkMode.value = false;
    document.body.classList.add("light-mode");
  }
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});
</script>

<template>
  <header
    class="app-header navbar navbar-expand-xl"
    :class="{
      'navbar-hidden': !isVisible,
      'navbar-scrolled': isScrolled,
      'navbar-expanded': isMenuExpanded,
    }"
  >
    <div class="container">
      <div class="d-flex align-items-center gap-3">
        <router-link class="navbar-brand" to="/">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="infinity-logo"
          >
            <path
              d="M6 16c5 0 7-8 12-8a4 4 0 0 1 0 8c-5 0-7-8-12-8a4 4 0 1 0 0 8"
            />
          </svg>
          InfiniteCompute
        </router-link>
        <nav class="nav-links d-none d-xl-flex gap-4 align-items-center">
          <router-link class="nav-link text-foreground" to="/products"
            >Products</router-link
          >
          <router-link class="nav-link text-foreground" to="/track-order"
            >Track Order</router-link
          >
          <router-link class="nav-link text-foreground" to="/news"
            >News</router-link
          >
          <router-link class="nav-link text-foreground" to="/about"
            >About</router-link
          >
        </nav>
      </div>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        @click="isMenuExpanded = !isMenuExpanded"
      >
        <div
          v-if="!isMenuExpanded"
          class="menu-icon hamburger-icon"
          aria-label="Menu"
        ></div>
        <div v-else class="menu-icon x-icon" aria-label="Close"></div>
      </button>
      <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
        <ul class="navbar-nav align-items-center nav-items-desktop">
          <li class="nav-item d-lg-none mt-3">
            <router-link
              class="nav-link text-foreground"
              to="/products"
              @click="collapseMenu"
              >Products</router-link
            >
          </li>
          <li class="nav-item d-lg-none">
            <router-link
              class="nav-link text-foreground"
              to="/track-order"
              @click="collapseMenu"
              >Track Order</router-link
            >
          </li>
          <li class="nav-item d-lg-none">
            <router-link
              class="nav-link text-foreground"
              to="/news"
              @click="collapseMenu"
              >News</router-link
            >
          </li>
          <li class="nav-item d-lg-none mb-3">
            <router-link
              class="nav-link text-foreground"
              to="/about"
              @click="collapseMenu"
              >About</router-link
            >
          </li>
          <li class="nav-item d-none d-xl-block">
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
                type="search"
                placeholder="Search..."
                class="search-input"
                v-model="searchQuery"
                @keyup.enter="handleSearch"
                @focus="showDropdown = true"
                @blur="closeDropdown"
                aria-label="Search products"
              />

              <!-- Search Results Dropdown -->
              <div
                v-if="showDropdown && searchResults.length > 0"
                class="search-dropdown"
              >
                <a
                  v-for="product in searchResults"
                  :key="product.id"
                  href="#"
                  class="search-result-item"
                  @click.prevent="selectResult(product.id)"
                >
                  <div class="result-image">
                    <img
                      :src="product.image_url || '/images/default-product.webp'"
                      :alt="product.name"
                      @error="
                        $event.target.src =
                          'https://placehold.co/100x100/1a1a1a/FFF?text=IMG'
                      "
                    />
                  </div>
                  <div class="result-info">
                    <div class="result-name">{{ product.name }}</div>
                    <div class="result-price">
                      ${{ formatPrice(product.price) }}
                    </div>
                  </div>
                </a>
                <div class="dropdown-footer" @click="handleSearch">
                  See all results for "{{ searchQuery }}"
                </div>
              </div>
            </div>
          </li>
          <!-- Dashboard Icon (Admin/Staff) -->
          <li
            class="nav-item d-none d-xl-block"
            v-if="isAuthenticated && isAdmin"
          >
            <router-link
              class="nav-icon-btn d-flex align-items-center gap-2 text-decoration-none"
              to="/dashboard"
              aria-label="Dashboard"
              title="Dashboard"
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
                <rect width="7" height="9" x="3" y="3" rx="1" />
                <rect width="7" height="5" x="14" y="3" rx="1" />
                <rect width="7" height="9" x="14" y="12" rx="1" />
                <rect width="7" height="5" x="3" y="16" rx="1" />
              </svg>
              <span class="d-none d-xxl-inline dashboard-text">Dashboard</span>
            </router-link>
          </li>

          <!-- Cart Icon -->
          <li class="nav-item d-none d-xl-block cart-nav-item">
            <button
              class="btn btn-icon btn-ghost position-relative cart-icon-btn"
              @click="toggleCart"
              aria-label="Open Cart"
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
                <circle cx="8" cy="21" r="1" />
                <circle cx="19" cy="21" r="1" />
                <path
                  d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"
                />
              </svg>
              <span v-if="cartItemCount > 0" class="cart-badge">
                {{ cartItemCount }}
                <span class="visually-hidden">items in cart</span>
              </span>
            </button>
          </li>

          <!-- Theme Toggle (Moved here) -->
          <li class="nav-item d-none d-xl-block">
            <button
              class="btn btn-sm btn-icon btn-ghost theme-toggle"
              @click="toggleTheme"
              :aria-label="
                isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'
              "
            >
              <svg
                v-if="isDarkMode"
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2" />
                <path d="M12 20v2" />
                <path d="m4.93 4.93 1.41 1.41" />
                <path d="m17.66 17.66 1.41 1.41" />
                <path d="M2 12h2" />
                <path d="M20 12h2" />
                <path d="m6.34 17.66-1.41 1.41" />
                <path d="m19.07 4.93-1.41 1.41" />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
              </svg>
            </button>
          </li>

          <!-- Mobile Cart (Visible only on lg and below) -->
          <li class="nav-item d-lg-none">
            <button
              class="btn btn-icon btn-ghost position-relative cart-icon-btn"
              @click="toggleCart"
              aria-label="Open Cart"
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
                <circle cx="8" cy="21" r="1" />
                <circle cx="19" cy="21" r="1" />
                <path
                  d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"
                />
              </svg>
              <span v-if="cartItemCount > 0" class="cart-badge">
                {{ cartItemCount }}
                <span class="visually-hidden">items in cart</span>
              </span>
            </button>
          </li>

          <!-- Mobile Theme Toggle (Visible only on lg and below, right next to cart) -->
          <li class="nav-item d-lg-none">
            <button
              class="btn btn-sm btn-icon btn-ghost theme-toggle"
              @click="toggleTheme"
              :aria-label="
                isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'
              "
            >
              <svg
                v-if="isDarkMode"
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2" />
                <path d="M12 20v2" />
                <path d="m4.93 4.93 1.41 1.41" />
                <path d="m17.66 17.66 1.41 1.41" />
                <path d="M2 12h2" />
                <path d="M20 12h2" />
                <path d="m6.34 17.66-1.41 1.41" />
                <path d="m19.07 4.93-1.41 1.41" />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
              </svg>
            </button>
          </li>

          <!-- Auth Section -->
          <li class="nav-item auth-nav-group" v-if="!isAuthenticated">
            <router-link class="btn btn-sm btn-outline" to="/sign-in"
              >Login</router-link
            >
          </li>
          <li class="nav-item mb-3 mb-lg-0" v-if="!isAuthenticated">
            <router-link class="btn btn-sm btn-primary" to="/sign-up"
              >Sign Up</router-link
            >
          </li>

          <!-- Mobile Logout Button (Visible only on lg and below when authenticated) -->
          <li class="nav-item d-lg-none" v-if="isAuthenticated">
            <button
              class="btn btn-sm btn-icon btn-ghost logout-icon-btn"
              @click="logout"
              aria-label="Log Out"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" x2="9" y1="12" y2="12" />
              </svg>
            </button>
          </li>

          <!-- User Dropdown (Desktop only - hidden on mobile/tablet) -->
          <li class="nav-item dropdown d-none d-xl-block" v-if="isAuthenticated">
            <button
              class="btn btn-icon btn-ghost nav-icon-btn user-icon-btn"
              data-bs-toggle="dropdown"
              aria-expanded="false"
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
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </button>
            <ul class="dropdown-menu dropdown-menu-end user-dropdown-menu">
              <li>
                <button
                  class="dropdown-item d-flex align-items-center gap-2 text-destructive logout-item"
                  @click="logout"
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
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                    <polyline points="16 17 21 12 16 7" />
                    <line x1="21" x2="9" y1="12" y2="12" />
                  </svg>
                  Log Out
                </button>
              </li>
            </ul>
          </li>

        </ul>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: var(--z-fixed);
  transition: transform var(--transition-slow) ease-in-out,
    background-color var(--transition-slow) ease,
    backdrop-filter var(--transition-slow) ease;
  transform: translateY(0);
  padding-top: var(--spacing-sm);
  padding-bottom: var(--spacing-sm);
}

.navbar-scrolled,
.navbar-expanded {
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

body.light-mode .navbar-scrolled,
body.light-mode .navbar-expanded {
  background-color: rgba(255, 255, 255, 0.5);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.navbar-hidden {
  transform: translateY(-100%);
}

.nav-link {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  transition: color var(--transition-base);
  text-decoration: none;
  padding: 0;
}
.nav-link:hover {
  color: var(--primary) !important;
}
.infinity-logo {
  color: var(--primary);
}
.search-wrapper {
  position: relative;
  display: inline-block;
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
  height: 2.25rem;
  width: 200px;
  min-width: 0;
  border-radius: var(--radius);
  border: 1px solid var(--input);
  background: var(--background);
  padding: var(--spacing-xs) var(--spacing-sm) var(--spacing-xs) 2.25rem;
  font-size: 0.875rem;
  box-shadow: var(--shadow-sm);
  transition: color var(--transition-base), box-shadow var(--transition-base);
  outline: none;
  color: var(--foreground);
}
.search-input::placeholder {
  color: var(--muted-foreground);
}
.search-input::selection {
  background-color: var(--primary);
  color: var(--primary-foreground);
}
.search-input:focus-visible {
  border-color: var(--ring);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--ring), transparent 50%);
}
.search-input[aria-invalid="true"] {
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--destructive), transparent 80%);
  border-color: var(--destructive);
}
.search-input:disabled {
  pointer-events: none;
  cursor: not-allowed;
  opacity: var(--opacity-disabled);
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: var(--spacing-sm);
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-lg);
  z-index: var(--z-dropdown);
  overflow: hidden;
  width: 300px;
  max-height: 400px;
  overflow-y: auto;
}

@media (max-width: 991px) {
  .search-dropdown {
    width: 100%;
  }
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm);
  text-decoration: none;
  color: var(--foreground);
  transition: background-color var(--transition-base);
}

.search-result-item:not(:last-of-type) {
  border-bottom: 1px solid var(--border);
  border-color: var(--border);
}

.search-result-item:hover {
  background-color: color-mix(in srgb, var(--primary), transparent 90%);
}

.result-image {
  width: 40px;
  height: 40px;
  border-radius: var(--radius);
  overflow: hidden;
  background-color: var(--card);
  flex-shrink: 0;
}

.result-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.result-info {
  flex: 1;
  min-width: 0;
}

.result-name {
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 0.125rem;
}

.result-price {
  font-size: 0.75rem;
  color: var(--primary);
  font-family: var(--font-mono);
}

.dropdown-footer {
  padding: var(--spacing-sm);
  text-align: center;
  font-size: 0.875rem;
  color: var(--primary);
  cursor: pointer;
  background-color: color-mix(in srgb, var(--card), transparent 50%);
  border-top: 1px solid var(--border);
  transition: background-color var(--transition-base);
}

.dropdown-footer:hover {
  background-color: color-mix(in srgb, var(--primary), transparent 90%);
}

.navbar-toggler {
  border: none;
  padding: 0.25rem 0.5rem;
  background: transparent;
  border-radius: 0;
  color: var(--foreground);
}

.navbar-toggler:focus {
  box-shadow: none;
  border: none;
  outline: none;
}

.navbar-toggler-icon {
  display: none;
}

.menu-icon {
  width: 1.5em;
  height: 1.5em;
  display: block;
  background-color: var(--foreground);
  -webkit-mask-size: contain;
  mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  mask-repeat: no-repeat;
  -webkit-mask-position: center;
  mask-position: center;
}

.hamburger-icon {
  -webkit-mask-image: url("/icons/hamburger-menu.svg");
  mask-image: url("/icons/hamburger-menu.svg");
}

.x-icon {
  -webkit-mask-image: url("/icons/x.svg");
  mask-image: url("/icons/x.svg");
}

.theme-toggle {
  color: var(--foreground);
}

.theme-toggle:hover {
  color: var(--primary);
}

.cart-icon-btn {
  color: var(--foreground);
}

.cart-icon-btn:hover {
  color: var(--primary);
}

.logout-icon-btn {
  color: var(--foreground);
}

.logout-icon-btn:hover {
  color: var(--primary);
}

.nav-icon-btn {
  color: var(--foreground);
  transition: color var(--transition-base);
  padding: 0.5rem;
}

.nav-icon-btn:hover {
  color: var(--primary);
}

.user-icon-btn {
  transition: background-color var(--transition-base),
    color var(--transition-base);
}

.user-icon-btn:hover {
  background-color: var(--muted);
}

.user-icon-btn:focus,
.user-icon-btn:focus-visible {
  box-shadow: none;
  border-color: transparent;
  outline: none;
}

.cart-badge {
  position: absolute;
  top: 0;
  left: 100%;
  transform: translate(-50%, -50%);
  background-color: var(--primary);
  color: var(--primary-foreground);
  font-size: var(--text-xs);
  min-width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  padding: 0 0.35em;
}

.nav-items-desktop {
  gap: 0;
}

.nav-items-desktop > .nav-item {
  margin-left: var(--spacing-sm);
}

.cart-nav-item {
  margin-left: var(--spacing-sm) !important;
}

.auth-nav-group {
  margin-left: var(--spacing-xl) !important;
}

@media (max-width: 1279px) {
  .nav-items-desktop > .nav-item {
    margin-left: 0;
    margin-bottom: var(--spacing-sm);
  }

  .cart-nav-item,
  .auth-nav-group {
    margin-left: 0 !important;
  }
}

.dashboard-text {
  font-size: var(--text-sm);
}
</style>
