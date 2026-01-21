import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export function useUrlState() {
  const route = useRoute();
  const router = useRouter();

  const updateQuery = (params) => {
    const query = { ...route.query };
    
    Object.entries(params).forEach(([key, value]) => {
      if (value === null || value === undefined || value === '') {
        delete query[key];
      } else {
        query[key] = String(value);
      }
    });

    router.replace({ query });
  };

  const getQueryParam = (key, defaultValue) => {
    const value = route.query[key];
    if (value === undefined || value === null) {
      return defaultValue;
    }
    return value;
  };

  const getNumberParam = (key, defaultValue) => {
    const value = route.query[key];
    if (value === undefined || value === null) {
      return defaultValue;
    }
    const parsed = Number(value);
    return isNaN(parsed) ? defaultValue : parsed;
  };

  return {
    updateQuery,
    getQueryParam,
    getNumberParam,
  };
}

export function useUrlPagination(defaultPageSize = 10) {
  const { updateQuery, getNumberParam, getQueryParam } = useUrlState();
  const route = useRoute();

  const currentPage = ref(getNumberParam('page', 1));
  const pageSize = ref(getNumberParam('pageSize', defaultPageSize));
  const searchQuery = ref(getQueryParam('search', ''));
  const sortColumn = ref(getQueryParam('sortBy', ''));
  const sortDirection = ref(getQueryParam('sortDir', 'asc'));

  watch([currentPage, pageSize, searchQuery, sortColumn, sortDirection], () => {
    updateQuery({
      page: currentPage.value !== 1 ? currentPage.value : null,
      pageSize: pageSize.value !== defaultPageSize ? pageSize.value : null,
      search: searchQuery.value || null,
      sortBy: sortColumn.value || null,
      sortDir: sortColumn.value && sortDirection.value !== 'asc' ? sortDirection.value : null,
    });
  });

  watch(() => route.query, (newQuery) => {
    currentPage.value = getNumberParam('page', 1);
    pageSize.value = getNumberParam('pageSize', defaultPageSize);
    searchQuery.value = getQueryParam('search', '');
    sortColumn.value = getQueryParam('sortBy', '');
    sortDirection.value = getQueryParam('sortDir', 'asc');
  }, { deep: true });

  return {
    currentPage,
    pageSize,
    searchQuery,
    sortColumn,
    sortDirection,
  };
}
