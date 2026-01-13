import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import News from "../views/News.vue";
import NewsDetails from "../views/NewsDetails.vue";
import Products from "../views/Products.vue";
import ProductDetails from "../views/ProductDetails.vue";
import SignIn from "../views/SignIn.vue";
import SignUp from "../views/SignUp.vue";
import Checkout from "../views/Checkout.vue";
import OrderTracking from "../views/OrderTracking.vue";
import About from "../views/About.vue";
import Dashboard from "../views/Dashboard.vue";
import { useAuth } from "../composables/useAuth";

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
  {
    path: "/checkout",
    name: "Checkout",
    component: Checkout,
  },
  {
    path: "/track-order",
    name: "OrderTracking",
    component: OrderTracking,
  },
  {
    path: "/about",
    name: "About",
    component: About,
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
    meta: { requiresAuth: true, requiresAdminOrStaff: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});

router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, isAdmin, fetchUser, user } = useAuth();
  
  // Wait for user to be fetched if we have a token but no user data yet
  if (localStorage.getItem("token") && !user.value) {
    await fetchUser();
  }

  if (to.meta.requiresAuth && !isAuthenticated.value) {
    next({ name: "SignIn", query: { redirect: to.fullPath } });
  } else if (to.meta.requiresAdminOrStaff && !isAdmin.value) {
    next({ name: "Home" });
  } else {
    next();
  }
});

export default router;
