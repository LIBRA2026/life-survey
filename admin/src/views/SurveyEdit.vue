<template>
  <div class="survey-edit">
    <el-card class="header-card">
      <div class="header-content">
        <el-button @click="goBack">
          <el-icon><IconBack /></el-icon>
          返回
        </el-button>
        <div class="title-section">
          <h2>{{ surveyId ? '编辑问卷' : '新建问卷' }}</h2>
          <el-tag v-if="surveyId">{{ surveyInfo.title }}</el-tag>
        </div>
      </div>
    </el-card>

    <!-- 基本信息 -->
    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
        </div>
      </template>
      <el-form :model="form" label-width="100px" style="max-width: 600px;">
        <el-form-item label="问卷标题">
          <el-input v-model="form.title" placeholder="请输入问卷标题" />
        </el-form-item>
        <el-form-item label="问卷描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入问卷描述"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveBasicInfo">保存信息</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 题目管理 -->
    <el-card class="questions-card">
      <template #header>
        <div class="card-header">
          <span>题目管理</span>
          <el-button type="primary" size="small" @click="handleAddQuestion">
            <el-icon><IconPlus /></el-icon>
            添加题目
          </el-button>
        </div>
      </template>

      <div v-if="questions.length === 0" class="empty-questions">
        <el-empty description="暂无题目，请点击上方按钮添加" />
      </div>

      <div v-else class="questions-list">
        <div
          v-for="(question, index) in questions"
          :key="question.id || index"
          class="question-item"
        >
          <div class="question-header">
            <span class="question-index">Q{{ index + 1 }}</span>
            <el-tag :type="getQuestionTypeTag(question.type)" size="small">
              {{ getQuestionTypeName(question.type) }}
            </el-tag>
            <el-button type="danger" link size="small" @click="handleDeleteQuestion(index)">
              删除
            </el-button>
          </div>
          <div class="question-content">
            <el-input
              v-model="question.content"
              type="textarea"
              :rows="2"
              placeholder="请输入题目内容"
            />
          </div>
          <div v-if="question.type !== 'scale'" class="question-options">
            <div
              v-for="(option, optIndex) in question.options"
              :key="optIndex"
              class="option-item"
            >
              <span class="option-label">{{ String.fromCharCode(65 + optIndex) }}.</span>
              <el-input
                v-model="question.options[optIndex]"
                placeholder="选项内容"
                style="flex: 1;"
              />
              <el-button
                type="danger"
                link
                @click="removeOption(question, optIndex)"
                :disabled="question.options.length <= 2"
              >
                <el-icon><IconDelete /></el-icon>
              </el-button>
            </div>
            <el-button
              type="primary"
              link
              size="small"
              @click="addOption(question)"
              :disabled="question.options.length >= 6"
            >
              <el-icon><IconPlus /></el-icon>
              添加选项
            </el-button>
          </div>
          <div v-else class="scale-options">
            <span class="scale-label">量表范围：1 - 5</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 添加题目对话框 -->
    <el-dialog v-model="addDialogVisible" title="添加题目" width="500px">
      <el-form label-width="100px">
        <el-form-item label="题目类型">
          <el-select v-model="newQuestion.type" style="width: 100%;">
            <el-option label="单选题" value="single_choice" />
            <el-option label="多选题" value="multiple_choice" />
            <el-option label="量表题" value="scale" />
          </el-select>
        </el-form-item>
        <el-form-item label="题目内容">
          <el-input
            v-model="newQuestion.content"
            type="textarea"
            :rows="2"
            placeholder="请输入题目内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddQuestion">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const route = useRoute()
const router = useRouter()

// 获取问卷ID
const surveyId = computed(() => parseInt(route.params.id) || null)

// 表单数据
const surveyInfo = reactive({
  title: ''
})

const form = reactive({
  title: '',
  description: '',
  status: 'active'
})

// 题目列表
const questions = ref([])

// 添加题目对话框
const addDialogVisible = ref(false)
const newQuestion = reactive({
  type: 'single_choice',
  content: ''
})

// 初始化
const init = async () => {
  if (surveyId.value) {
    await fetchSurveyDetail()
  }
}

// 获取问卷详情
const fetchSurveyDetail = async () => {
  try {
    // 这里应该调用获取问卷详情的API
    // const data = await getSurveyDetail(surveyId.value)
    // form.title = data.title
    // form.description = data.description
    // form.status = data.status
    // questions.value = data.questions
    // 为了演示，先使用空数据
    form.title = '人生观调研问卷'
    form.description = '欢迎参加人生观调研！'
    form.status = 'active'
    surveyInfo.title = form.title
  } catch (error) {
    console.error('获取问卷详情失败:', error)
  }
}

// 保存基本信息
const saveBasicInfo = async () => {
  try {
    if (surveyId.value) {
      await api.updateSurvey(surveyId.value, form)
    } else {
      const data = await api.createSurvey(form)
      surveyId.value = data.id
    }
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 返回列表
const goBack = () => {
  router.push('/surveys')
}

// 添加题目
const handleAddQuestion = () => {
  newQuestion.type = 'single_choice'
  newQuestion.content = ''
  addDialogVisible.value = true
}

const confirmAddQuestion = () => {
  if (!newQuestion.content.trim()) {
    ElMessage.warning('请输入题目内容')
    return
  }
  
  const question = {
    id: Date.now(),
    type: newQuestion.type,
    content: newQuestion.content,
    options: newQuestion.type === 'scale' ? ['1', '2', '3', '4', '5'] : ['', ''],
    sort_order: questions.value.length
  }
  
  questions.value.push(question)
  addDialogVisible.value = false
  ElMessage.success('题目已添加')
}

// 删除题目
const handleDeleteQuestion = (index) => {
  questions.value.splice(index, 1)
}

// 添加选项
const addOption = (question) => {
  if (question.options.length < 6) {
    question.options.push('')
  }
}

// 删除选项
const removeOption = (question, index) => {
  if (question.options.length > 2) {
    question.options.splice(index, 1)
  }
}

// 获取题型名称
const getQuestionTypeName = (type) => {
  const map = {
    'single_choice': '单选题',
    'multiple_choice': '多选题',
    'scale': '量表题'
  }
  return map[type] || type
}

// 获取题型标签类型
const getQuestionTypeTag = (type) => {
  const map = {
    'single_choice': '',
    'multiple_choice': 'warning',
    'scale': 'success'
  }
  return map[type] || 'info'
}

onMounted(() => {
  init()
})
</script>

<style scoped>
.survey-edit {
  min-height: 100%;
}

.header-card {
  margin-bottom: 16px;
  border-radius: 12px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-section h2 {
  margin: 0;
  font-size: 18px;
}

.info-card,
.questions-card {
  margin-bottom: 16px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-questions {
  padding: 40px 0;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-item {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.question-index {
  font-weight: 600;
  color: #7aa2f7;
}

.question-content {
  margin-bottom: 12px;
}

.question-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-label {
  width: 24px;
  font-weight: 500;
  color: #666;
}

.scale-options {
  padding: 8px 0;
}

.scale-label {
  color: #888;
  font-size: 13px;
}
</style>
