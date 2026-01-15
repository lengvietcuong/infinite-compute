import { ref, computed } from "vue";
import { API_BASE_URL } from "@/config/api";

const user = ref(null);
const token = ref(localStorage.getItem("token"));
const isLoading = ref(false);

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(
    () => user.value?.role === "admin" || user.value?.role === "staff"
  ); // Including staff as per requirement "staff or an admin"

  const fetchUser = async () => {
    if (!token.value) {
      user.value = null;
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/users/me`, {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      });

      if (response.ok) {
        user.value = await response.json();
      } else {
        // Token might be invalid or expired
        logout();
      }
    } catch (error) {
      console.error("Failed to fetch user:", error);
      // Don't auto-logout on network error, but maybe clear user
    }
  };

  const login = async (newToken) => {
    token.value = newToken;
    localStorage.setItem("token", newToken);
    await fetchUser();
  };

  const logout = () => {
    token.value = null;
    user.value = null;
    localStorage.removeItem("token");
    window.location.href = "/"; // Simple redirection
  };

  // Initialize
  if (token.value && !user.value) {
    fetchUser();
  }

  return {
    user,
    token,
    isLoading,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    fetchUser,
  };
}
