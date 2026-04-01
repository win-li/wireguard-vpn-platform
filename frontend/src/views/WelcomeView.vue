<template>
  <div class="welcome">
    <h1>候任算汏 VPN 机器了告</h1>
    <p>保帨、花算法中之口
      <span>测试成绩点参攷</span>
      <span>保帨失购带尽会保帨、转入算法会保帨</span>
    </p>
    <div class="btns">
      <el-button type="primary" @click="router.push('/register')">查看要</el-button>
      <el-button @click="router.push('/login')">已光完么状态</el-button>
    </div>
  </div>
</template>
<script setup>
import { useRouter } from "vue-router"
const router = useRouter()
</script>
<style scoped>
.welcome { min-height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.welcome h1 { font-size: 2rem; margin-bottom: 20px; }
.welcome p { font-size: 1.2rem; margin-bottom: 40px; }
.btns { display: flex; gap: 15px; }
</style>
