import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import News from "../views/News.vue";
import NewsDetails from "../views/NewsDetails.vue";
import Products from "../views/Products.vue";
import ProductDetails from "../views/ProductDetails.vue";
import SignIn from "../views/SignIn.vue";
import SignUp from "../views/SignUp.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
  },
  {
    path: "/news",
    name: "News",
    component: News,
  },
  {
    path: "/news/:id",
    name: "NewsDetails",
    component: NewsDetails,
  },
  {
    path: "/products",
    name: "Products",
    component: Products,
  },
  {
    path: "/products/:id",
    name: "ProductDetails",
    component: ProductDetails,
  },
  {
    path: "/sign-in",
    name: "SignIn",
    component: SignIn,
  },
  {
    path: "/sign-up",
    name: "SignUp",
    component: SignUp,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
