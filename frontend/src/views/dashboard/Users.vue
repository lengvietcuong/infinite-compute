<script setup>
import { ref, onMounted, computed } from "vue";
import { useAuth } from "../../composables/useAuth";
import { useToast } from "../../composables/useToast";
import Table from "../../components/ui/table/Table.vue";
import TableHeader from "../../components/ui/table/TableHeader.vue";
import TableRow from "../../components/ui/table/TableRow.vue";
import TableHead from "../../components/ui/table/TableHead.vue";
import TableBody from "../../components/ui/table/TableBody.vue";
import TableCell from "../../components/ui/table/TableCell.vue";
import Select from "../../components/ui/select/Select.vue";
import Modal from "../../components/ui/Modal.vue";
import Skeleton from "../../components/Skeleton.vue";

const { token } = useAuth();
const { showToast } = useToast();
const users = ref([]);
const isLoading = ref(false);
const isModalOpen = ref(false);
const isEditing = ref(false);
const showPassword = ref(false);
const userToDelete = ref(null);
const isDeleteModalOpen = ref(false);

// Search, Sort, Pagination
const searchQuery = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const sortColumn = ref("");
const sortDirection = ref("asc");

const formData = ref({
  id: null,
  full_name: "",
  email: "",
  password: "",
  role: "customer",
});

const passwordError = ref("");

const fetchUsers = async () => {
  isLoading.value = true;
  try {
    const response = await fetch("/api/users", {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    if (response.ok) {
      users.value = await response.json();
    }
  } catch (error) {
    console.error("Failed to fetch users:", error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchUsers);

const filteredUsers = computed(() => {
  let result = [...users.value];

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(
      (user) =>
        (user.full_name && user.full_name.toLowerCase().includes(query)) ||
        (user.email && user.email.toLowerCase().includes(query)) ||
        (user.role && user.role.toLowerCase().includes(query))
    );
  }

  if (sortColumn.value) {
    result.sort((a, b) => {
      let valA = a[sortColumn.value];
      let valB = b[sortColumn.value];

      if (typeof valA === "string") valA = valA.toLowerCase();
      if (typeof valB === "string") valB = valB.toLowerCase();

      if (valA < valB) return sortDirection.value === "asc" ? -1 : 1;
      if (valA > valB) return sortDirection.value === "asc" ? 1 : -1;
      return 0;
    });
  } else {
    // Default sort by id desc
    result.sort((a, b) => b.id - a.id);
  }

  return result;
});

const totalPages = computed(
  () => Math.ceil(filteredUsers.value.length / pageSize.value) || 1
);

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredUsers.value.slice(start, start + pageSize.value);
});

const handleSort = (column) => {
  if (sortColumn.value === column) {
    if (sortDirection.value === "asc") {
      sortDirection.value = "desc";
    } else if (sortDirection.value === "desc") {
      sortColumn.value = "";
      sortDirection.value = "asc";
    }
  } else {
    sortColumn.value = column;
    sortDirection.value = "asc";
  }
};

const goToFirstPage = () => {
  if (currentPage.value !== 1) currentPage.value = 1;
};

const goToLastPage = () => {
  if (currentPage.value !== totalPages.value)
    currentPage.value = totalPages.value;
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++;
};

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--;
};

const openCreate = () => {
  isEditing.value = false;
  formData.value = {
    id: null,
    full_name: "",
    email: "",
    password: "",
    role: "customer",
  };
  showPassword.value = false;
  isModalOpen.value = true;
};

const openEdit = (user) => {
  isEditing.value = true;
  formData.value = {
    id: user.id,
    full_name: user.full_name || "",
    email: user.email,
    password: "",
    role: user.role,
  };
  showPassword.value = false;
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  passwordError.value = "";
};

const saveUser = async () => {
  passwordError.value = "";

  if (!isEditing.value && !formData.value.password) {
    passwordError.value = "Password is required for new users";
    return;
  }

  if (formData.value.password && formData.value.password.length < 6) {
    passwordError.value = "Password must be at least 6 characters";
    return;
  }

  try {
    const url = isEditing.value
      ? `/api/users/${formData.value.id}`
      : "/api/users";

    const method = isEditing.value ? "PATCH" : "POST";

    const body = {
      full_name: formData.value.full_name,
      email: formData.value.email,
    };

    if (isEditing.value && formData.value.role) {
      body.role = formData.value.role;
    }

    if (formData.value.password) {
      body.password = formData.value.password;
    }

    const response = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token.value}`,
      },
      body: JSON.stringify(body),
    });

    if (response.ok) {
      await fetchUsers();
      closeModal();
      showToast(
        isEditing.value
          ? "User updated successfully"
          : "User created successfully",
        "success"
      );
    } else {
      const data = await response.json();
      showToast(
        data.detail ||
          (isEditing.value ? "Failed to update user" : "Failed to create user"),
        "error"
      );
    }
  } catch (error) {
    console.error("Error saving user:", error);
  }
};

const openDeleteModal = (user) => {
  userToDelete.value = user;
  isDeleteModalOpen.value = true;
};

const closeDeleteModal = () => {
  isDeleteModalOpen.value = false;
  userToDelete.value = null;
};

const deleteUser = async () => {
  if (!userToDelete.value) return;

  try {
    const response = await fetch(`/api/users/${userToDelete.value.id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });

    if (response.ok) {
      users.value = users.value.filter((u) => u.id !== userToDelete.value.id);
      closeDeleteModal();
      showToast("User deleted successfully", "success");
    } else {
      const data = await response.json();
      showToast(data.detail || "Failed to delete user", "error");
    }
  } catch (error) {
    console.error("Error deleting user:", error);
  }
};
</script>

<template>
  <div>
    <div class="flex items-center justify-between gap-3 header-row flex-wrap">
      <div class="flex items-center gap-3 md:gap-4 flex-1 min-w-0">
        <h2 class="text-2xl font-bold tracking-tight">Users</h2>
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
            v-model="searchQuery"
            type="text"
            placeholder="Search users..."
            class="search-input"
          />
        </div>
      </div>
      <button
        @click="openCreate"
        class="btn btn-primary gap-2 whitespace-nowrap"
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
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        <span class="d-none d-sm-inline">Add User</span>
        <span class="d-sm-none">Add</span>
      </button>
    </div>

    <div
      class="border bg-card text-card-foreground shadow-sm border-color table-wrapper"
      role="region"
      aria-label="Users table"
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead
              @click="handleSort('id')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                ID
                <svg
                  v-if="sortColumn !== 'id'"
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon"
                >
                  <path d="m21 16-4 4-4-4" />
                  <path d="M17 20V4" />
                  <path d="m3 8 4-4 4 4" />
                  <path d="M7 4v16" />
                </svg>
                <svg
                  v-else-if="sortDirection === 'asc'"
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon sort-icon-active"
                >
                  <path d="m5 12 7-7 7 7" />
                  <path d="M12 19V5" />
                </svg>
                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon sort-icon-active"
                >
                  <path d="M12 5v14" />
                  <path d="m19 12-7 7-7-7" />
                </svg>
              </div>
            </TableHead>
            <TableHead
              @click="handleSort('full_name')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Full Name
                <svg
                  v-if="sortColumn !== 'full_name'"
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon"
                >
                  <path d="m21 16-4 4-4-4" />
                  <path d="M17 20V4" />
                  <path d="m3 8 4-4 4 4" />
                  <path d="M7 4v16" />
                </svg>
                <svg
                  v-else-if="sortDirection === 'asc'"
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon sort-icon-active"
                >
                  <path d="m5 12 7-7 7 7" />
                  <path d="M12 19V5" />
                </svg>
                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon sort-icon-active"
                >
                  <path d="M12 5v14" />
                  <path d="m19 12-7 7-7-7" />
                </svg>
              </div>
            </TableHead>
            <TableHead
              @click="handleSort('email')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Email
                <svg
                  v-if="sortColumn !== 'email'"
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon"
                >
                  <path d="m21 16-4 4-4-4" />
                  <path d="M17 20V4" />
                  <path d="m3 8 4-4 4 4" />
                  <path d="M7 4v16" />
                </svg>
                <svg
                  v-else-if="sortDirection === 'asc'"
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon sort-icon-active"
                >
                  <path d="m5 12 7-7 7 7" />
                  <path d="M12 19V5" />
                </svg>
                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon sort-icon-active"
                >
                  <path d="M12 5v14" />
                  <path d="m19 12-7 7-7-7" />
                </svg>
              </div>
            </TableHead>
            <TableHead
              @click="handleSort('role')"
              class="cursor-pointer select-none"
            >
              <div class="flex items-center gap-2">
                Role
                <svg
                  v-if="sortColumn !== 'role'"
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon"
                >
                  <path d="m21 16-4 4-4-4" />
                  <path d="M17 20V4" />
                  <path d="m3 8 4-4 4 4" />
                  <path d="M7 4v16" />
                </svg>
                <svg
                  v-else-if="sortDirection === 'asc'"
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon sort-icon-active"
                >
                  <path d="m5 12 7-7 7 7" />
                  <path d="M12 19V5" />
                </svg>
                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="sort-icon sort-icon-active"
                >
                  <path d="M12 5v14" />
                  <path d="m19 12-7 7-7-7" />
                </svg>
              </div>
            </TableHead>
            <TableHead class="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-if="isLoading" v-for="n in 5" :key="'skeleton-' + n">
            <TableCell><Skeleton class="h-4 w-8" :rounded="false" /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-32" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-40" :rounded="false"
            /></TableCell>
            <TableCell
              ><Skeleton class="h-4 w-32" :rounded="false"
            /></TableCell>
            <TableCell class="text-right"
              ><div class="flex justify-end gap-2">
                <Skeleton class="h-8 w-8" :rounded="false" /><Skeleton
                  class="h-8 w-8"
                  :rounded="false"
                /></div
            ></TableCell>
          </TableRow>
          <TableRow
            v-for="user in paginatedUsers"
            :key="user.id"
            v-if="!isLoading"
          >
            <TableCell>{{ user.id }}</TableCell>
            <TableCell>{{ user.full_name || "-" }}</TableCell>
            <TableCell>{{ user.email }}</TableCell>
            <TableCell>
              <span class="role-badge" :class="`role-${user.role}`">
                {{ user.role.charAt(0).toUpperCase() + user.role.slice(1) }}
              </span>
            </TableCell>
            <TableCell class="text-right">
              <div class="flex justify-end gap-2">
                <button
                  @click="openEdit(user)"
                  class="action-btn"
                  title="Edit"
                  aria-label="Edit user"
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
                    aria-hidden="true"
                  >
                    <path
                      d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"
                    ></path>
                  </svg>
                </button>
                <button
                  @click="openDeleteModal(user)"
                  class="action-btn delete-btn"
                  title="Delete"
                  aria-label="Delete user"
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
                    aria-hidden="true"
                  >
                    <path d="M3 6h18"></path>
                    <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                    <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                  </svg>
                </button>
              </div>
            </TableCell>
          </TableRow>
          <TableRow v-if="users.length === 0 && !isLoading">
            <TableCell
              colspan="5"
              class="text-center h-24 text-muted-foreground"
            >
              No users found.
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination-wrapper">
      <button
        @click="goToFirstPage"
        :disabled="currentPage === 1"
        class="btn-pagination"
        aria-label="Go to first page"
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
          <path d="m11 17-5-5 5-5" />
          <path d="m18 17-5-5 5-5" />
        </svg>
      </button>
      <button
        @click="prevPage"
        :disabled="currentPage === 1"
        class="btn-pagination"
        aria-label="Go to previous page"
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
          <path d="m15 18-6-6 6-6" />
        </svg>
      </button>
      <span class="d-flex align-items-center font-mono text-muted"
        >Page {{ currentPage }}/{{ totalPages }}</span
      >
      <button
        @click="nextPage"
        :disabled="currentPage >= totalPages"
        class="btn-pagination"
        aria-label="Go to next page"
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
          <path d="m9 18 6-6-6-6" />
        </svg>
      </button>
      <button
        @click="goToLastPage"
        :disabled="currentPage >= totalPages"
        class="btn-pagination"
        aria-label="Go to last page"
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
          <path d="m6 17 5-5-5-5" />
          <path d="m13 17 5-5-5-5" />
        </svg>
      </button>
    </div>

    <Modal
      :isOpen="isModalOpen"
      :title="isEditing ? 'Edit User' : 'Add User'"
      @close="closeModal"
    >
      <div class="modal-content-padding">
        <div class="space-y-4 max-h-[70vh] overflow-y-auto">
          <div>
            <label class="form-label">
              Full Name<span v-if="!isEditing" class="text-destructive">*</span>
            </label>
            <input
              v-model="formData.full_name"
              class="form-control"
              :placeholder="isEditing ? '' : 'John Doe'"
            />
          </div>
          <div>
            <label class="form-label">
              Email<span v-if="!isEditing" class="text-destructive">*</span>
            </label>
            <input
              v-model="formData.email"
              type="email"
              class="form-control"
              :placeholder="isEditing ? '' : 'john@example.com'"
            />
          </div>
          <div>
            <label class="form-label">
              Password<span v-if="!isEditing" class="text-destructive">*</span>
            </label>
            <div class="password-input-wrapper">
              <input
                :type="showPassword ? 'text' : 'password'"
                v-model="formData.password"
                class="form-control password-input"
                :class="{ 'input-error': passwordError }"
                :placeholder="isEditing ? 'Leave blank to keep unchanged' : ''"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="password-toggle-btn"
              >
                <svg
                  v-if="showPassword"
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
                  <path
                    d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
                  ></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
                <svg
                  v-else
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
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
              </button>
            </div>
            <p v-if="passwordError" class="password-error text-xs">
              {{ passwordError }}
            </p>
            <p v-else class="password-hint text-xs">
              Password must be at least 6 characters
            </p>
          </div>
          <div v-if="isEditing">
            <label class="form-label">Role</label>
            <Select
              v-model="formData.role"
              class-name="h-10 w-full border-color bg-background text-foreground"
            >
              <option value="customer">Customer</option>
              <option value="staff">Staff</option>
              <option value="admin">Admin</option>
            </Select>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeModal" class="btn btn-outline">Cancel</button>
          <button @click="saveUser" class="btn btn-primary">
            Save Changes
          </button>
        </div>
      </div>
    </Modal>

    <Modal
      :isOpen="isDeleteModalOpen"
      title="Delete User"
      @close="closeDeleteModal"
    >
      <div class="modal-content-padding">
        <p>
          Are you sure you want to delete user
          <strong>{{ userToDelete?.email }}</strong
          >? This action cannot be undone.
        </p>
        <div class="flex justify-end gap-2 mt-6">
          <button @click="closeDeleteModal" class="btn btn-outline">
            Cancel
          </button>
          <button @click="deleteUser" class="btn btn-destructive">
            Delete
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<style scoped>
:deep(.border-b) {
  border-color: var(--border);
}

.search-wrapper {
  position: relative;
  display: inline-block;
  flex: 1;
  max-width: 300px;
  min-width: 0;
}

@media (max-width: 640px) {
  .search-wrapper {
    max-width: 100%;
    width: 100%;
  }
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
  height: 2.375rem;
  width: 100%;
  border-radius: var(--radius);
  border: 1px solid var(--input);
  background: var(--background);
  padding: var(--spacing-xs) var(--spacing-sm) var(--spacing-xs)
    calc(var(--spacing-xl) + var(--spacing-xs));
  font-size: var(--text-sm);
  box-shadow: var(--shadow-sm);
  transition: color var(--transition-base), box-shadow var(--transition-base);
  outline: none;
  color: var(--foreground);
}

.search-input::placeholder {
  color: var(--muted-foreground);
}

.search-input:focus-visible {
  border-color: var(--ring);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--ring), transparent 50%);
}

.sort-icon {
  color: var(--muted-foreground);
  flex-shrink: 0;
}

.sort-icon-active {
  color: var(--primary);
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding: 1rem;
  padding-bottom: 1rem;
  background-color: transparent;
}

.btn-pagination {
  width: calc(var(--spacing-xl) + var(--spacing-xs));
  height: calc(var(--spacing-xl) + var(--spacing-xs));
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
  font-size: var(--text-xs);
}

.btn-pagination svg {
  width: 20px;
  height: 20px;
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

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: var(--spacing-xl);
  height: var(--spacing-xl);
  background-color: transparent;
  border: none;
  cursor: pointer;
  border-radius: var(--radius);
  transition: all var(--transition-base);
  color: var(--foreground);
}

.action-btn:hover {
  background-color: var(--accent);
  color: var(--primary);
}

.action-btn svg {
  pointer-events: none;
}

.action-btn.delete-btn:hover {
  color: var(--destructive);
  background-color: color-mix(in srgb, var(--destructive), transparent 90%);
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  margin-bottom: var(--spacing-xs);
}

.form-control {
  background: color-mix(in srgb, var(--background), transparent 50%);
  border: 1px solid var(--border);
  color: var(--foreground);
  padding: var(--spacing-sm) var(--spacing-sm);
  height: auto;
  font-size: var(--text-sm);
  border-radius: var(--radius);
  transition: all var(--transition-base);
}

.form-control::placeholder {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
}

.form-control:focus {
  background: var(--background);
  border-color: var(--primary);
  outline: none;
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary), transparent 80%);
}

.modal-content-padding {
  padding: 0 var(--spacing-lg) var(--spacing-lg) var(--spacing-lg);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
}

.role-badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--text-xs);
  font-weight: 500;
  border-radius: var(--radius);
  text-transform: capitalize;
}

.role-customer {
  background-color: var(--accent);
  color: var(--accent-foreground);
}

.role-staff {
  background-color: color-mix(in srgb, var(--primary), transparent 85%);
  color: var(--primary);
}

.role-admin {
  background-color: color-mix(in srgb, var(--destructive), transparent 85%);
  color: var(--destructive);
}

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input {
  padding-right: calc(var(--spacing-xl) + var(--spacing-sm));
}

.password-toggle-btn {
  position: absolute;
  right: var(--spacing-sm);
  background: none;
  border: none;
  color: var(--muted-foreground);
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  transition: color var(--transition-base);
}

.password-toggle-btn:hover {
  color: var(--foreground);
}

.password-hint {
  color: var(--muted-foreground);
  margin-top: var(--spacing-xs);
  margin-bottom: 0;
}

.password-error {
  color: var(--destructive);
  margin-top: var(--spacing-xs);
  margin-bottom: 0;
}

.input-error {
  border-color: var(--destructive);
}

.input-error:focus {
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--destructive), transparent 80%);
}

.header-row {
  margin-bottom: var(--spacing-sm);
}

.table-wrapper {
  margin-top: var(--spacing-md);
}

@media (max-width: 1023px) {
  .header-row {
    margin-bottom: var(--spacing-sm);
  }
}

@media (max-width: 640px) {
  .header-row {
    margin-bottom: var(--spacing-sm);
  }

  .table-wrapper {
    margin-top: var(--spacing-md);
  }
}

@media (max-width: 1023px) {
  .btn.btn-primary {
    height: 2.375rem;
  }
}

@media (max-width: 640px) {
  .table-wrapper {
    margin-top: 1rem;
  }

  .flex.items-center.justify-between {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .flex.items-center.gap-4 {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
    gap: 0.75rem;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }

  .modal-actions .btn {
    width: 100%;
  }
}
</style>
