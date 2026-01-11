<script setup>
import { ref, watch, onMounted, computed } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const products = ref([]);
const loading = ref(false);
const error = ref(null);

// Filters
const searchQuery = ref("");
const sortBy = ref("latest"); // latest, price_asc, price_desc, most_reviews

// Pagination (User asked for specific grid dimensions which implies 12 items per page: 4x3=12, 3x4=12, 2x6=12)
const page = ref(1);
const pageSize = 12;
const totalProducts = ref(0);

// Computed property for sorted products
// Note: We fetch 'all' (or a large batch) and sort client-side because backend only supports creation_date sort
// However, if we paginate server-side, we can only sort by creation date server-side.
// To support "Price" and "Reviews" sorting with pagination correctly, we need backend support.
// As per instructions "Scan backend... then implement", and "Avoid overly complicated... logic",
// I will fetch a larger batch (e.g. 100) and do client-side pagination and sorting for the best UX without modifying backend deeply yet.
// If the user meant "Show ALL products", fetching 100 is reasonable for a start.
const allFetchedProducts = ref([]);

const filteredAndSortedProducts = computed(() => {
  let result = [...allFetchedProducts.value];

  // Search is handled by API usually, but if we do client-side:
  // API has 'search' param, so we use that during fetch.

  // Client-side Sorting
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
      // Assuming default API order is latest, or we sort by ID/date if available
      // API returns "order_by(Product.created_at.desc())"
      // So default fetch is already latest.
      // If we re-sort:
      result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      break;
  }
  return result;
});

const paginatedProducts = computed(() => {
  const start = (page.value - 1) * pageSize;
  const end = start + pageSize;
  return filteredAndSortedProducts.value.slice(start, end);
});

const totalPages = computed(() =>
  Math.ceil(filteredAndSortedProducts.value.length / pageSize)
);

const fetchProducts = async () => {
  loading.value = true;
  error.value = null;
  try {
    const params = new URLSearchParams({
      skip: 0,
      limit: 100, // Fetch up to 100 to allow client-side sorting
    });

    if (searchQuery.value) params.append("search", searchQuery.value);

    // Note: We are not using backend pagination (skip/limit) for the view pages,
    // but for the initial data load to enable client-side sorting.
    const response = await fetch(
      `http://localhost:8000/products?${params.toString()}`
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

// Debounce search
let timeout;
const debouncedFetch = () => {
  page.value = 1;
  clearTimeout(timeout);
  timeout = setTimeout(fetchProducts, 500);
};

watch(searchQuery, debouncedFetch);

// Reset page when sort changes
watch(sortBy, () => {
  page.value = 1;
});

onMounted(fetchProducts);

const nextPage = () => {
  if (page.value < totalPages.value) {
    window.scrollTo({ top: 0, behavior: "smooth" });
    page.value++;
  }
};

const prevPage = () => {
  if (page.value > 1) {
    window.scrollTo({ top: 0, behavior: "smooth" });
    page.value--;
  }
};

const navigateToProduct = (id) => {
  router.push(`/products/${id}`);
};

const formatPrice = (price) => {
  return parseFloat(price).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};
</script>

<template>
  <div class="products-page container">
    <h1 class="page-title mb-4 fade-in-up">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="48"
        height="48"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
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
    <div class="filters-row mb-5 fade-in-up delay-100">
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
        <select v-model="sortBy" class="form-select">
          <option value="latest">Newest</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
          <option value="most_reviews">Most Reviews</option>
        </select>
      </div>
    </div>

    <!-- Loading/Error -->
    <div
      v-if="loading && allFetchedProducts.length === 0"
      class="text-center py-5"
    >
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="error" class="text-center py-5 text-danger">
      {{ error }}
    </div>

    <!-- Grid -->
    <div v-else class="products-grid fade-in-up delay-200">
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
      class="text-center py-5 text-muted fade-in-up"
    >
      No products found matching your criteria.
    </div>

    <!-- Pagination -->
    <div
      class="pagination mt-5 d-flex justify-content-center gap-3 fade-in-up delay-300"
      v-if="filteredAndSortedProducts.length > pageSize"
    >
      <button
        @click="prevPage"
        :disabled="page === 1"
        class="btn btn-outline btn-sm"
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
        Previous
      </button>
      <span class="d-flex align-items-center font-mono text-muted"
        >Page {{ page }}/{{ totalPages }}</span
      >
      <button
        @click="nextPage"
        :disabled="page >= totalPages"
        class="btn btn-outline btn-sm"
      >
        Next
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
    </div>
  </div>
</template>

<style scoped>
.products-page {
  padding-top: 2rem;
  padding-bottom: 4rem;
}

.page-title {
  font-size: 3rem;
  text-align: center;
  color: var(--foreground);
  font-family: var(--font-mono);
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.title-icon {
  width: 48px;
  height: 48px;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .title-icon {
    width: 32px;
    height: 32px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.5rem;
  }

  .title-icon {
    width: 28px;
    height: 28px;
  }
}

.filters-row {
  display: grid;
  grid-template-columns: 300px 180px;
  gap: 1rem;
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
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  padding-right: 1rem;
  border-radius: var(--radius);
  outline: none;
  font-family: var(--font-sans);
  transition: all 0.2s;
  font-size: 0.9rem;
}

.search-icon,
.select-icon {
  position: absolute;
  left: 1rem;
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

/* Products Grid - Specific Requirements */
.products-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
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
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  height: 100%;
  cursor: pointer;
  background: color-mix(in srgb, var(--card), transparent 80%);
  border: 1px solid var(--border);
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
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
  transition: transform 0.5s ease;
}

.product-card:hover .card-image img {
  transform: scale(1.05);
}

.price-tag {
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  background: var(--primary);
  color: var(--primary-foreground);
  padding: 0.25rem 0.5rem;
  font-weight: 700;
  font-family: var(--font-mono);
  border-radius: var(--radius);
  font-size: 0.9rem;
}

.card-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--muted-foreground);
  margin-bottom: 0.5rem;
  font-family: var(--font-mono);
}

.rating {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.text-warning {
  color: #f59e0b;
}

.card-title {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  line-height: 1.3;
  font-weight: 600;
  color: var(--foreground);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-excerpt {
  font-size: 0.85rem;
  color: var(--muted-foreground);
  margin-bottom: 1rem;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
