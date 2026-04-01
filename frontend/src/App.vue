<template>
  <div id="app">
    <el-container>
      <el-header>
        <h1>VPN 系统</h1>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
      <el-footer>
        <p>© 2026 VPN System. All rights reserved.</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.el-header {
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
}

.el-footer {
  background-color: #f5f5f5;
  text-align: center;
  padding: 20px;
}
</style>
