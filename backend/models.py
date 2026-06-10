"""
数据模型定义
包含所有数据库表的ORM模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=True)  # 管理员用户名
    nickname = Column(String(50), default="")
    avatar = Column(String(500), default="")
    password_hash = Column(String(255), nullable=True)  # 预留，后续支持密码登录
    is_admin = Column(Integer, default=0)  # 是否管理员
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联答案
    answers = relationship("Answer", back_populates="user")


class Survey(Base):
    """问卷表"""
    __tablename__ = "surveys"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    status = Column(String(20), default="active")  # active, inactive
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联题目
    questions = relationship("Question", back_populates="survey", order_by="Question.sort_order")
    # 关联答案
    answers = relationship("Answer", back_populates="survey")


class Question(Base):
    """题目表"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    type = Column(String(50), nullable=False)  # single_choice, multiple_choice, scale
    content = Column(Text, nullable=False)
    options = Column(JSON, default=[])  # 选项JSON数组
    sort_order = Column(Integer, default=0)
    
    # 关联问卷
    survey = relationship("Survey", back_populates="questions")
    # 关联答案
    answers = relationship("Answer", back_populates="question")


class Answer(Base):
    """答案表"""
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer = Column(JSON, nullable=False)  # 存储答案内容
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联用户
    user = relationship("User", back_populates="answers")
    # 关联问卷
    survey = relationship("Survey", back_populates="answers")
    # 关联题目
    question = relationship("Question", back_populates="answers")
