<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card stat-users">
          <div class="stat-icon">
            <el-icon><IconUser /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_users || 0 }}</div>
            <div class="stat-label">用户总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-surveys">
          <div class="stat-icon">
            <el-icon><IconDocument /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_surveys || 0 }}</div>
            <div class="stat-label">问卷总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-submissions">
          <div class="stat-icon">
            <el-icon><IconFinished /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_submissions || 0 }}</div>
            <div class="stat-label">提交总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-rate">
          <div class="stat-icon">
            <el-icon><IconDataBoard /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ ((stats.completion_rate || 0) * 100).toFixed(1) }}%</div>
            <div class="stat-label">完成率</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>近7天提交趋势</span>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>问卷分布</span>
            </div>
          </template>
          <div ref="pieChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 近期活动 -->
    <el-card class="activity-card">
      <template #header>
        <div class="card-header">
          <span>近期活动</span>
        </div>
      </template>
      <el-table :data="recentActivity" style="width: 100%">
        <el-table-column prop="date" label="日期" width="180" />
        <el-table-column prop="count" label="提交数" width="120">
          <template #default="{ row }">
            <el-tag type="success">{{ row.count }} 次</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="趋势">
          <template #default="{ row }">
            <el-progress
              :percentage="getTrendPercentage(row.count)"
              :color="getTrendColor(row.count)"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'
import { getStats } from '../api'

// 数据
const stats = reactive({
  total_users: 0,
  total_surveys: 0,
  total_submissions: 0,
  completion_rate: 0,
  recent_activity: []
})

const loading = ref(false)

// 图表实例
let trendChart = null
let pieChart = null
const trendChartRef = ref(null)
const pieChartRef = ref(null)

// 近期活动
const recentActivity = computed(() => {
  return [...(stats.recent_activity || [])].reverse()
})

// 获取统计数据
const fetchStats = async () => {
  try {
    loading.value = true
    const data = await getStats()
    Object.assign(stats, data)
    updateCharts()
  } catch (error) {
    console.error('获取统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 更新图表
const updateCharts = () => {
  updateTrendChart()
  updatePieChart()
}

// 更新趋势图
const updateTrendChart = () => {
  if (!trendChartRef.value) return
  
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }
  
  const dates = (stats.recent_activity || []).map(item => item.date.slice(5))
  const counts = (stats.recent_activity || []).map(item => item.count)
  
  trendChart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#e0e0e0' } }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f0f0f0' } }
    },
    series: [{
      name: '提交数',
      type: 'line',
      smooth: true,
      data: counts,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(122, 162, 247, 0.4)' },
          { offset: 1, color: 'rgba(122, 162, 247, 0.05)' }
        ])
      },
      lineStyle: { color: '#7aa2f7', width: 3 },
      itemStyle: { color: '#7aa2f7' }
    }]
  })
}

// 更新饼图
const updatePieChart = () => {
  if (!pieChartRef.value) return
  
  if (!pieChart) {
    pieChart = echarts.init(pieChartRef.value)
  }
  
  pieChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      data: [
        { value: stats.total_submissions || 0, name: '已完成', itemStyle: { color: '#7aa2f7' } },
        { value: Math.max(0, (stats.total_users || 0) * (stats.total_surveys || 0) - (stats.total_submissions || 0)), name: '未完成', itemStyle: { color: '#e0e0e0' } }
      ]
    }]
  })
}

// 计算趋势百分比
const getTrendPercentage = (count) => {
  const max = Math.max(...(stats.recent_activity || []).map(item => item.count), 1)
  return Math.round((count / max) * 100)
}

// 获取趋势颜色
const getTrendColor = (count) => {
  const avg = (stats.total_submissions || 0) / 7
  if (count > avg * 1.5) return '#67c23a'
  if (count > avg) return '#7aa2f7'
  return '#e6a23c'
}

// 窗口调整时重绘图表
const handleResize = () => {
  trendChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  fetchStats()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.dashboard {
  min-height: 100%;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-users .stat-icon {
  background: rgba(122, 162, 247, 0.15);
  color: #7aa2f7;
}

.stat-surveys .stat-icon {
  background: rgba(103, 232, 153, 0.15);
  color: #67c89a;
}

.stat-submissions .stat-icon {
  background: rgba(149, 117, 250, 0.15);
  color: #9575f5;
}

.stat-rate .stat-icon {
  background: rgba(250, 145, 110, 0.15);
  color: #fa916e;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e1e2e;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #888;
  margin-top: 4px;
}

/* 图表卡片 */
.chart-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  color: #1e1e2e;
}

.chart-container {
  height: 280px;
}

/* 活动卡片 */
.activity-card {
  border-radius: 12px;
}
</style>
