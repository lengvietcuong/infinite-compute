<script setup>
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";
import CartSheet from "./components/CartSheet.vue";
</script>

<template>
  <div class="app-container">
    <Header />
    <router-view />
    <CartSheet />
    <Footer />
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  width: 100%;
}
</style>
