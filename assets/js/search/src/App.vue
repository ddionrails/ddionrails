<template>
  <div id="app">
    <section class="container">
      <h1>Search</h1>
      <ul class="nav nav-tabs">
        <li>
          <router-link class="nav-link" to="/search/publications">Publications</router-link>
        </li>
      </ul>
      <router-view></router-view>
    </section>
  </div>
</template>

<script>
export default {
  name: "App",
  data() {
    return {
      query: this.$route.query
    };
  }
};
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
.card {
  border: 1px solid black;
}
</style>
