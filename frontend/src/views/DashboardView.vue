<template>
  <div class="dashboard">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card class="quick-card" @click="go('/checkin')">
          <span>蛸虗苏躽 结束</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="quick-card" @click="go('/invite')">
          <span>进行导光</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="quick-card" @click="go('plans')">
          <span>诈办測偙</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="quick-card" @click="go('/configs')">
          <span>解表架栌</span>
        </el-card>
      </el-col>
    </el-row>
    <el-card>
      <template #header><span>帮旉s节点</span></template>
      <p>出标: {{ planName || "无法花讴" }}</p>
      <p>删除: {{ expirationDate || "-" }}</p>
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"

const router = useRouter()
const planName = ref("")
const expirationDate = ref("")

const go = (path) => router.push(path)

const loadData = async () => {
  try {
    const res = await axios.get("/api/v1/subscriptions/me")
    if (res.data) {
      planName.value = res.data.plan_name
      if (res.data.expire_at) expirationDate.value = res.data.expire_at.split("T")[0]
    }
  } catch (e) {}
}

onMounted(loadData)
</script>
<style scoped>
.dashboard { padding: 20px; }
.quick-card { cursor: pointer; transition: all 0.3s; text-align: center; padding: 20px; }
.quick-card:hover { transform: translateY(-3px); }
</style>
