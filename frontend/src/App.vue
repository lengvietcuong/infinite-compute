<script setup>
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";
import CartSheet from "./components/CartSheet.vue";
import ChatWidget from "./components/ChatWidget.vue";
import NotificationDialog from "./components/ui/NotificationDialog.vue";
import { useCart } from "./composables/useCart";

const { stockDialog, closeStockDialog } = useCart();
</script>

<template>
  <div class="app-container">
    <Header />
    <router-view />
    <CartSheet />
    <ChatWidget />
    <Footer />
    <NotificationDialog
      :isOpen="stockDialog.isOpen"
      :title="stockDialog.title"
      :message="stockDialog.message"
      :variant="stockDialog.variant"
      @close="closeStockDialog"
    />
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  width: 100%;
}
</style>
