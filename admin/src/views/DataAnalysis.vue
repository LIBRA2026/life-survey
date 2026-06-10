<template>
  <div class="data-analysis">
    <!-- 顶部信息 -->
    <el-card class="header-card">
      <div class="header-content">
        <div class="info-left">
          <el-button @click="goBack">
            <el-icon><IconBack /></el-icon>
            返回
          </el-button>
          <div class="survey-info">
            <h2>{{ surveyInfo.title }}</h2>
            <div class="survey-stats">
              <el-tag type="success">参与人数: {{ surveyStats.total_participants || 0 }}</el-tag>
              <el-tag type="warning">完成率: {{ ((surveyStats.completion_rate || 0) * 100).toFixed(1) }}%</el-tag>
            </div>
          </div>
        </div>
        <el-button type="success" @click="handleExport">
          <el-icon><IconDownload /></el-icon>
          导出数据
        </el-button>
      </div>
    </el-card>

    <!-- 图表区域 -->
    <el-row :gutter="20">
      <el-col v-for="(stat, index) in surveyStats.question_stats || []" :key="index" :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <span class="question-num">Q{{ index + 1 }}</span>
              <span class="question-type">{{ getQuestionTypeName(stat.question_type) }}</span>
            </div>
          </template>
          <div class="question-text">{{ stat.question_content }}</div>
          <div :ref="el => chartRefs[index] = el" class="question-chart"></div>
          <div class="answer-count">答题人数: {{ stat.total_answers }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!loading && (!surveyStats.question_stats || surveyStats.question_stats.length === 0)" description="暂无数据" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getSurveyStats, exportSurveyData } from '../api'

const route = useRoute()
const router = useRouter()

// 问卷信息
const surveyInfo = reactive({
  title: '人生观调研问卷'
})

const surveyStats = reactive({
  total_participants: 0,
  completion_rate: 0,
  question_stats: []
})

const loading = ref(false)
const chartRefs = ref([])
let charts = []

// 获取分析数据
const fetchAnalysis = async () => {
  try {
    loading.value = true
    const id = route.params.id
    const data = await getSurveyStats(id)
    surveyInfo.title = data.survey_title
    Object.assign(surveyStats, data)
    
    await nextTick()
    initCharts()
  } catch (error) {
    console.error('获取分析数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 初始化图表
const initCharts = () => {
  charts.forEach(chart => chart?.dispose())
  charts = []
  
  const stats = surveyStats.question_stats || []
  stats.forEach((stat, index) => {
    const chartDom = chartRefs.value[index]
    if (!chartDom) return
    
    const chart = echarts.init(chartDom)
    charts.push(chart)
    
    if (stat.question_type === 'scale') {
      // 量表题使用柱状图
      const data = stat.options_stats?.distribution || {}
      const xData = Object.keys(data).sort()
      const yData = xData.map(key => data[key])
      
      chart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: {
          type: 'category',
          data: xData,
          axisLine: { lineStyle: { color: '#e0e0e0' } }
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f0f0f0' } }
        },
        series: [{
          type: 'bar',
          data: yData,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#7aa2f7' },
              { offset: 1, color: '#9575f5' }
            ]),
            borderRadius: [4, 4, 0, 0]
          }
        }]
      })
    } else {
      // 选择题使用饼图
      const options = stat.options_stats || []
      chart.setOption({
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: '5%',
          top: 'center',
          textStyle: { fontSize: 11 }
        },
        series: [{
          type: 'pie',
          radius: ['30%', '60%'],
          center: ['35%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 6,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: { show: false },
          emphasis: {
            label: { show: true, fontSize: 12, fontWeight: 'bold' }
          },
          data: options.map((opt, i) => ({
            name: opt.option,
            value: opt.count,
            itemStyle: {
              color: ['#7aa2f7', '#67c89a', '#9575f5', '#fa916e', '#f7c95f', '#67c2e8'][i % 6]
            }
          }))
        }]
      })
    }
  })
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

// 导出数据
const handleExport = async () => {
  try {
    const blob = await exportSurveyData(route.params.id)
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    link.download = `survey_${route.params.id}_analysis.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 返回
const goBack = () => {
  router.push('/surveys')
}

// 窗口调整
const handleResize = () => {
  charts.forEach(chart => chart?.resize())
}

onMounted(() => {
  fetchAnalysis()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  charts.forEach(chart => chart?.dispose())
})
</script>

<style scoped>
.data-analysis {
  min-height: 100%;
}

.header-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.survey-info h2 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.survey-stats {
  display: flex;
  gap: 8px;
}

.chart-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.chart-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.question-num {
  font-weight: 600;
  color: #7aa2f7;
}

.question-type {
  font-size: 12px;
  color: #888;
}

.question-text {
  font-size: 14px;
  color: #333;
  margin-bottom: 16px;
  line-height: 1.6;
}

.question-chart {
  height: 250px;
}

.answer-count {
  text-align: right;
  color: #888;
  font-size: 13px;
  margin-top: 8px;
}
</style>
