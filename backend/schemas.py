"""
Pydantic模型定义
用于API请求和响应的数据验证
"""
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


# ============== 用户相关模型 ==============

class UserBase(BaseModel):
    """用户基础模型"""
    phone: str
    nickname: Optional[str] = ""


class UserCreate(UserBase):
    """用户创建模型"""
    pass


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    avatar: str = ""
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== 认证相关模型 ==============

class LoginRequest(BaseModel):
    """登录请求模型"""
    phone: str
    code: str  # 验证码


class AdminLoginRequest(BaseModel):
    """管理员登录请求模型"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """注册请求模型"""
    phone: str
    nickname: str = ""


class AuthResponse(BaseModel):
    """认证响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============== 题目相关模型 ==============

class QuestionBase(BaseModel):
    """题目基础模型"""
    type: str  # single_choice, multiple_choice, scale
    content: str
    options: List[Any] = []
    sort_order: int = 0


class QuestionCreate(QuestionBase):
    """题目创建模型"""
    pass


class QuestionResponse(QuestionBase):
    """题目响应模型"""
    id: int
    
    class Config:
        from_attributes = True


# ============== 问卷相关模型 ==============

class SurveyBase(BaseModel):
    """问卷基础模型"""
    title: str
    description: str = ""


class SurveyCreate(SurveyBase):
    """问卷创建模型"""
    questions: List[QuestionCreate] = []


class SurveyResponse(SurveyBase):
    """问卷响应模型"""
    id: int
    status: str
    created_at: datetime
    question_count: int = 0
    
    class Config:
        from_attributes = True


class SurveyDetailResponse(SurveyResponse):
    """问卷详情响应模型"""
    questions: List[QuestionResponse] = []


# ============== 答案相关模型 ==============

class AnswerItem(BaseModel):
    """答案项模型"""
    question_id: int
    answer: Any  # 单选为选项索引，多选为选项索引数组，量表为数值


class SubmitAnswersRequest(BaseModel):
    """提交答案请求模型"""
    answers: List[AnswerItem]


class AnswerResponse(BaseModel):
    """答案响应模型"""
    id: int
    question_id: int
    answer: Any
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== 历史记录模型 ==============

class HistoryItem(BaseModel):
    """历史记录项"""
    survey_id: int
    survey_title: str
    submitted_at: datetime
    total_questions: int
    answered_questions: int


# ============== 统计相关模型 ==============

class StatsResponse(BaseModel):
    """统计概览响应模型"""
    total_users: int
    total_surveys: int
    total_submissions: int
    completion_rate: float
    recent_activity: List[dict]


class QuestionStats(BaseModel):
    """题目统计模型"""
    question_id: int
    question_content: str
    question_type: str
    total_answers: int
    options_stats: List[dict] = []


class SurveyStatsResponse(BaseModel):
    """问卷统计响应模型"""
    survey_id: int
    survey_title: str
    total_participants: int
    completion_rate: float
    question_stats: List[QuestionStats]
