<script setup>
import { ref, computed, watch } from "vue";
import { useAuth } from "../../composables/useAuth";
import { useRouter } from "vue-router";
import Analytics from "./Analytics.vue";
import Products from "./Products.vue";
import Users from "./Users.vue";
import Orders from "./Orders.vue";
import Reviews from "./Reviews.vue";
import Coupons from "./Coupons.vue";
import Conversations from "./Conversations.vue";
import Toast from "../../components/ui/Toast.vue";

const { user } = useAuth();
const router = useRouter();

const tabs = computed(() => {
  if (user.value?.role === "admin") {
    return [
      "Analytics",
      "Users",
      "Products",
      "Orders",
      "Reviews",
      "Coupons",
      "Conversations",
    ];
  }
  return ["Products", "Orders", "Reviews", "Coupons", "Conversations"];
});

const activeTab = ref("Analytics");

watch(
  user,
  (newUser) => {
    if (
      newUser?.role !== "admin" &&
      (activeTab.value === "Analytics" || activeTab.value === "Users")
    ) {
      activeTab.value = "Products";
    }
  },
  { immediate: true }
);

const currentTabComponent = computed(() => {
  switch (activeTab.value) {
    case "Analytics":
      return Analytics;
    case "Users":
      return Users;
    case "Products":
      return Products;
    case "Orders":
      return Orders;
    case "Reviews":
      return Reviews;
    case "Coupons":
      return Coupons;
    case "Conversations":
      return Conversations;
    default:
      return Products;
  }
});
</script>

<template>
  <div class="dashboard-layout">
    <!-- Mobile/Tablet Select Menu -->
    <div class="mobile-nav-select">
      <div class="nav-select-wrapper">
        <div
          class="nav-select-icon"
          :class="`nav-icon-${activeTab.toLowerCase()}`"
        ></div>
        <select
          v-model="activeTab"
          class="nav-select"
          aria-label="Select dashboard section"
        >
          <option v-for="tab in tabs" :key="tab" :value="tab">
            {{ tab }}
          </option>
        </select>
        <div class="nav-select-arrow">
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
            <path d="m6 9 6 6 6-6" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Desktop Sidebar -->
    <aside class="sidebar glass-card" aria-label="Dashboard navigation">
      <nav class="sidebar-nav">
        <a
          v-for="tab in tabs"
          :key="tab"
          href="#"
          @click.prevent="activeTab = tab"
          class="nav-item"
          :class="{ active: activeTab === tab }"
          :aria-current="activeTab === tab ? 'page' : undefined"
        >
          <div
            class="nav-icon"
            :class="`nav-icon-${tab.toLowerCase()}`"
            aria-hidden="true"
          ></div>
          {{ tab }}
        </a>
      </nav>
      <div class="sidebar-footer">
        <button
          @click="router.push('/')"
          class="btn btn-outline w-100 mb-2 gap-2"
          aria-label="Return to home page"
        >
          <div
            class="icon-sm bg-foreground nav-icon-home"
            aria-hidden="true"
          ></div>
          Back to Home
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <component :is="currentTabComponent" />
    </main>

    <!-- Toast Notifications -->
    <Toast />
  </div>
</template>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: calc(100vh - 60px);
  background-color: var(--background);
  color: var(--foreground);
  border-top: 1px solid var(--border);
  border-top-color: var(--border);
}

.mobile-nav-select {
  display: none;
  width: 100%;
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--background);
  position: static;
  z-index: var(--z-sticky);
}

.nav-select-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
}

.nav-select-icon {
  position: absolute;
  left: var(--spacing-sm);
  width: var(--spacing-md);
  height: var(--spacing-md);
  background-color: var(--foreground);
  -webkit-mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
  pointer-events: none;
  z-index: 1;
}

.nav-icon-analytics {
  -webkit-mask-image: url("/icons/dashboard.svg");
  mask-image: url("/icons/dashboard.svg");
}

.nav-icon-users {
  -webkit-mask-image: url("/icons/user.svg");
  mask-image: url("/icons/user.svg");
}

.nav-icon-products {
  -webkit-mask-image: url("/icons/packages.svg");
  mask-image: url("/icons/packages.svg");
}

.nav-icon-orders {
  -webkit-mask-image: url("/icons/cart.svg");
  mask-image: url("/icons/cart.svg");
}

.nav-icon-reviews {
  -webkit-mask-image: url("/icons/write.svg");
  mask-image: url("/icons/write.svg");
}

.nav-icon-coupons {
  -webkit-mask-image: url("/icons/discount.svg");
  mask-image: url("/icons/discount.svg");
}

.nav-icon-conversations {
  -webkit-mask-image: url("/icons/chatbot.svg");
  mask-image: url("/icons/chatbot.svg");
}

.nav-icon-home {
  -webkit-mask-image: url("/icons/home.svg");
  mask-image: url("/icons/home.svg");
}

.nav-select {
  width: 100%;
  height: 2.625rem;
  padding: 0 calc(var(--spacing-xl) + var(--spacing-md)) 0
    calc(var(--spacing-xl) + var(--spacing-md));
  border: 1px solid var(--border);
  background-color: var(--background);
  color: var(--foreground);
  font-size: var(--text-sm);
  font-weight: 500;
  border-radius: var(--radius);
  appearance: none;
  background-image: none;
  cursor: pointer;
  transition: all var(--transition-base);
}

.nav-select:hover {
  border-color: var(--muted-foreground);
}

.nav-select:focus {
  outline: none;
  border-color: var(--ring);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--ring), transparent 50%);
}

.nav-select-arrow {
  position: absolute;
  right: var(--spacing-sm);
  width: var(--spacing-md);
  height: var(--spacing-md);
  color: var(--muted-foreground);
  pointer-events: none;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar {
  width: 250px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-radius: 0;
  border-left: none;
  border-top: none;
  border-bottom: none;
  border-right: 1px solid var(--border);
  z-index: var(--z-sticky);
  position: sticky;
  top: 60px;
  height: calc(100vh - 60px);
}

.sidebar-nav {
  flex: 1;
  padding: var(--spacing-md) 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  color: var(--muted-foreground);
  text-decoration: none;
  font-weight: 500;
  transition: all var(--transition-base);
  border-left: 3px solid transparent;
}

.nav-item:hover {
  color: var(--foreground);
  background-color: var(--secondary);
}

.nav-item.active {
  color: var(--primary);
  background-color: var(--accent);
  border-left-color: var(--primary);
}

.nav-icon {
  width: var(--spacing-md);
  height: var(--spacing-md);
  background-color: var(--muted-foreground);
  -webkit-mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
  transition: background-color var(--transition-base);
}

.nav-item:hover .nav-icon {
  background-color: var(--foreground);
}

.nav-item.active .nav-icon {
  background-color: var(--primary);
}

.sidebar-footer {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border);
}

.icon-sm {
  width: var(--spacing-md);
  height: var(--spacing-md);
  -webkit-mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
}

.bg-foreground {
  background-color: var(--foreground);
}

.main-content {
  flex: 1;
  padding: var(--spacing-xl);
  overflow-y: auto;
  min-width: 0;
}

@media (max-width: 1023px) {
  .mobile-nav-select {
    display: block;
  }

  .sidebar {
    display: none;
  }

  .dashboard-layout {
    flex-direction: column;
  }

  .main-content {
    padding: var(--spacing-md) var(--spacing-lg);
  }
}

@media (max-width: 767px) {
  .main-content {
    padding: var(--spacing-md) var(--spacing-lg);
  }
}
</style>
