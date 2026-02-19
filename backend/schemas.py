TABLES = {
    "T_JCXX": {
        "description": "检查信息表 - 患者基本信息和主病理报告",
        "fields": [
            {"name": "F_BLH", "type": "VARCHAR", "description": "病理号(主键)"},
            {"name": "F_XM", "type": "VARCHAR", "description": "姓名"},
            {"name": "F_XB", "type": "VARCHAR", "description": "性别"},
            {"name": "F_NL", "type": "VARCHAR", "description": "年龄"},
            {"name": "F_BRBH", "type": "VARCHAR", "description": "病人编号"},
            {"name": "F_ZYH", "type": "VARCHAR", "description": "住院号"},
            {"name": "F_MZH", "type": "VARCHAR", "description": "门诊号"},
            {"name": "F_SJKS", "type": "VARCHAR", "description": "送检科室"},
            {"name": "F_BGYS", "type": "VARCHAR", "description": "报告医生"},
            {"name": "F_SHYS", "type": "VARCHAR", "description": "审核医生"},
            {"name": "F_BGRQ", "type": "DATE", "description": "报告日期"},
            {"name": "F_BGZT", "type": "VARCHAR", "description": "报告状态"},
            {"name": "F_BLZD", "type": "TEXT", "description": "病理诊断"},
            {"name": "F_JXSJ", "type": "TEXT", "description": "镜下所见"},
            {"name": "F_RYSJ", "type": "TEXT", "description": "肉眼所见"},
            {"name": "F_LCZD", "type": "VARCHAR", "description": "临床诊断"},
            {"name": "F_BBMC", "type": "VARCHAR", "description": "标本名称"},
            {"name": "F_SDRQ", "type": "DATE", "description": "收到日期"},
            {"name": "F_QCYS", "type": "VARCHAR", "description": "取材医生"},
            {"name": "F_QCRQ", "type": "DATE", "description": "取材日期"},
            {"name": "F_LKZS", "type": "INT", "description": "蜡块总数"},
            {"name": "F_CKZS", "type": "INT", "description": "材块总数"},
            {"name": "F_SFDY", "type": "VARCHAR", "description": "是否打印"},
            {"name": "F_GDZT", "type": "VARCHAR", "description": "归档状态"},
            {"name": "F_FBSJ", "type": "DATETIME", "description": "发布时间"},
        ]
    },
    "T_BCBG": {
        "description": "补充报告表 - 补充报告信息(主要用于免疫组化报告)",
        "fields": [
            {"name": "F_ID", "type": "INT", "description": "主键ID"},
            {"name": "F_BLH", "type": "VARCHAR", "description": "病理号(外键)"},
            {"name": "F_BC_BGXH", "type": "INT", "description": "补充报告序号"},
            {"name": "F_BC_BGYS", "type": "VARCHAR", "description": "报告医生"},
            {"name": "F_BC_SHYS", "type": "VARCHAR", "description": "审核医生"},
            {"name": "F_BCZD", "type": "TEXT", "description": "补充诊断"},
            {"name": "F_BC_BGZT", "type": "VARCHAR", "description": "报告状态"},
            {"name": "F_BC_FBSJ", "type": "DATETIME", "description": "发布时间"},
        ]
    },
    "T_BDBG": {
        "description": "冰冻报告表 - 冰冻病理报告信息",
        "fields": [
            {"name": "F_ID", "type": "INT", "description": "主键ID"},
            {"name": "F_BLH", "type": "VARCHAR", "description": "病理号(外键)"},
            {"name": "F_BD_BGXH", "type": "INT", "description": "冰冻报告序号"},
            {"name": "F_BD_BGYS", "type": "VARCHAR", "description": "报告医生"},
            {"name": "F_BDZD", "type": "TEXT", "description": "冰冻诊断"},
            {"name": "F_BC_BGZT", "type": "VARCHAR", "description": "报告状态"},
            {"name": "F_BD_FBSJ", "type": "DATETIME", "description": "发布时间"},
            {"name": "F_BD_BBMC", "type": "VARCHAR", "description": "标本名称"},
        ]
    },
    "T_LK": {
        "description": "蜡块表 - 蜡块信息",
        "fields": [
            {"name": "F_ID", "type": "INT", "description": "主键ID"},
            {"name": "F_BLH", "type": "VARCHAR", "description": "病理号(外键)"},
            {"name": "F_LKH", "type": "VARCHAR", "description": "蜡块号"},
            {"name": "F_LKZT", "type": "VARCHAR", "description": "蜡块状态"},
            {"name": "F_QPZT", "type": "VARCHAR", "description": "切片状态"},
            {"name": "F_CZY", "type": "VARCHAR", "description": "操作员"},
            {"name": "F_BMSJ", "type": "DATETIME", "description": "包埋时间"},
            {"name": "F_GDZT", "type": "VARCHAR", "description": "归档状态"},
        ]
    },
    "T_QP": {
        "description": "切片表 - 切片信息",
        "fields": [
            {"name": "F_ID", "type": "INT", "description": "主键ID"},
            {"name": "F_BLH", "type": "VARCHAR", "description": "病理号(外键)"},
            {"name": "F_LKH", "type": "VARCHAR", "description": "蜡块号(外键关联T_LK)"},
            {"name": "F_QPTMH", "type": "VARCHAR", "description": "切片条码号"},
            {"name": "F_QPXH", "type": "INT", "description": "切片序号"},
            {"name": "F_CZY", "type": "VARCHAR", "description": "操作员"},
            {"name": "F_QPSJ", "type": "DATETIME", "description": "切片时间"},
            {"name": "F_QPZT", "type": "VARCHAR", "description": "切片状态"},
            {"name": "F_GDZT", "type": "VARCHAR", "description": "归档状态"},
            {"name": "F_TJH", "type": "VARCHAR", "description": "特检号"},
            {"name": "F_RSY", "type": "VARCHAR", "description": "染色员"},
            {"name": "F_RSSJ", "type": "DATETIME", "description": "染色时间"},
        ]
    },
    "T_JHP": {
        "description": "借还片表 - 蜡块/切片借阅归还记录",
        "fields": [
            {"name": "F_ID", "type": "INT", "description": "主键ID"},
            {"name": "F_BLH", "type": "VARCHAR", "description": "病理号(外键)"},
            {"name": "F_XM", "type": "VARCHAR", "description": "姓名"},
            {"name": "F_JHPBH", "type": "VARCHAR", "description": "借还片编号"},
            {"name": "F_JHPZT", "type": "VARCHAR", "description": "借还片状态"},
            {"name": "F_JCSJ", "type": "DATETIME", "description": "借出时间"},
            {"name": "F_GHSJ", "type": "DATETIME", "description": "归还时间"},
            {"name": "F_JYR", "type": "VARCHAR", "description": "借阅人"},
        ]
    },
    "T_TX": {
        "description": "图像表 - 患者病理图像记录",
        "fields": [
            {"name": "F_ID", "type": "INT", "description": "主键ID"},
            {"name": "F_BLH", "type": "VARCHAR", "description": "病理号(外键)"},
            {"name": "F_TXM", "type": "VARCHAR", "description": "图像名"},
            {"name": "F_TXSM", "type": "VARCHAR", "description": "图像说明"},
            {"name": "F_TXLB", "type": "VARCHAR", "description": "图像类别"},
            {"name": "F_CZY", "type": "VARCHAR", "description": "操作员"},
        ]
    },
    "T_BGHJ": {
        "description": "报告痕迹表 - 从登记到报告发放的所有动作记录",
        "fields": [
            {"name": "F_ID", "type": "INT", "description": "主键ID"},
            {"name": "F_BLH", "type": "VARCHAR", "description": "病理号(外键)"},
            {"name": "F_RQ", "type": "DATE", "description": "日期"},
            {"name": "F_CZY", "type": "VARCHAR", "description": "操作员"},
            {"name": "F_DZ", "type": "VARCHAR", "description": "动作"},
            {"name": "F_NR", "type": "TEXT", "description": "内容"},
            {"name": "F_EXEMC", "type": "VARCHAR", "description": "工作站类型(QP/BM/BPS/RPT)"},
        ]
    },
    "T_JSYZ": {
        "description": "技术医嘱表 - 患者技术医嘱信息",
        "fields": [
            {"name": "F_ID", "type": "INT", "description": "主键ID"},
            {"name": "F_BLH", "type": "VARCHAR", "description": "病理号(外键)"},
            {"name": "F_JSYZH", "type": "VARCHAR", "description": "技术医嘱号"},
            {"name": "F_YZLX", "type": "VARCHAR", "description": "医嘱类型"},
            {"name": "F_LKH", "type": "VARCHAR", "description": "蜡块号(外键)"},
            {"name": "F_SQYS", "type": "VARCHAR", "description": "申请医生"},
            {"name": "F_SQSJ", "type": "DATETIME", "description": "申请时间"},
            {"name": "F_YZZT", "type": "VARCHAR", "description": "医嘱状态"},
        ]
    },
    "T_TJYZ": {
        "description": "特检医嘱表 - 患者特检医嘱(免疫组化等)",
        "fields": [
            {"name": "F_ID", "type": "INT", "description": "主键ID"},
            {"name": "F_BLH", "type": "VARCHAR", "description": "病理号(外键)"},
            {"name": "F_TJYZH", "type": "VARCHAR", "description": "特检医嘱号"},
            {"name": "F_YZLX", "type": "VARCHAR", "description": "医嘱类型"},
            {"name": "F_LKH", "type": "VARCHAR", "description": "蜡块号(外键)"},
            {"name": "F_BJW", "type": "VARCHAR", "description": "标记物"},
            {"name": "F_SQYS", "type": "VARCHAR", "description": "申请医生"},
            {"name": "F_YZZT", "type": "VARCHAR", "description": "医嘱状态"},
            {"name": "F_ZXSJ", "type": "DATETIME", "description": "执行时间"},
            {"name": "F_TJH", "type": "VARCHAR", "description": "特检号"},
            {"name": "F_ZLBL", "type": "VARCHAR", "description": "肿瘤比例"},
        ]
    },
    "T_QCMX": {
        "description": "取材明细表 - 取材明细信息",
        "fields": [
            {"name": "F_ID", "type": "INT", "description": "主键ID"},
            {"name": "F_BLH", "type": "VARCHAR", "description": "病理号(外键)"},
            {"name": "F_QCXH", "type": "INT", "description": "取材序号"},
            {"name": "F_ZZMC", "type": "VARCHAR", "description": "组织名称"},
            {"name": "F_CKS", "type": "INT", "description": "材块数"},
            {"name": "F_QCYS", "type": "VARCHAR", "description": "取材医生"},
            {"name": "F_BMZT", "type": "VARCHAR", "description": "包埋状态"},
        ]
    },
    "T_TBS_BG": {
        "description": "TBS报告表 - 结构化报告字段内容",
        "fields": [
            {"name": "F_BLH", "type": "VARCHAR", "description": "病理号(外键/主键)"},
            {"name": "F_TBS_JYFF", "type": "VARCHAR", "description": "检验方法"},
            {"name": "F_TBSZD", "type": "TEXT", "description": "TBS诊断"},
            {"name": "F_TBS_BBMYD", "type": "VARCHAR", "description": "标本满意度"},
            {"name": "F_TBS_YZCD", "type": "VARCHAR", "description": "炎症程度"},
            {"name": "F_TBS_XBL", "type": "VARCHAR", "description": "细胞量"},
        ]
    },
}
