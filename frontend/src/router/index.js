import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import News from '../views/News.vue';
import Products from '../views/Products.vue';
import ProductDetails from '../views/ProductDetails.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/news',
    name: 'News',
    component: News
  },
  {
    path: '/products',
    name: 'Products',
    component: Products
  },
  {
    path: '/products/:id',
    name: 'ProductDetails',
    component: ProductDetails
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
