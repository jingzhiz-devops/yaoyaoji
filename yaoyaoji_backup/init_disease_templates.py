"""
初始化疾病模板和建议数据
"""
from app.database import SessionLocal
from app.models.models import (
    DiseaseTemplate, DietRecommendation, ExerciseRecommendation, MealType
)


def init_templates(db):
    """初始化疾病类型模板"""
    templates = [
        {
            "disease_type": "hypertension",
            "display_name": "高血压",
            "icd10_code": "I10",
            "description": "以体循环动脉血压持续升高为主要特征的慢性病",
            "default_indicators": [
                {"name": "收缩压", "unit": "mmHg", "normal_min": 90, "normal_max": 140, "check_frequency": "daily"},
                {"name": "舒张压", "unit": "mmHg", "normal_min": 60, "normal_max": 90, "check_frequency": "daily"},
                {"name": "心率", "unit": "次/分", "normal_min": 60, "normal_max": 100, "check_frequency": "daily"}
            ]
        },
        {
            "disease_type": "hyperlipidemia",
            "display_name": "高血脂",
            "icd10_code": "E78",
            "description": "血脂水平过高，可直接引起一些严重危害人体健康的疾病",
            "default_indicators": [
                {"name": "总胆固醇", "unit": "mmol/L", "normal_min": 2.8, "normal_max": 5.2, "check_frequency": "monthly"},
                {"name": "甘油三酯", "unit": "mmol/L", "normal_min": 0, "normal_max": 1.7, "check_frequency": "monthly"},
                {"name": "高密度脂蛋白", "unit": "mmol/L", "normal_min": 1.0, "normal_max": None, "check_frequency": "monthly"},
                {"name": "低密度脂蛋白", "unit": "mmol/L", "normal_min": 0, "normal_max": 3.4, "check_frequency": "monthly"}
            ]
        },
        {
            "disease_type": "diabetes",
            "display_name": "糖尿病",
            "icd10_code": "E11",
            "description": "以高血糖为特征的代谢性疾病",
            "default_indicators": [
                {"name": "空腹血糖", "unit": "mmol/L", "normal_min": 3.9, "normal_max": 6.1, "check_frequency": "daily"},
                {"name": "餐后2小时血糖", "unit": "mmol/L", "normal_min": 3.9, "normal_max": 7.8, "check_frequency": "daily"},
                {"name": "糖化血红蛋白", "unit": "%", "normal_min": 4.0, "normal_max": 6.0, "check_frequency": "monthly"}
            ]
        }
    ]
    
    for t in templates:
        existing = db.query(DiseaseTemplate).filter_by(disease_type=t["disease_type"]).first()
        if not existing:
            db.add(DiseaseTemplate(**t))
    db.commit()


def init_diet_recommendations(db):
    """初始化饮食建议数据"""
    recommendations = [
        # 高血脂 - 通用饮食建议
        {
            "disease_type": "hyperlipidemia",
            "meal_type": None,
            "title": "高血脂饮食总则",
            "content": "控制总热量摄入，减少饱和脂肪酸和反式脂肪酸的摄入，增加膳食纤维和不饱和脂肪酸的摄入。",
            "food_suggestions": ["燕麦", "豆类", "深海鱼", "坚果", "橄榄油", "新鲜蔬果", "全谷物"],
            "food_restrictions": ["油炸食品", "动物内脏", "肥肉", "奶油", "蛋黄", "椰子油"],
            "priority": 10
        },
        # 糖尿病 - 早餐建议
        {
            "disease_type": "diabetes",
            "meal_type": MealType.BREAKFAST,
            "title": "糖尿病早餐建议",
            "content": "早餐应选择低GI食物，搭配优质蛋白质，避免精制碳水化合物。建议7:00-8:00进食。",
            "food_suggestions": ["全麦面包", "燕麦粥", "鸡蛋", "牛奶", "豆浆", "蔬菜沙拉"],
            "food_restrictions": ["白粥", "油条", "甜面包", "含糖饮料", "蜂蜜"],
            "priority": 10
        },
        # 糖尿病 - 午餐建议
        {
            "disease_type": "diabetes",
            "meal_type": MealType.LUNCH,
            "title": "糖尿病午餐建议",
            "content": "午餐注意荤素搭配，主食选择粗粮，蔬菜占一半以上。建议12:00-13:00进食。",
            "food_suggestions": ["糙米饭", "瘦肉", "鱼类", "豆腐", "绿叶蔬菜", "菌菇类"],
            "food_restrictions": ["白米饭过量", "红烧肉", "糖醋排骨", "含糖饮料"],
            "priority": 10
        },
        # 糖尿病 - 晚餐建议
        {
            "disease_type": "diabetes",
            "meal_type": MealType.DINNER,
            "title": "糖尿病晚餐建议",
            "content": "晚餐宜清淡，控制主食量，多吃蔬菜。建议18:00-19:00进食，睡前3小时不再进食。",
            "food_suggestions": ["杂粮粥", "清蒸鱼", "凉拌蔬菜", "豆制品", "西兰花", "番茄"],
            "food_restrictions": ["夜宵", "高脂肪食物", "甜点", "酒精"],
            "priority": 10
        },
        # 高血压 - 通用饮食建议
        {
            "disease_type": "hypertension",
            "meal_type": None,
            "title": "高血压饮食总则",
            "content": "遵循DASH饮食原则，低盐、低脂、高钾、高钙。每日食盐摄入不超过5克。",
            "food_suggestions": ["新鲜蔬果", "全谷物", "低脂乳制品", "鱼类", "豆类", "香蕉", "菠菜"],
            "food_restrictions": ["腌制食品", "咸菜", "加工肉类", "方便面", "高盐调味品"],
            "priority": 10
        }
    ]
    
    for r in recommendations:
        existing = db.query(DietRecommendation).filter_by(
            disease_type=r["disease_type"],
            title=r["title"]
        ).first()
        if not existing:
            db.add(DietRecommendation(**r))
    db.commit()


def init_exercise_recommendations(db):
    """初始化运动建议数据"""
    recommendations = [
        {
            "disease_type": "diabetes",
            "title": "有氧运动 - 快走",
            "exercise_type": "有氧运动",
            "duration_minutes": 30,
            "frequency_per_week": 5,
            "intensity": "moderate",
            "description": "快走是最适合糖尿病患者的运动之一，能有效降低血糖。建议餐后1小时开始，保持中等强度。",
            "precautions": "运动前检测血糖，血糖低于5.6mmol/L时先补充食物；随身携带糖果以防低血糖。",
            "priority": 10
        },
        {
            "disease_type": "diabetes",
            "title": "力量训练",
            "exercise_type": "力量训练",
            "duration_minutes": 20,
            "frequency_per_week": 3,
            "intensity": "moderate",
            "description": "适度的力量训练可以增加肌肉量，提高胰岛素敏感性。可使用弹力带或轻量哑铃。",
            "precautions": "避免憋气用力，注意呼吸节奏；有视网膜病变者避免举重。",
            "priority": 8
        },
        {
            "disease_type": "diabetes",
            "title": "太极拳",
            "exercise_type": "柔韧性运动",
            "duration_minutes": 30,
            "frequency_per_week": 3,
            "intensity": "low",
            "description": "太极拳动作缓慢柔和，有助于降低血糖、改善平衡能力和减轻压力。",
            "precautions": "注意保持呼吸平稳，避免过度弯腰或扭转。",
            "priority": 6
        },
        {
            "disease_type": "hypertension",
            "title": "有氧运动 - 慢跑",
            "exercise_type": "有氧运动",
            "duration_minutes": 30,
            "frequency_per_week": 5,
            "intensity": "moderate",
            "description": "规律的有氧运动可以有效降低血压。建议从慢跑开始，逐渐增加运动量。",
            "precautions": "血压超过180/110mmHg时不宜运动；运动中如感到头晕应立即停止。",
            "priority": 10
        },
        {
            "disease_type": "hyperlipidemia",
            "title": "有氧运动 - 游泳",
            "exercise_type": "有氧运动",
            "duration_minutes": 45,
            "frequency_per_week": 3,
            "intensity": "moderate",
            "description": "游泳是全身性有氧运动，能有效消耗脂肪，降低血脂水平。",
            "precautions": "饭后1小时再游泳；注意水温不宜过低。",
            "priority": 10
        }
    ]
    
    for r in recommendations:
        existing = db.query(ExerciseRecommendation).filter_by(
            disease_type=r["disease_type"],
            title=r["title"]
        ).first()
        if not existing:
            db.add(ExerciseRecommendation(**r))
    db.commit()


def init_all():
    """初始化所有数据"""
    db = SessionLocal()
    try:
        init_templates(db)
        init_diet_recommendations(db)
        init_exercise_recommendations(db)
        print("慢性病模板和建议数据初始化完成")
    finally:
        db.close()


if __name__ == "__main__":
    init_all()
