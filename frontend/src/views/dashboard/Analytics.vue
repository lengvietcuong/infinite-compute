<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from "vue";
import { useAuth } from "../../composables/useAuth";
import { formatPrice } from "../../utils/format";
import { API_BASE_URL } from "../../config/api";
import Skeleton from "../../components/Skeleton.vue";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "vue-chartjs";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const { user } = useAuth();
const analyticsData = ref(null);
const isLoading = ref(false);
const timeframe = ref("30d");
const timeframes = [
  { label: "Today", value: "today" },
  { label: "Last 7 Days", value: "7d" },
  { label: "Last 30 Days", value: "30d" },
  { label: "Last 90 Days", value: "90d" },
  { label: "Last 365 Days", value: "365d" },
  { label: "All Time", value: "all" },
];

const getPrimaryColor = () => {
  return getComputedStyle(document.documentElement)
    .getPropertyValue("--primary")
    .trim();
};

const chartData = computed(() => {
  if (!analyticsData.value?.sales_performance) return null;

  const data = analyticsData.value.sales_performance;
  const labels = data.map((item) => {
    const date = new Date(item.date);
    return timeframe.value === "today"
      ? date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      : date.toLocaleDateString();
  });

  const primaryColor = getPrimaryColor();

  return {
    labels,
    datasets: [
      {
        label: "Revenue",
        data: data.map((item) => item.revenue),
        borderColor: primaryColor,
        backgroundColor: primaryColor + "1A",
        yAxisID: "y",
        tension: 0.4,
      },
    ],
  };
});

const getComputedColor = (variable) => {
  return getComputedStyle(document.documentElement)
    .getPropertyValue(variable)
    .trim();
};

const getComputedFontSize = (variable) => {
  const remValue = getComputedStyle(document.documentElement)
    .getPropertyValue(variable)
    .trim();
  return parseInt(remValue.replace("rem", "")) * 16;
};

const isLightMode = ref(document.body.classList.contains("light-mode"));

const updateTheme = () => {
  isLightMode.value = document.body.classList.contains("light-mode");
};

let themeObserver = null;

onMounted(() => {
  themeObserver = new MutationObserver(updateTheme);
  themeObserver.observe(document.body, {
    attributes: true,
    attributeFilter: ["class"],
  });
});

onUnmounted(() => {
  if (themeObserver) {
    themeObserver.disconnect();
  }
});

const chartOptions = computed(() => {
  const mutedForeground = getComputedColor("--muted-foreground");
  const borderColor = getComputedColor("--border");
  const fontSize = getComputedFontSize("--text-sm");

  const gridLineColor = isLightMode.value ? "rgba(0, 0, 0, 0.15)" : borderColor;

  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: "index",
      intersect: false,
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            let label = context.dataset.label || "";
            if (label) {
              label += ": ";
            }
            if (context.parsed.y !== null) {
              label += formatPrice(context.parsed.y);
            }
            return label;
          },
        },
      },
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: timeframe.value === "today" ? "Time" : "Date",
          color: mutedForeground,
          font: {
            size: fontSize,
          },
        },
        grid: {
          color: gridLineColor,
          drawBorder: true,
          borderColor: borderColor,
        },
        ticks: {
          color: mutedForeground,
          maxRotation: 45,
          minRotation: 0,
        },
        border: {
          color: borderColor,
        },
      },
      y: {
        type: "linear",
        display: true,
        position: "left",
        title: {
          display: true,
          text: "Revenue (USD)",
          color: mutedForeground,
          font: {
            size: fontSize,
          },
        },
        grid: {
          color: gridLineColor,
          drawBorder: true,
          borderColor: borderColor,
        },
        ticks: {
          color: mutedForeground,
          callback: (value) => formatPrice(value),
          maxTicksLimit: 8,
        },
        border: {
          color: borderColor,
        },
      },
    },
  };
});

const fetchAnalytics = async () => {
  if (user.value?.role !== "admin") return;
  isLoading.value = true;
  try {
    const token = localStorage.getItem("token");
    const response = await fetch(
      `${API_BASE_URL}/analytics?timeframe=${timeframe.value}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.ok) {
      analyticsData.value = await response.json();
    }
  } catch (error) {
    console.error("Failed to fetch analytics:", error);
  } finally {
    isLoading.value = false;
  }
};

watch(timeframe, () => {
  fetchAnalytics();
});

onMounted(() => {
  fetchAnalytics();
});

const getProgressValue = (value, total) => {
  if (!total) return 0;
  return Math.min((value / total) * 100, 100);
};

const totalUnits = computed(() => {
  if (!analyticsData.value?.top_products_units) return 0;
  return analyticsData.value.top_products_units.reduce(
    (acc, curr) => acc + curr.units_sold,
    0
  );
});
</script>

<template>
  <div class="analytics-content">
    <header
      class="main-header mb-6 d-flex justify-content-between align-items-center"
    >
      <h1 class="h3 m-0 text-2xl font-bold tracking-tight">Analytics</h1>
      <!-- Timeframe Filter -->
      <select
        v-model="timeframe"
        class="form-select w-auto timeframe-select border bg-transparent px-3 py-2 text-sm shadow-sm"
        aria-label="Select timeframe"
      >
        <option
          v-for="opt in timeframes"
          :key="opt.value"
          :value="opt.value"
          class="bg-popover text-popover-foreground"
        >
          {{ opt.label }}
        </option>
      </select>
    </header>

    <div class="kpi-grid kpi-grid-spacing">
      <div>
        <div class="glass-card p-4 kpi-card">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <p class="text-sm font-medium text-muted-foreground mb-1">
                Total Revenue
              </p>
              <h3 v-if="!isLoading" class="text-2xl font-bold">
                ${{ formatPrice(analyticsData?.revenue || 0) }}
              </h3>
              <Skeleton v-else class="h-8 w-32" />
            </div>
            <div class="kpi-icon kpi-icon-dollar" aria-hidden="true"></div>
          </div>
        </div>
      </div>
      <div>
        <div class="glass-card p-4 kpi-card">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <p class="text-sm font-medium text-muted-foreground mb-1">
                Total Orders
              </p>
              <h3 v-if="!isLoading" class="text-2xl font-bold">
                {{ analyticsData?.total_orders || 0 }}
              </h3>
              <Skeleton v-else class="h-8 w-24" />
            </div>
            <div class="kpi-icon kpi-icon-packages" aria-hidden="true"></div>
          </div>
        </div>
      </div>
      <div>
        <div class="glass-card p-4 kpi-card">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <p class="text-sm font-medium text-muted-foreground mb-1">
                Avg. Order Value
              </p>
              <h3 v-if="!isLoading" class="text-2xl font-bold">
                ${{ formatPrice(analyticsData?.average_order_value || 0) }}
              </h3>
              <Skeleton v-else class="h-8 w-32" />
            </div>
            <div class="kpi-icon kpi-icon-order-value" aria-hidden="true"></div>
          </div>
        </div>
      </div>
      <div>
        <div class="glass-card p-4 kpi-card">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <p class="text-sm font-medium text-muted-foreground mb-1">
                Total Units
              </p>
              <h3 v-if="!isLoading" class="text-2xl font-bold">
                {{ totalUnits }}
              </h3>
              <Skeleton v-else class="h-8 w-24" />
            </div>
            <div class="kpi-icon kpi-icon-receipt" aria-hidden="true"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Chart -->
    <div class="glass-card p-4 mb-4 chart-container">
      <h3 class="text-lg font-semibold mb-4">Sales Performance</h3>
      <div class="chart-wrapper">
        <Line
          v-if="chartData && chartOptions && !isLoading"
          :data="chartData"
          :options="chartOptions"
        />
        <div v-else class="h-full flex flex-col gap-3 justify-center">
          <Skeleton class="h-6 w-full" />
          <Skeleton class="h-6 w-full" />
          <Skeleton class="h-6 w-full" />
          <Skeleton class="h-6 w-full" />
          <Skeleton class="h-6 w-full" />
          <Skeleton class="h-6 w-full" />
        </div>
      </div>
    </div>

    <!-- Top Products Lists -->
    <div class="products-grid">
      <!-- Top Products by Revenue -->
      <div>
        <div class="glass-card p-4 products-card">
          <h3 class="text-lg font-semibold mb-4">Top Products by Revenue</h3>
          <div class="table-container">
            <table class="w-full text-sm caption-bottom">
              <thead class="border-b border-border">
                <tr class="text-left font-medium text-muted-foreground">
                  <th class="h-10 px-2 align-middle">Product</th>
                  <th class="h-10 px-2 align-middle text-end">Revenue</th>
                </tr>
              </thead>
              <tbody class="[&_tr:last-child]:border-0">
                <tr
                  v-if="isLoading"
                  v-for="n in 5"
                  :key="'skeleton-revenue-' + n"
                  class="border-b border-border"
                >
                  <td class="p-2 align-middle">
                    <div class="flex items-center gap-3">
                      <Skeleton class="h-10 w-10" />
                      <div class="flex-1">
                        <Skeleton class="h-4 w-32 mb-2" />
                        <Skeleton class="h-1.5 w-full" />
                      </div>
                    </div>
                  </td>
                  <td class="p-2 align-middle text-end">
                    <Skeleton class="h-4 w-20 ml-auto" />
                  </td>
                </tr>
                <tr
                  v-if="!isLoading"
                  v-for="product in analyticsData?.top_products_revenue || []"
                  :key="product.product_id"
                  class="border-b border-border transition-colors hover:bg-muted/50"
                >
                  <td class="p-2 align-middle">
                    <div class="flex items-center gap-3">
                      <img
                        :src="product.image_url || '/placeholder.png'"
                        class="flex-shrink-0 product-image"
                        width="40"
                        height="40"
                        :alt="product.product_name || 'Product image'"
                      />
                      <div class="flex-1 min-w-0">
                        <div class="font-medium mb-1 product-name">
                          {{ product.product_name }}
                        </div>
                        <div class="progress-wrapper">
                          <div
                            class="progress-bar"
                            :style="{
                              width:
                                getProgressValue(
                                  product.revenue,
                                  analyticsData?.revenue || 0
                                ) + '%',
                            }"
                            :aria-label="`${Math.round(
                              getProgressValue(
                                product.revenue,
                                analyticsData?.revenue || 0
                              )
                            )}% of total revenue`"
                            role="progressbar"
                            :aria-valuenow="
                              Math.round(
                                getProgressValue(
                                  product.revenue,
                                  analyticsData?.revenue || 0
                                )
                              )
                            "
                            aria-valuemin="0"
                            aria-valuemax="100"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="p-2 align-middle text-end">
                    ${{ formatPrice(product.revenue) }}
                    <span class="text-muted-foreground text-xs ml-1"
                      >({{
                        Math.round(
                          getProgressValue(
                            product.revenue,
                            analyticsData?.revenue || 0
                          )
                        )
                      }}%)</span
                    >
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Top Products by Units -->
      <div>
        <div class="glass-card p-4 products-card">
          <h3 class="text-lg font-semibold mb-4">Top Products by Units Sold</h3>
          <div class="table-container">
            <table class="w-full text-sm caption-bottom">
              <thead class="border-b border-border">
                <tr class="text-left font-medium text-muted-foreground">
                  <th class="h-10 px-2 align-middle">Product</th>
                  <th class="h-10 px-2 align-middle text-end">Units</th>
                </tr>
              </thead>
              <tbody class="[&_tr:last-child]:border-0">
                <tr
                  v-if="isLoading"
                  v-for="n in 5"
                  :key="'skeleton-units-' + n"
                  class="border-b border-border"
                >
                  <td class="p-2 align-middle">
                    <div class="flex items-center gap-3">
                      <Skeleton class="h-10 w-10" />
                      <div class="flex-1">
                        <Skeleton class="h-4 w-32 mb-2" />
                        <Skeleton class="h-1.5 w-full" />
                      </div>
                    </div>
                  </td>
                  <td class="p-2 align-middle text-end">
                    <Skeleton class="h-4 w-16 ml-auto" />
                  </td>
                </tr>
                <tr
                  v-if="!isLoading"
                  v-for="product in analyticsData?.top_products_units || []"
                  :key="product.product_id"
                  class="border-b border-border transition-colors hover:bg-muted/50"
                >
                  <td class="p-2 align-middle">
                    <div class="flex items-center gap-3">
                      <img
                        :src="product.image_url || '/placeholder.png'"
                        class="flex-shrink-0 product-image"
                        width="40"
                        height="40"
                        :alt="product.product_name || 'Product image'"
                      />
                      <div class="flex-1 min-w-0">
                        <div class="font-medium mb-1 product-name">
                          {{ product.product_name }}
                        </div>
                        <div class="progress-wrapper">
                          <div
                            class="progress-bar"
                            :style="{
                              width:
                                getProgressValue(
                                  product.units_sold,
                                  totalUnits
                                ) + '%',
                            }"
                            :aria-label="`${Math.round(
                              getProgressValue(product.units_sold, totalUnits)
                            )}% of total units`"
                            role="progressbar"
                            :aria-valuenow="
                              Math.round(
                                getProgressValue(product.units_sold, totalUnits)
                              )
                            "
                            aria-valuemin="0"
                            aria-valuemax="100"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="p-2 align-middle text-end">
                    {{ product.units_sold }}
                    <span class="text-muted-foreground text-xs ml-1"
                      >({{
                        Math.round(
                          getProgressValue(product.units_sold, totalUnits)
                        )
                      }}%)</span
                    >
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analytics-content {
  max-width: 100%;
  overflow-x: hidden;
}

/* KPI Cards Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.kpi-grid-spacing {
  margin-top: var(--spacing-md);
}

@media (min-width: 640px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.kpi-icon {
  width: 1.25rem;
  height: 1.25rem;
  background-color: var(--primary);
  -webkit-mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
  flex-shrink: 0;
}

.kpi-icon-dollar {
  -webkit-mask-image: url("/icons/dollar.svg");
  mask-image: url("/icons/dollar.svg");
}

.kpi-icon-packages {
  -webkit-mask-image: url("/icons/packages.svg");
  mask-image: url("/icons/packages.svg");
}

.kpi-icon-order-value {
  -webkit-mask-image: url("/icons/order-value.svg");
  mask-image: url("/icons/order-value.svg");
}

.kpi-icon-receipt {
  -webkit-mask-image: url("/icons/receipt.svg");
  mask-image: url("/icons/receipt.svg");
}

.kpi-card {
  border: 1px solid var(--border);
  background-color: var(--card);
  color: var(--card-foreground);
  box-shadow: var(--shadow-sm);
}

@media (max-width: 1023px) {
  .kpi-card {
    padding: var(--spacing-sm) !important;
  }
}

.chart-wrapper {
  height: 300px;
}

.product-image {
  object-fit: cover;
}

.progress-wrapper {
  height: 6px;
  background: var(--muted);
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: var(--primary);
}

/* Chart Container */
.chart-container {
  border: 1px solid var(--border);
  background-color: var(--card);
  color: var(--card-foreground);
  box-shadow: var(--shadow-sm);
}

/* Products Grid */
.products-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 1024px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.products-card {
  border: 1px solid var(--border);
  background-color: var(--card);
  color: var(--card-foreground);
  box-shadow: var(--shadow-sm);
  min-width: 0;
}

@media (max-width: 767px) {
  .products-card {
    overflow: auto;
  }
}

/* Table Container */
.table-container {
  overflow-x: auto;
  max-width: 100%;
}

.table-container table {
  min-width: 100%;
}

/* Product name truncation */
.product-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Border colors for tables */
:deep(.border-b) {
  border-color: var(--border);
}

:deep(.border-border) {
  border-color: var(--border);
}

.glass-card {
  background: var(--card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

/* Timeframe Select Styling */
.timeframe-select {
  color: var(--foreground);
  background-color: transparent;
  border: 1px solid var(--border) !important;
  min-width: 160px;
  border-radius: 0;
}

.timeframe-select:hover {
  border-color: var(--muted-foreground);
}

.timeframe-select:focus {
  outline: none;
  border-color: var(--ring);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--ring), transparent 50%);
}

.timeframe-select option {
  color: var(--foreground);
  background-color: var(--popover);
}

.timeframe-select option:checked {
  background-color: var(--primary);
  color: var(--primary-foreground);
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

@media (max-width: 1023px) {
  .main-header {
    margin-bottom: 0.75rem;
  }
}
</style>
