import { ref } from 'vue';

const toasts = ref([]);

export function useToast() {
  const showToast = (message, type = 'success') => {
    const id = Date.now() + Math.random();
    const toast = {
      id,
      message,
      type,
    };
    
    toasts.value.push(toast);
    
    setTimeout(() => {
      removeToast(id);
    }, 3000);
    
    return id;
  };
  
  const removeToast = (id) => {
    const index = toasts.value.findIndex(t => t.id === id);
    if (index !== -1) {
      toasts.value.splice(index, 1);
    }
  };
  
  return {
    toasts,
    showToast,
    removeToast,
  };
}
