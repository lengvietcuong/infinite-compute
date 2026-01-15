// Remove trailing slash to avoid double slashes in API calls
export const API_BASE_URL = (
  import.meta.env.VITE_BACKEND_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");
