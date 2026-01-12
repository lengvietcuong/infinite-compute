import { createApp } from "vue";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap";
import "./style.css";
import App from "./App.vue";
import router from "./router";
import Particles from "@tsparticles/vue3";
import { loadSlim } from "@tsparticles/slim";

createApp(App)
  .use(router)
  .use(Particles, {
    init: async (engine) => {
      await loadSlim(engine);
    },
  })
  .mount("#app");
