<template>
  <div class="page-container">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <h1 class="page-title" style="margin:0">常用乘机人</h1>
      <el-button type="primary" @click="openDialog()">添加乘机人</el-button>
    </div>
    <div class="page-card" v-loading="loading">
      <el-table :data="passengers">
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="id_card" label="身份证号" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column label="默认">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="success" size="small">默认</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog v-model="visible" :title="editing ? '编辑乘机人' : '添加乘机人'" width="420px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="身份证"><el-input v-model="form.id_card" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="默认"><el-switch v-model="form.is_default" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { passengerApi } from '@/api/passenger'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const passengers = ref([])
const visible = ref(false)
const editing = ref(null)
const form = ref({ name: '', id_card: '', phone: '', is_default: false })

const fetchList = async () => {
  loading.value = true
  try {
    const res = await passengerApi.getList()
    passengers.value = res.results || res
  } finally {
    loading.value = false
  }
}

const openDialog = (row = null) => {
  editing.value = row
  form.value = row ? { ...row } : { name: '', id_card: '', phone: '', is_default: false }
  visible.value = true
}

const handleSave = async () => {
  if (editing.value?.id) {
    await passengerApi.update(editing.value.id, form.value)
  } else {
    await passengerApi.create(form.value)
  }
  ElMessage.success('保存成功')
  visible.value = false
  fetchList()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该乘机人？')
  await passengerApi.remove(row.id)
  ElMessage.success('已删除')
  fetchList()
}

onMounted(fetchList)
</script>
