<template>
  <div class="payment">
    <el-card>
      <template #header><span>USDT支付</span></template>
      <div v-if="!selectedPlan">
        <h3>选择套餐</h3>
        <el-row :gutter="20">
          <el-col :span="8" v-for="plan in plans" :key="plan.id">
            <el-card class="plan-card" :class="{active: selectedPlanId === plan.id}" @click="selectedPlanId = plan.id">
              <h4>{{ plan.name }}</h4>
              <div>¥{{ plan.price }}</div>
              <p>{{ plan.duration_days }}天</p>
            </el-card>
          </el-col>
        </el-row>
        <el-button type="primary" size="large" :disabled="!selectedPlanId" @click="createPayment">确认支付</el-button>
      </div>
      <div v-else>
        <el-alert type="warning">请在 {{ remainingTime }} 内完成支付</el-alert>
        <p>支付金额: {{ usdtAmount }} USDT</p>
        <p>收款地址: {{ walletAddress }}</p>
        <el-button type="primary" @click="copyAddress">复制地址</el-button>
        <el-button type="success" @click="checkPayment">我已支付</el-button>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import axios from "axios"
const router = useRouter()
const plans = ref([])
const selectedPlanId = ref(null)
const selectedPlan = ref(null)
const usdtAmount = ref(0)
const walletAddress = ref("")
const remainingTime = ref("30:00")
const orderId = ref(null)
const loadPlans = async () => {
  try {
    const res = await axios.get("/api/v1/plans/active")
    plans.value = res.data
  } catch (e) {}
}
const createPayment = async () => {
  try {
    const token = localStorage.getItem("token")
    const plan = plans.value.find(p => p.id === selectedPlanId.value)
    selectedPlan.value = plan
    const subRes = await axios.post("/api/v1/subscriptions/purchase", { plan_id: plan.id }, { headers: { Authorization: "Bearer " + token } })
    const payRes = await axios.post("/api/v1/payments/usdt/create", { subscription_id: subRes.data.id, amount: parseFloat(plan.price), network: "TRC20" }, { headers: { Authorization: "Bearer " + token } })
    walletAddress.value = payRes.data.wallet_address
    usdtAmount.value = payRes.data.usdt_amount
    orderId.value = payRes.data.payment_id
    ElMessage.success("订单创建成功")
  } catch (e) {
    ElMessage.error("创建失败")
  }
}
const copyAddress = async () => {
  try {
    await navigator.clipboard.writeText(walletAddress.value)
    ElMessage.success("已复制")
  } catch (e) {}
}
const checkPayment = async () => {
  try {
    const token = localStorage.getItem("token")
    const res = await axios.get("/api/v1/payments/usdt/" + orderId.value + "/status", { headers: { Authorization: "Bearer " + token } })
    if (res.data.status === "success") {
      ElMessage.success("支付成功")
      router.push("/subscription")
    } else {
      ElMessage.info("暂未检测到支付")
    }
  } catch (e) {}
}
onMounted(loadPlans)
</script>
<style scoped>
.payment { padding: 20px; max-width: 800px; margin: 0 auto; }
.plan-card { cursor: pointer; text-align: center; padding: 20px; }
.plan-card.active { border: 2px solid #409EFF; }
</style>
