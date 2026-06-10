<template>
  <div class="survey-list">
    <!-- 工具栏 -->
    <el-card class="toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索问卷标题"
            style="width: 240px;"
            clearable
            @clear="fetchSurveys"
            @keyup.enter="fetchSurveys"
          >
            <template #prefix>
              <el-icon><IconSearch /></el-icon>
            </template>
          </el-input>
          <el-select v-model="statusFilter" placeholder="状态" style="width: 120px; margin-left: 12px;">
            <el-option label="全部" value="" />
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button type="primary" @click="handleCreate">
            <el-icon><IconPlus /></el-icon>
            新建问卷
          </el-button>
          <el-button @click="fetchSurveys">
            <el-icon><IconRefresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 问卷列表 -->
    <el-card class="list-card">
      <el-table
        v-loading="loading"
        :data="surveys"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="问卷标题" min-width="200">
          <template #default="{ row }">
            <div class="survey-title">
              <span>{{ row.title }}</span>
            </div>
            <div class="survey-desc">{{ row.description || '暂无描述' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="question_count" label="题目数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info">{{ row.question_count }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="participant_count" label="参与人数" width="100" align="center">
          <template #default="{ row }">
            <span class="participant-count">{{ row.participant_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handleAnalysis(row)">分析</el-button>
            <el-button type="success" link @click="handleExport(row)">导出</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建问卷对话框 -->
    <el-dialog v-model="createDialogVisible" title="新建问卷" width="500px">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="80px">
        <el-form-item label="问卷标题" prop="title">
          <el-input v-model="createForm.title" placeholder="请输入问卷标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入问卷描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSurveyList, createSurvey, deleteSurvey, exportSurveyData } from '../api'

const router = useRouter()

// 列表数据
const surveys = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const statusFilter = ref('')

// 新建对话框
const createDialogVisible = ref(false)
const createFormRef = ref()
const createForm = reactive({
  title: '',
  description: ''
})
const createRules = {
  title: [{ required: true, message: '请输入问卷标题', trigger: 'blur' }]
}

// 获取问卷列表
const fetchSurveys = async () => {
  try {
    loading.value = true
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    const data = await getSurveyList(params)
    surveys.value = data
  } catch (error) {
    console.error('获取问卷列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 新建问卷
const handleCreate = () => {
  createForm.title = ''
  createForm.description = ''
  createDialogVisible.value = true
}

const submitCreate = async () => {
  try {
    await createFormRef.value.validate()
    await createSurvey(createForm)
    ElMessage.success('创建成功')
    createDialogVisible.value = false
    fetchSurveys()
    // 跳转到编辑页面
    const newSurvey = surveys.value.find(s => s.title === createForm.title)
    if (newSurvey) {
      router.push(`/surveys/${newSurvey.id}/edit`)
    }
  } catch (error) {
    console.error('创建失败:', error)
  }
}

// 编辑问卷
const handleEdit = (row) => {
  router.push(`/surveys/${row.id}/edit`)
}

// 数据分析
const handleAnalysis = (row) => {
  router.push(`/analysis/${row.id}`)
}

// 导出数据
const handleExport = async (row) => {
  try {
    ElMessageBox.confirm(`确定要导出"${row.title}"的数据吗？`, '导出确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }).then(async () => {
      const blob = await exportSurveyData(row.id)
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([blob]))
      const link = document.createElement('a')
      link.href = url
      link.download = `survey_${row.id}_data.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    }).catch(() => {})
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 删除问卷
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除"${row.title}"吗？此操作不可恢复！`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteSurvey(row.id)
      ElMessage.success('删除成功')
      fetchSurveys()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchSurveys()
})
</script>

<style scoped>
.survey-list {
  min-height: 100%;
}

.toolbar-card {
  margin-bottom: 16px;
  border-radius: 12px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.list-card {
  border-radius: 12px;
}

.survey-title {
  font-weight: 600;
  color: #1e1e2e;
}

.survey-desc {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.participant-count {
  font-weight: 600;
  color: #7aa2f7;
}
</style>
