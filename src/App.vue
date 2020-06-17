<template>
  <div id="app">
    <Bangkit/>
  </div>
</template>

<script>
import Bangkit from './components/Bangkit.vue'

export default {
  name: 'App',
  components: {
    Bangkit
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
