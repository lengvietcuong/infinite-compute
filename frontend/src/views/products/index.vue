<script setup>
import { ref, watch, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { formatPrice } from "../../utils/format";
import Skeleton from "../../components/Skeleton.vue";
import { API_BASE_URL } from "@/config/api";

const router = useRouter();
const route = useRoute();
const products = ref([]);
const loading = ref(false);
const error = ref(null);

const searchQuery = ref(route.query.search || "");
const sortBy = ref(route.query.sort_by || "latest");

const page = ref(parseInt(route.query.page) || 1);
const pageSize = 12;
const totalProducts = ref(0);
const allFetchedProducts = ref([]);

const filteredAndSortedProducts = computed(() => {
  let result = [...allFetchedProducts.value];

  switch (sortBy.value) {
    case "price_asc":
      result.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
      break;
    case "price_desc":
      result.sort((a, b) => parseFloat(b.price) - parseFloat(a.price));
      break;
    case "most_reviews":
      result.sort((a, b) => (b.review_count || 0) - (a.review_count || 0));
      break;
    case "latest":
    default:
      // Handle potential missing dates safely
      result.sort((a, b) => {
        const dateA = a.created_at ? new Date(a.created_at) : new Date(0);
        const dateB = b.created_at ? new Date(b.created_at) : new Date(0);
        return dateB - dateA;
      });
      break;
  }
  return result;
});

const paginatedProducts = computed(() => {
  const start = (page.value - 1) * pageSize;
  const end = start + pageSize;
  return filteredAndSortedProducts.value.slice(start, end);
});

const totalPages = computed(
  () => Math.ceil(filteredAndSortedProducts.value.length / pageSize) || 1
);

const fetchProducts = async () => {
  loading.value = true;
  error.value = null;
  try {
    const params = new URLSearchParams({
      skip: 0,
      limit: 100,
    });

    if (searchQuery.value) params.append("search", searchQuery.value);

    const response = await fetch(
      `${API_BASE_URL}/products?${params.toString()}`
    );

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    const data = await response.json();
    allFetchedProducts.value = data;
    totalProducts.value = data.length;
  } catch (err) {
    console.error("Failed to fetch products:", err);
    error.value = "Failed to load products. Please try again later.";
  } finally {
    loading.value = false;
  }
};

// URL Syncing
const updateURL = () => {
  const query = {
    page: page.value,
    sort_by: sortBy.value,
  };
  if (searchQuery.value) {
    query.search = searchQuery.value;
  }
  router.replace({ query }).catch(() => {});
};

// Watchers
watch(searchQuery, () => {
  page.value = 1; // Reset to page 1 on search
  // Debounce fetch handled by separate watcher or logic if needed,
  // but here we just fetch immediately or via debounced function.
  debouncedFetch();
});

let timeout;
const debouncedFetch = () => {
  clearTimeout(timeout);
  timeout = setTimeout(() => {
    updateURL();
    fetchProducts();
  }, 500);
};

watch(sortBy, () => {
  page.value = 1;
  updateURL();
});

watch(page, () => {
  updateURL();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// React to route changes (Back/Forward buttons)
watch(
  () => route.query,
  (newQuery) => {
    const newPage = parseInt(newQuery.page) || 1;
    if (page.value !== newPage) {
      page.value = newPage;
    }

    if (newQuery.search !== searchQuery.value) {
      searchQuery.value = newQuery.search || "";
      // Fetch will be triggered by searchQuery watcher?
      // No, searchQuery watcher calls debouncedFetch.
      // But if it comes from URL, we might want immediate fetch?
      // Let's rely on searchQuery watcher for now.
    }

    if (newQuery.sort_by !== sortBy.value && newQuery.sort_by) {
      sortBy.value = newQuery.sort_by;
    }
  }
);

onMounted(() => {
  // Initial fetch
  fetchProducts();
});

const goToFirstPage = () => {
  if (page.value !== 1) page.value = 1;
};

const goToLastPage = () => {
  if (page.value !== totalPages.value) page.value = totalPages.value;
};

const nextPage = () => {
  if (page.value < totalPages.value) page.value++;
};

const prevPage = () => {
  if (page.value > 1) page.value--;
};

const navigateToProduct = (id) => {
  router.push(`/products/${id}`);
};
</script>

<template>
  <div class="products-page container">
    <h1 class="page-title mb-4">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="48"
        height="48"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="title-icon"
      >
        <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7" />
        <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" />
        <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4" />
        <path d="M2 7h20" />
        <path
          d="M22 7v3a2 2 0 0 1-2 2v0a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12v0a2 2 0 0 1-2-2V7"
        />
      </svg>
      Products
    </h1>

    <!-- Filters -->
    <div class="filters-row mb-5">
      <!-- Search -->
      <div class="search-box">
        <span class="search-icon">
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
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.3-4.3" />
          </svg>
        </span>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search products..."
          class="form-input"
          aria-label="Search products"
        />
      </div>

      <!-- Sort -->
      <div class="select-with-icon">
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
          class="select-icon"
        >
          <path d="m3 16 4 4 4-4" />
          <path d="M7 20V4" />
          <path d="m21 8-4-4-4 4" />
          <path d="M17 4v16" />
        </svg>
        <select v-model="sortBy" class="form-select" aria-label="Sort products">
          <option value="latest">Newest</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
          <option value="most_reviews">Most Reviews</option>
        </select>
      </div>
    </div>

    <!-- Loading/Error -->
    <div v-if="loading" class="products-grid">
      <div v-for="n in pageSize" :key="n" class="product-card glass-card">
        <div class="card-image">
          <Skeleton class="w-full h-full" />
        </div>
        <div class="card-content">
          <div class="flex justify-between mb-2">
            <Skeleton class="w-1/3 h-4" />
            <Skeleton class="w-1/4 h-4" />
          </div>
          <Skeleton class="w-3/4 h-6 mb-2" />
          <Skeleton class="w-full h-12" />
        </div>
      </div>
    </div>
    <div v-else-if="error" class="text-center py-5 text-danger">
      {{ error }}
    </div>

    <!-- Grid -->
    <div v-else class="products-grid">
      <article
        v-for="product in paginatedProducts"
        :key="product.id"
        class="product-card glass-card"
        @click="navigateToProduct(product.id)"
      >
        <div class="card-image">
          <img
            :src="product.image_url || '/images/default-product.webp'"
            :alt="product.name"
            loading="lazy"
            @error="
              $event.target.src =
                'https://placehold.co/600x400/1a1a1a/FFF?text=Product'
            "
          />
          <div class="price-tag">${{ formatPrice(product.price) }}</div>
        </div>
        <div class="card-content">
          <div class="card-meta">
            <span class="architecture" v-if="product.architecture">
              {{ product.architecture }}
            </span>
            <span class="rating" v-if="product.average_rating">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="currentColor"
                stroke="none"
                class="text-warning"
              >
                <polygon
                  points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
                />
              </svg>
              {{ product.average_rating.toFixed(1) }} ({{
                product.review_count
              }})
            </span>
          </div>
          <h3 class="card-title">{{ product.name }}</h3>
          <p class="card-excerpt">
            {{
              product.description
                ? product.description.substring(0, 80) + "..."
                : ""
            }}
          </p>
        </div>
      </article>
    </div>

    <!-- Empty State -->
    <div
      v-if="!loading && !error && allFetchedProducts.length === 0"
      class="text-center py-5 text-muted"
    >
      No products found matching your criteria.
    </div>

    <!-- Pagination -->
    <div
      class="pagination mt-5 d-flex justify-content-center gap-2"
      v-if="filteredAndSortedProducts.length > pageSize"
    >
      <button
        @click="goToFirstPage"
        :disabled="page === 1"
        class="btn-pagination"
        aria-label="Go to first page"
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
          <path d="m11 17-5-5 5-5" />
          <path d="m18 17-5-5 5-5" />
        </svg>
      </button>
      <button
        @click="prevPage"
        :disabled="page === 1"
        class="btn-pagination"
        aria-label="Go to previous page"
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
          <path d="m15 18-6-6 6-6" />
        </svg>
      </button>
      <span class="d-flex align-items-center font-mono text-muted"
        >Page {{ page }}/{{ totalPages }}</span
      >
      <button
        @click="nextPage"
        :disabled="page >= totalPages"
        class="btn-pagination"
        aria-label="Go to next page"
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
          <path d="m9 18 6-6-6-6" />
        </svg>
      </button>
      <button
        @click="goToLastPage"
        :disabled="page >= totalPages"
        class="btn-pagination"
        aria-label="Go to last page"
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
          <path d="m6 17 5-5-5-5" />
          <path d="m13 17 5-5-5-5" />
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.products-page {
  padding-top: var(--spacing-xl);
  padding-bottom: var(--spacing-2xl);
}

.page-title {
  font-size: var(--text-5xl);
  text-align: center;
  color: var(--foreground);
  font-family: var(--font-mono);
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
}

.title-icon {
  width: 48px;
  height: 48px;
  color: var(--primary);
  stroke: var(--primary);
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

.filters-row {
  display: grid;
  grid-template-columns: 300px 180px;
  gap: var(--spacing-md);
  align-items: center;
  justify-content: center;
  max-width: 800px;
  margin: 0 auto 3rem auto;
}

@media (max-width: 640px) {
  .filters-row {
    grid-template-columns: 1fr 1fr;
  }
}

.search-box,
.select-with-icon {
  position: relative;
  width: 100%;
}

.form-input,
.form-select {
  width: 100%;
  padding-left: 2.5rem;
  background: color-mix(in srgb, var(--background), transparent 50%);
  border: 1px solid var(--border);
  color: var(--foreground);
  padding-top: var(--spacing-sm);
  padding-bottom: var(--spacing-sm);
  padding-right: var(--spacing-md);
  border-radius: var(--radius);
  outline: none;
  font-family: var(--font-sans);
  transition: all var(--transition-base);
  font-size: var(--text-sm);
}

.search-icon,
.select-icon {
  position: absolute;
  left: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted-foreground);
  pointer-events: none;
  z-index: 1;
}

.form-input:focus,
.form-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary), transparent 80%);
}

.products-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-lg);
}

@media (min-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .products-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.product-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform var(--transition-slow) ease,
    box-shadow var(--transition-slow) ease,
    border-color var(--transition-slow) ease;
  height: 100%;
  cursor: pointer;
  background: color-mix(in srgb, var(--card), transparent 80%);
  border: 1px solid var(--border);
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-xl);
  border-color: var(--primary);
}

.card-image {
  position: relative;
  height: 200px;
  overflow: hidden;
  background-color: var(--card);
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slower) ease;
}

.product-card:hover .card-image img {
  transform: scale(1.05);
}

.price-tag {
  position: absolute;
  bottom: var(--spacing-sm);
  right: var(--spacing-sm);
  background: var(--primary);
  color: var(--primary-foreground);
  padding: var(--spacing-xs) var(--spacing-sm);
  font-weight: 700;
  font-family: var(--font-mono);
  border-radius: var(--radius);
  font-size: var(--text-sm);
}

.card-content {
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  flex: 1;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 0.75rem;
  color: var(--muted-foreground);
  margin-bottom: var(--spacing-sm);
  font-family: var(--font-mono);
}

.rating {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.text-warning {
  color: var(--destructive);
}

.card-title {
  font-size: var(--text-lg);
  margin-bottom: var(--spacing-sm);
  line-height: 1.3;
  font-weight: 600;
  color: var(--foreground);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-excerpt {
  font-size: var(--text-sm);
  color: var(--muted-foreground);
  margin-bottom: var(--spacing-md);
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.btn-pagination {
  width: 40px;
  height: 40px;
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

.btn-pagination svg {
  flex-shrink: 0;
}
</style>
