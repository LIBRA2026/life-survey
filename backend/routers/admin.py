"""
管理后台路由模块
处理统计、用户管理、数据导出等管理员接口
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from io import BytesIO
import pandas as pd
from database import get_db
from models import Survey, Question, Answer, User
from schemas import StatsResponse, SurveyStatsResponse, QuestionStats

router = APIRouter(prefix="/api/admin", tags=["管理"])


@router.get("/stats", response_model=StatsResponse, summary="获取统计概览")
def get_stats(db: Session = Depends(get_db)):
    """获取系统统计概览"""
    # 用户总数
    total_users = db.query(func.count(User.id)).scalar()
    
    # 问卷总数
    total_surveys = db.query(func.count(Survey.id)).scalar()
    
    # 提交总数
    total_submissions = db.query(func.count(Answer.id)).scalar()
    
    # 计算完成率
    completion_rate = 0.0
    if total_users > 0 and total_surveys > 0:
        # 计算每个用户-问卷组合的完成情况
        user_survey_combos = total_users * total_surveys
        if user_survey_combos > 0:
            # 简化计算：实际提交数 / 预期提交数
            unique_user_survey = db.query(
                func.count(func.distinct(Answer.user_id + Answer.survey_id * 10000))
            ).scalar()
            completion_rate = round(min(total_submissions / max(unique_user_survey, 1), 1.0), 2)
    
    # 最近活动（最近7天每日提交数）
    recent_activity = []
    for i in range(7):
        day = datetime.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0)
        day_end = day.replace(hour=23, minute=59, second=59)
        
        count = db.query(func.count(Answer.id)).filter(
            Answer.created_at >= day_start,
            Answer.created_at <= day_end
        ).scalar()
        
        recent_activity.append({
            "date": day.strftime("%Y-%m-%d"),
            "count": count
        })
    
    return StatsResponse(
        total_users=total_users,
        total_surveys=total_surveys,
        total_submissions=total_submissions,
        completion_rate=completion_rate,
        recent_activity=recent_activity
    )


@router.get("/surveys/{survey_id}/stats", response_model=SurveyStatsResponse, summary="获取问卷统计")
def get_survey_stats(
    survey_id: int,
    db: Session = Depends(get_db)
):
    """获取单个问卷的详细统计"""
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    
    # 获取题目
    questions = db.query(Question).filter(
        Question.survey_id == survey_id
    ).order_by(Question.sort_order).all()
    
    # 参与者总数
    total_participants = db.query(
        func.count(func.distinct(Answer.user_id))
    ).filter(Answer.survey_id == survey_id).scalar()
    
    # 完成率
    total_questions = len(questions)
    completion_rate = 0.0
    if total_participants > 0 and total_questions > 0:
        total_answers = db.query(func.count(Answer.id)).filter(
            Answer.survey_id == survey_id
        ).scalar()
        completion_rate = round(total_answers / (total_participants * total_questions), 2)
    
    # 每道题的统计
    question_stats = []
    for question in questions:
        # 获取该题的所有答案
        answers = db.query(Answer).filter(
            Answer.question_id == question.id
        ).all()
        
        total_answers = len(answers)
        options_stats = []
        
        if question.type == "single_choice" or question.type == "multiple_choice":
            # 统计每个选项的选择次数
            options = question.options or []
            for idx, option in enumerate(options):
                count = sum(1 for a in answers if idx in (a.answer if isinstance(a.answer, list) else [a.answer]))
                percentage = round(count / max(total_answers, 1) * 100, 1)
                options_stats.append({
                    "option": option,
                    "option_index": idx,
                    "count": count,
                    "percentage": percentage
                })
        
        elif question.type == "scale":
            # 量表题统计
            values = [a.answer for a in answers if isinstance(a.answer, (int, float))]
            if values:
                options_stats = {
                    "average": round(sum(values) / len(values), 2),
                    "min": min(values),
                    "max": max(values),
                    "distribution": {
                        str(i): values.count(i) for i in range(1, 6) if i in values or True
                    }
                }
        
        question_stats.append(QuestionStats(
            question_id=question.id,
            question_content=question.content,
            question_type=question.type,
            total_answers=total_answers,
            options_stats=options_stats
        ))
    
    return SurveyStatsResponse(
        survey_id=survey_id,
        survey_title=survey.title,
        total_participants=total_participants,
        completion_rate=completion_rate,
        question_stats=question_stats
    )


@router.get("/users", summary="获取用户列表")
def get_users(
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    query = db.query(User)
    
    if keyword:
        query = query.filter(
            (User.phone.contains(keyword)) | 
            (User.nickname.contains(keyword))
        )
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    # 获取每个用户的提交统计
    user_list = []
    for user in users:
        submission_count = db.query(func.count(Answer.id)).filter(
            Answer.user_id == user.id
        ).scalar()
        
        user_list.append({
            "id": user.id,
            "phone": user.phone,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "created_at": user.created_at,
            "submission_count": submission_count
        })
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": user_list
    }


@router.get("/surveys", summary="获取问卷列表（管理）")
def get_surveys_admin(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取所有问卷列表（管理员视角）"""
    query = db.query(Survey)
    if status:
        query = query.filter(Survey.status == status)
    
    surveys = query.order_by(Survey.created_at.desc()).all()
    
    result = []
    for survey in surveys:
        question_count = db.query(func.count(Question.id)).filter(
            Question.survey_id == survey.id
        ).scalar()
        participant_count = db.query(
            func.count(func.distinct(Answer.user_id))
        ).filter(Answer.survey_id == survey.id).scalar()
        
        result.append({
            "id": survey.id,
            "title": survey.title,
            "description": survey.description,
            "status": survey.status,
            "created_at": survey.created_at,
            "question_count": question_count,
            "participant_count": participant_count
        })
    
    return result


@router.post("/surveys", summary="创建问卷")
def create_survey(
    title: str,
    description: str = "",
    db: Session = Depends(get_db)
):
    """创建新问卷"""
    survey = Survey(
        title=title,
        description=description,
        status="active"
    )
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return {"id": survey.id, "message": "创建成功"}


@router.put("/surveys/{survey_id}", summary="更新问卷")
def update_survey(
    survey_id: int,
    title: str = None,
    description: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """更新问卷信息"""
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    
    if title:
        survey.title = title
    if description is not None:
        survey.description = description
    if status:
        survey.status = status
    
    db.commit()
    return {"message": "更新成功"}


@router.post("/surveys/{survey_id}/questions", summary="添加题目")
def add_question(
    survey_id: int,
    question_type: str,
    content: str,
    options: List = [],
    sort_order: int = 0,
    db: Session = Depends(get_db)
):
    """向问卷添加题目"""
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    
    question = Question(
        survey_id=survey_id,
        type=question_type,
        content=content,
        options=options,
        sort_order=sort_order
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return {"id": question.id, "message": "添加成功"}


@router.delete("/surveys/{survey_id}", summary="删除问卷")
def delete_survey(
    survey_id: int,
    db: Session = Depends(get_db)
):
    """删除问卷"""
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    
    # 先删除关联的答案
    db.query(Answer).filter(Answer.survey_id == survey_id).delete()
    # 删除题目
    db.query(Question).filter(Question.survey_id == survey_id).delete()
    # 删除问卷
    db.delete(survey)
    db.commit()
    
    return {"message": "删除成功"}


@router.get("/export/{survey_id}", summary="导出问卷数据")
def export_survey_data(
    survey_id: int,
    db: Session = Depends(get_db)
):
    """导出问卷数据为Excel"""
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    
    # 获取题目
    questions = db.query(Question).filter(
        Question.survey_id == survey_id
    ).order_by(Question.sort_order).all()
    
    # 获取所有提交用户
    user_ids = db.query(func.distinct(Answer.user_id)).filter(
        Answer.survey_id == survey_id
    ).all()
    user_ids = [uid[0] for uid in user_ids]
    
    # 构建Excel数据
    data = []
    for user_id in user_ids:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            continue
        
        row = {
            "用户手机": user.phone,
            "用户昵称": user.nickname,
            "提交时间": ""
        }
        
        for question in questions:
            answer = db.query(Answer).filter(
                Answer.user_id == user_id,
                Answer.survey_id == survey_id,
                Answer.question_id == question.id
            ).first()
            
            if answer:
                if question.type == "multiple_choice":
                    options = question.options or []
                    selected = [options[i] for i in answer.answer if 0 <= i < len(options)]
                    row[f"Q{question.sort_order + 1}"] = ", ".join(selected)
                elif question.type == "single_choice":
                    options = question.options or []
                    idx = answer.answer if isinstance(answer.answer, int) else 0
                    row[f"Q{question.sort_order + 1}"] = options[idx] if 0 <= idx < len(options) else ""
                else:
                    row[f"Q{question.sort_order + 1}"] = answer.answer
                
                if not row.get("提交时间"):
                    row["提交时间"] = answer.created_at.strftime("%Y-%m-%d %H:%M:%S")
            else:
                row[f"Q{question.sort_order + 1}"] = ""
        
        data.append(row)
    
    # 创建DataFrame并导出
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='问卷数据')
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=survey_{survey_id}_data.xlsx"
        }
    )
