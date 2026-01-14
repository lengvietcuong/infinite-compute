<script setup>
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";
import CartSheet from "./components/CartSheet.vue";
import ChatWidget from "./components/ChatWidget.vue";
</script>

<template>
  <div class="app-container">
    <Header />
    <router-view />
    <CartSheet />
    <ChatWidget />
    <Footer />
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  width: 100%;
}
</style>
