<script setup>
import { ref, watch, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import Skeleton from "../../components/Skeleton.vue";

const router = useRouter();
const route = useRoute();
const news = ref([]);
const loading = ref(false);
const error = ref(null);

// Initialize state from URL
const searchQuery = ref(route.query.search || "");
const sortBy = ref(route.query.sort_by || "recent");
const startDate = ref(route.query.start_date || "");
const endDate = ref(route.query.end_date || "");
const page = ref(parseInt(route.query.page) || 1);

const pageSize = 6;
const totalPages = ref(0);
const totalCount = ref(0);

const fetchNews = async () => {
  loading.value = true;
  error.value = null;
  try {
    const params = new URLSearchParams({
      skip: (page.value - 1) * pageSize,
      limit: pageSize,
      sort_by: sortBy.value,
    });

    if (searchQuery.value) params.append("search", searchQuery.value);
    if (startDate.value) params.append("start_date", startDate.value);
    if (endDate.value) params.append("end_date", endDate.value);

    const response = await fetch(
      `http://localhost:8000/news?${params.toString()}`
    );

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    const data = await response.json();
    news.value = data.items;
    totalPages.value = data.total_pages;
    totalCount.value = data.total;
  } catch (err) {
    console.error("Failed to fetch news:", err);
    error.value = "Failed to load news. Please try again later.";
  } finally {
    loading.value = false;
  }
};

const updateURL = () => {
  const query = {
    page: page.value,
    sort_by: sortBy.value,
  };
  if (searchQuery.value) query.search = searchQuery.value;
  if (startDate.value) query.start_date = startDate.value;
  if (endDate.value) query.end_date = endDate.value;

  // Use replace to avoid polluting history for every small change,
  // or push for significant ones?
  // Let's use push for pagination to allow "Back" to work.
  // But for typing search, replace is better.
  router.push({ query }).catch(() => {});
};

// Watchers
let debounceTimeout;
watch(searchQuery, () => {
  clearTimeout(debounceTimeout);
  debounceTimeout = setTimeout(() => {
    page.value = 1;
    updateURL();
    fetchNews();
  }, 500);
});

watch([sortBy, startDate, endDate], () => {
  page.value = 1;
  updateURL();
  fetchNews();
});

watch(page, () => {
  updateURL();
  fetchNews();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// Sync from URL (Handling Back/Forward)
watch(
  () => route.query,
  (newQuery) => {
    const newPage = parseInt(newQuery.page) || 1;
    if (page.value !== newPage) {
      page.value = newPage;
      // fetchNews will be triggered by page watcher
    }

    // Handle other params if needed (e.g. shared link)
    if (newQuery.sort_by && newQuery.sort_by !== sortBy.value) {
      sortBy.value = newQuery.sort_by;
    }
    // ... similarly for others
  }
);

onMounted(() => {
  fetchNews();
});

const navigateToNewsDetails = (id) => {
  router.push({ name: "NewsDetails", params: { id } });
};

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
</script>

<template>
  <div class="news-page container">
    <h1 class="page-title mb-5">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="title-icon"
      >
        <path
          d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"
        />
        <path d="M18 14h-8" />
        <path d="M15 18h-5" />
        <path d="M10 6h8v4h-8V6Z" />
      </svg>
      News
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
          placeholder="Search by title, content, category..."
          class="form-input"
          aria-label="Search news articles"
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
          <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
        </svg>
        <select
          v-model="sortBy"
          class="form-select"
          aria-label="Sort news articles"
        >
          <option value="recent">Most Recent</option>
          <option value="oldest">Oldest</option>
        </select>
      </div>

      <!-- Date Range Start -->
      <div class="date-input-wrapper">
        <label class="date-label">Start Date</label>
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
          class="date-icon"
        >
          <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
          <line x1="16" x2="16" y1="2" y2="6" />
          <line x1="8" x2="8" y1="2" y2="6" />
          <line x1="3" x2="21" y1="10" y2="10" />
        </svg>
        <input
          v-model="startDate"
          type="date"
          class="form-input date-input"
          aria-label="Start Date"
        />
      </div>

      <!-- Date Range End -->
      <div class="date-input-wrapper">
        <label class="date-label">End Date</label>
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
          class="date-icon"
        >
          <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
          <line x1="16" x2="16" y1="2" y2="6" />
          <line x1="8" x2="8" y1="2" y2="6" />
          <line x1="3" x2="21" y1="10" y2="10" />
        </svg>
        <input
          v-model="endDate"
          type="date"
          class="form-input date-input"
          aria-label="End Date"
        />
      </div>
    </div>

    <!-- Loading/Error -->
    <div v-if="loading" class="news-grid">
      <div v-for="n in pageSize" :key="n" class="news-card glass-card">
        <div class="card-image">
          <Skeleton class="w-full h-full" />
        </div>
        <div class="card-content">
          <div class="flex justify-between mb-2">
            <Skeleton class="w-1/3 h-4" />
            <Skeleton class="w-1/4 h-4" />
          </div>
          <Skeleton class="w-3/4 h-6 mb-4" />
          <Skeleton class="w-full h-16" />
        </div>
      </div>
    </div>
    <div v-else-if="error" class="text-center py-5 text-danger">
      {{ error }}
    </div>

    <!-- Grid -->
    <div v-else class="news-grid">
      <article
        v-for="item in news"
        :key="item.id"
        class="news-card glass-card"
        @click="navigateToNewsDetails(item.id)"
      >
        <div class="card-image">
          <img
            :src="item.image_url || '/images/default-news.webp'"
            :alt="item.title"
            loading="lazy"
            @error="
              $event.target.src =
                'https://placehold.co/600x400/1a1a1a/FFF?text=News'
            "
          />
        </div>
        <div class="card-content">
          <div class="card-meta">
            <span class="date">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
                <line x1="16" x2="16" y1="2" y2="6" />
                <line x1="8" x2="8" y1="2" y2="6" />
                <line x1="3" x2="21" y1="10" y2="10" />
              </svg>
              {{ new Date(item.published_date).toLocaleDateString() }}
            </span>
            <span v-if="item.category" class="category">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path
                  d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z"
                />
                <path d="M7 7h.01" />
              </svg>
              {{ item.category }}
            </span>
          </div>
          <h3 class="card-title">
            {{ item.title }}
          </h3>
          <p class="card-excerpt">
            {{
              item.summary ||
              (item.content ? item.content.substring(0, 120) + "..." : "")
            }}
          </p>
        </div>
      </article>
    </div>

    <!-- Empty State -->
    <div
      v-if="!loading && !error && news.length === 0"
      class="text-center py-5 text-muted"
    >
      No news articles found matching your criteria.
    </div>

    <!-- Pagination -->
    <div
      class="pagination mt-5 d-flex justify-content-center gap-2 fade-in-up-fast delay-300-fast"
      v-if="news.length > 0 || page > 1"
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
.news-page {
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
  margin-bottom: var(--spacing-lg) !important;
}

.title-icon {
  width: 48px;
  height: 48px;
  color: var(--primary);
  stroke: var(--primary);
}

@media (max-width: 1024px) {
  .page-title {
    font-size: var(--text-3xl);
    margin-bottom: var(--spacing-md) !important;
  }

  .title-icon {
    width: 32px;
    height: 32px;
  }
}

@media (max-width: 640px) {
  .page-title {
    font-size: var(--text-2xl);
    margin-bottom: var(--spacing-md) !important;
  }

  .title-icon {
    width: 24px;
    height: 24px;
  }
}

.filters-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: var(--spacing-md);
  align-items: center;
}

@media (max-width: 1024px) {
  .filters-row {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 640px) {
  .filters-row {
    grid-template-columns: 1fr;
  }
}

.search-box {
  position: relative;
  width: 100%;
}

.search-box .form-input {
  width: 100%;
  padding-left: 2.5rem;
}

.search-box .search-icon {
  position: absolute;
  left: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted-foreground);
  pointer-events: none;
  display: flex;
  z-index: 1;
}

.select-with-icon {
  position: relative;
  width: 100%;
}

.select-with-icon .select-icon {
  position: absolute;
  left: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted-foreground);
  pointer-events: none;
  z-index: 1;
}

.select-with-icon .form-select {
  width: 100%;
  padding-left: 2.5rem;
}

.date-input-wrapper {
  position: relative;
  width: 100%;
}

.date-input-wrapper .date-label {
  position: absolute;
  left: 0.75rem;
  top: -0.65rem;
  background: var(--background);
  padding: 0 0.25rem;
  font-size: var(--text-xs);
  color: var(--muted-foreground);
  font-family: var(--font-sans);
  z-index: 2;
}

.date-input-wrapper .date-icon {
  position: absolute;
  left: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted-foreground);
  pointer-events: none;
  z-index: 1;
}

.date-input-wrapper .date-input {
  width: 100%;
  padding-left: 2.5rem;
}

.filter-controls {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  align-items: center;
}

.form-input,
.form-select {
  background: color-mix(in srgb, var(--background), transparent 50%);
  border: 1px solid var(--border);
  color: var(--foreground);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius);
  outline: none;
  font-family: var(--font-sans);
  transition: all var(--transition-base);
  font-size: var(--text-sm);
}

.form-input:focus,
.form-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary), transparent 80%);
}

.news-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-xl);
}

@media (min-width: 768px) {
  .news-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .news-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.news-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform var(--transition-slow) ease,
    box-shadow var(--transition-slow) ease,
    border-color var(--transition-slow) ease;
  height: 100%;
  cursor: pointer;
}

.news-card:hover {
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

.news-card:hover .card-image img {
  transform: scale(1.05);
}

.card-content {
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  flex: 1;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--text-sm);
  color: var(--muted-foreground);
  margin-bottom: var(--spacing-sm);
  font-family: var(--font-mono);
}

.card-meta .date,
.card-meta .category {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.card-meta svg {
  flex-shrink: 0;
}

.card-title {
  font-size: var(--text-xl);
  margin-bottom: var(--spacing-lg);
  line-height: 1.4;
  font-weight: 600;
  color: var(--foreground);
}

.card-excerpt {
  font-size: var(--text-sm);
  color: var(--muted-foreground);
  margin-bottom: 0;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

input[type="date"]::-webkit-calendar-picker-indicator {
  filter: invert(1);
  opacity: var(--opacity-hover);
  cursor: pointer;
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
