"""
问卷路由模块
处理问卷列表、详情、提交等接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from database import get_db
from models import Survey, Question, Answer, User
from schemas import (
    SurveyResponse, SurveyDetailResponse, QuestionResponse,
    SubmitAnswersRequest, HistoryItem
)
from auth import get_current_user

router = APIRouter(prefix="/api", tags=["问卷"])


@router.get("/surveys", response_model=List[SurveyResponse], summary="获取问卷列表")
def get_surveys(
    status: str = "active",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取问卷列表"""
    query = db.query(Survey)
    if status:
        query = query.filter(Survey.status == status)
    
    surveys = query.order_by(Survey.created_at.desc()).all()
    result = []
    for survey in surveys:
        question_count = db.query(func.count(Question.id)).filter(
            Question.survey_id == survey.id
        ).scalar()
        result.append(SurveyResponse(
            id=survey.id,
            title=survey.title,
            description=survey.description,
            status=survey.status,
            created_at=survey.created_at,
            question_count=question_count
        ))
    return result


@router.get("/surveys/{survey_id}", response_model=SurveyDetailResponse, summary="获取问卷详情")
def get_survey_detail(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取问卷详情，包含所有题目"""
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    
    # 获取题目
    questions = db.query(Question).filter(
        Question.survey_id == survey_id
    ).order_by(Question.sort_order).all()
    
    return SurveyDetailResponse(
        id=survey.id,
        title=survey.title,
        description=survey.description,
        status=survey.status,
        created_at=survey.created_at,
        question_count=len(questions),
        questions=[QuestionResponse.model_validate(q) for q in questions]
    )


@router.post("/surveys/{survey_id}/submit", summary="提交问卷答案")
def submit_survey(
    survey_id: int,
    request: SubmitAnswersRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """提交问卷答案"""
    # 检查问卷是否存在
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    
    # 检查是否已提交过
    existing_answers = db.query(Answer).filter(
        Answer.user_id == current_user.id,
        Answer.survey_id == survey_id
    ).first()
    if existing_answers:
        raise HTTPException(status_code=400, detail="您已提交过此问卷")
    
    # 保存答案
    for answer_item in request.answers:
        # 验证题目是否存在
        question = db.query(Question).filter(
            Question.id == answer_item.question_id,
            Question.survey_id == survey_id
        ).first()
        if not question:
            raise HTTPException(
                status_code=400,
                detail=f"题目{answer_item.question_id}不存在"
            )
        
        answer = Answer(
            user_id=current_user.id,
            survey_id=survey_id,
            question_id=answer_item.question_id,
            answer=answer_item.answer
        )
        db.add(answer)
    
    db.commit()
    return {"message": "提交成功"}


@router.get("/user/profile", summary="获取用户信息")
def get_profile(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "phone": current_user.phone,
        "nickname": current_user.nickname,
        "avatar": current_user.avatar,
        "created_at": current_user.created_at
    }


@router.get("/user/history", response_model=List[HistoryItem], summary="获取参与历史")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户参与问卷的历史记录"""
    # 获取用户参与的所有问卷
    user_answers = db.query(Answer.survey_id, func.count(Answer.id).label('answer_count')).filter(
        Answer.user_id == current_user.id
    ).group_by(Answer.survey_id).all()
    
    history = []
    for survey_id, answer_count in user_answers:
        survey = db.query(Survey).filter(Survey.id == survey_id).first()
        if survey:
            total_questions = db.query(func.count(Question.id)).filter(
                Question.survey_id == survey_id
            ).scalar()
            
            # 获取最新提交时间
            latest_answer = db.query(Answer).filter(
                Answer.user_id == current_user.id,
                Answer.survey_id == survey_id
            ).order_by(Answer.created_at.desc()).first()
            
            history.append(HistoryItem(
                survey_id=survey_id,
                survey_title=survey.title,
                submitted_at=latest_answer.created_at if latest_answer else None,
                total_questions=total_questions,
                answered_questions=answer_count
            ))
    
    return history


@router.get("/surveys/{survey_id}/result", summary="获取问卷结果")
def get_survey_result(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户填写的问卷结果"""
    # 检查是否已提交
    answers = db.query(Answer).filter(
        Answer.user_id == current_user.id,
        Answer.survey_id == survey_id
    ).all()
    
    if not answers:
        raise HTTPException(status_code=400, detail="您尚未提交此问卷")
    
    # 获取问卷信息
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    
    # 构建结果数据
    result = {
        "survey_title": survey.title,
        "questions": []
    }
    
    for answer in answers:
        question = db.query(Question).filter(Question.id == answer.question_id).first()
        result["questions"].append({
            "content": question.content,
            "type": question.type,
            "options": question.options,
            "answer": answer.answer
        })
    
    return result
