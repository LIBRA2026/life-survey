"""
初始化示例数据脚本
创建完整的人生观调研问卷示例数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, init_db
from models import Survey, Question, User
from auth import get_password_hash

def init_sample_data():
    """初始化示例问卷数据"""
    init_db()
    db = SessionLocal()
    
    # 创建admin用户
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            phone="13800000000",
            nickname="管理员",
            password_hash=get_password_hash("admin"),
            is_admin=True
        )
        db.add(admin)
        print("创建管理员用户: admin/admin")
    
    # 检查是否已有数据
    existing = db.query(Survey).first()
    if existing:
        print("数据已存在，跳过初始化")
        db.close()
        return
    
    print("开始初始化示例数据...")
    
    # 创建人生观调研问卷
    survey = Survey(
        title="人生观调研问卷",
        description="欢迎参加人生观调研！本问卷旨在了解您对人生意义、幸福观、价值观等方面的看法，答案无对错之分，请根据您的真实想法填写。完成问卷后，您将获得专属的'人生观画像'分析结果。",
        status="active"
    )
    db.add(survey)
    db.commit()
    db.refresh(survey)
    
    print(f"创建问卷: {survey.title} (ID: {survey.id})")
    
    # 定义题目
    questions = [
        # ==================== 第一部分：人生意义 ====================
        {
            "type": "single_choice",
            "content": "您认为人生的终极意义是什么？",
            "options": [
                "追求个人幸福与自我实现",
                "为社会和他人创造价值",
                "体验生命中的各种经历",
                "遵循宗教或哲学指引",
                "没有固定意义，由自己赋予"
            ],
            "sort_order": 1
        },
        {
            "type": "single_choice",
            "content": "您对'成功'的定义最接近以下哪一项？",
            "options": [
                "拥有高收入和物质财富",
                "在事业上取得成就",
                "家庭和睦、亲人健康",
                "内心平静、精神充实",
                "对社会有积极贡献"
            ],
            "sort_order": 2
        },
        {
            "type": "scale",
            "content": "您对'人生目标'的清晰程度如何？（1=完全模糊，5=非常清晰）",
            "options": ["1", "2", "3", "4", "5"],
            "sort_order": 3
        },
        {
            "type": "single_choice",
            "content": "当面对人生重大抉择时，您通常会？",
            "options": [
                "听从自己内心的声音",
                "参考家人朋友的建议",
                "理性分析利弊后决定",
                "顺其自然，看情况发展",
                "寻求专业人士指导"
            ],
            "sort_order": 4
        },
        
        # ==================== 第二部分：幸福观 ====================
        {
            "type": "multiple_choice",
            "content": "以下哪些因素对您的幸福感影响最大？（可多选）",
            "options": [
                "健康状况",
                "家庭关系",
                "工作/事业",
                "经济状况",
                "人际关系",
                "个人成长",
                "兴趣爱好",
                "社会认同"
            ],
            "sort_order": 5
        },
        {
            "type": "scale",
            "content": "总体而言，您对目前生活满意度打几分？（1=很不满意，5=非常满意）",
            "options": ["1", "2", "3", "4", "5"],
            "sort_order": 6
        },
        {
            "type": "single_choice",
            "content": "您认为幸福的主要来源是？",
            "options": [
                "物质享受和生活条件",
                "精神层面的满足感",
                "与家人朋友的情感连接",
                "个人成就和自我实现",
                "帮助他人和社会贡献"
            ],
            "sort_order": 7
        },
        {
            "type": "scale",
            "content": "您觉得生活中'快乐'和'意义'哪个更重要？（1=快乐更重要，5=意义更重要）",
            "options": ["1", "2", "3", "4", "5"],
            "sort_order": 8
        },
        
        # ==================== 第三部分：价值观 ====================
        {
            "type": "multiple_choice",
            "content": "您最看重的人生价值有哪些？（可多选）",
            "options": [
                "诚实守信",
                "自由独立",
                "责任担当",
                "勤奋努力",
                "宽容理解",
                "创新进取",
                "感恩回报",
                "平衡和谐"
            ],
            "sort_order": 9
        },
        {
            "type": "single_choice",
            "content": "当个人利益与集体利益发生冲突时，您通常会？",
            "options": [
                "优先考虑集体利益",
                "优先保护个人利益",
                "努力寻求双赢方案",
                "视具体情况而定",
                "遵循道德和法律底线"
            ],
            "sort_order": 10
        },
        {
            "type": "scale",
            "content": "您对传统文化的认同程度如何？（1=不认同，5=非常认同）",
            "options": ["1", "2", "3", "4", "5"],
            "sort_order": 11
        },
        
        # ==================== 第四部分：社会责任 ====================
        {
            "type": "single_choice",
            "content": "您认为个人对社会应承担怎样的责任？",
            "options": [
                "遵纪守法，履行公民义务",
                "积极参与公益活动",
                "做好本职工作就是贡献",
                "有能力时多帮助他人",
                "没有强制责任，看个人意愿"
            ],
            "sort_order": 12
        },
        {
            "type": "scale",
            "content": "您参与志愿服务或公益活动的频率如何？（1=从不，5=经常）",
            "options": ["1", "2", "3", "4", "5"],
            "sort_order": 13
        },
        {
            "type": "multiple_choice",
            "content": "您关注或参与过哪些社会议题？（可多选）",
            "options": [
                "环境保护",
                "教育公平",
                "医疗健康",
                "养老问题",
                "贫富差距",
                "乡村振兴",
                "科技创新",
                "文化传承"
            ],
            "sort_order": 14
        },
        
        # ==================== 第五部分：人际关系 ====================
        {
            "type": "single_choice",
            "content": "在您看来，最理想的人际关系是？",
            "options": [
                "亲密无间，彼此透明",
                "保持适当距离，互相尊重",
                "互利共赢，各取所需",
                "君子之交，淡如水",
                "因人而异，灵活处理"
            ],
            "sort_order": 15
        },
        {
            "type": "scale",
            "content": "您对目前的人际关系满意程度如何？（1=很不满意，5=非常满意）",
            "options": ["1", "2", "3", "4", "5"],
            "sort_order": 16
        },
        {
            "type": "multiple_choice",
            "content": "当您遇到困难时，通常会向谁寻求帮助？（可多选）",
            "options": [
                "家人",
                "配偶/恋人",
                "朋友",
                "同事/同学",
                "专业人士",
                "独自解决",
                "网络社群",
                "不寻求帮助"
            ],
            "sort_order": 17
        },
        {
            "type": "single_choice",
            "content": "您更倾向于建立怎样的社交圈？",
            "options": [
                "小而精的知心圈子",
                "广泛交友，多认识人",
                "基于兴趣的圈子",
                "工作和业务的圈子",
                "随缘，不刻意经营"
            ],
            "sort_order": 18
        },
        
        # ==================== 第六部分：自我认知 ====================
        {
            "type": "scale",
            "content": "您对自我的了解程度如何？（1=不了解自己，5=非常了解）",
            "options": ["1", "2", "3", "4", "5"],
            "sort_order": 19
        },
        {
            "type": "single_choice",
            "content": "您如何看待自己的优点和缺点？",
            "options": [
                "坦然接受，包容自己",
                "努力改进缺点",
                "扬长避短",
                "顺其自然，不过分在意",
                "经常反思总结"
            ],
            "sort_order": 20
        },
        {
            "type": "scale",
            "content": "您对改变和成长的开放程度如何？（1=抗拒改变，5=积极拥抱变化）",
            "options": ["1", "2", "3", "4", "5"],
            "sort_order": 21
        },
        {
            "type": "single_choice",
            "content": "面对挫折和失败时，您通常会？",
            "options": [
                "总结教训，重新尝试",
                "暂时休息，调整心态",
                "寻求他人帮助",
                "逃避，不愿面对",
                "分析原因，制定计划"
            ],
            "sort_order": 22
        },
        
        # ==================== 第七部分：未来展望 ====================
        {
            "type": "scale",
            "content": "您对未来的态度是？（1=悲观担忧，5=乐观期待）",
            "options": ["1", "2", "3", "4", "5"],
            "sort_order": 23
        },
        {
            "type": "single_choice",
            "content": "您希望在5年后成为怎样的人？",
            "options": [
                "事业有成的人",
                "家庭幸福的人",
                "精神富足的人",
                "对社会有贡献的人",
                "健康快乐的人",
                "还没想好"
            ],
            "sort_order": 24
        },
        {
            "type": "multiple_choice",
            "content": "您未来最想实现的愿望有哪些？（可多选）",
            "options": [
                "财务自由",
                "健康的身体",
                "美满的家庭",
                "称心的事业",
                "自我成长",
                "旅行探索",
                "帮助他人",
                "生活平衡"
            ],
            "sort_order": 25
        }
    ]
    
    # 批量创建题目
    for q in questions:
        question = Question(
            survey_id=survey.id,
            type=q["type"],
            content=q["content"],
            options=q["options"],
            sort_order=q["sort_order"]
        )
        db.add(question)
    
    db.commit()
    print(f"成功创建 {len(questions)} 道题目")
    print("\n初始化完成！")
    print("="*50)
    print("人生观调研问卷已创建，包含以下维度：")
    print("  1. 人生意义（4题）")
    print("  2. 幸福观（4题）")
    print("  3. 价值观（3题）")
    print("  4. 社会责任（3题）")
    print("  5. 人际关系（4题）")
    print("  6. 自我认知（4题）")
    print("  7. 未来展望（3题）")
    print("="*50)
    
    db.close()


if __name__ == "__main__":
    init_sample_data()
