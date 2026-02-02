"""
蒲县产品标准配置(基于附件数据)

图片资源说明：
================
图片文件应放置在以下位置：

【开发环境】
  项目根目录/static/images/
  ├── products/           # 产品图片
  │   ├── ylx-158-1.jpg   # 玉露香梨礼盒图1
  │   ├── ylx-158-2.jpg   # 玉露香梨礼盒图2
  │   ├── wns-158-1.jpg   # 维纳斯苹果礼盒
  │   └── ...
  ├── farm/               # 农场照片
  │   ├── overview.jpg    # 果园全景
  │   └── organic-cert.jpg
  ├── process/            # 种植流程图
  │   ├── fertilization.jpg
  │   └── harvest.jpg
  └── reports/            # 质检报告
      └── quality-report.pdf

【生产环境】
  使用阿里云OSS存储，配置 .env 文件：
  OSS_BUCKET=zhinong-assets
  OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com

  图片上传到OSS后，保持相同的目录结构即可。

【使用方法】
  from backend.config.product_config import get_image_url
  
  # 获取产品图片完整URL
  url = get_image_url("products/ylx-158-1.jpg")
  # 开发环境返回: /static/images/products/ylx-158-1.jpg
  # 生产环境返回: https://zhinong-assets.oss-cn-beijing.aliyuncs.com/products/ylx-158-1.jpg
"""
import os
from backend.config.settings import settings


def get_image_base_url() -> str:
    """
    获取图片基础URL
    - 开发环境返回本地路径
    - 生产环境返回OSS路径
    """
    if settings.DEBUG:
        return "/static/images"
    else:
        return f"https://{settings.OSS_BUCKET}.{settings.OSS_ENDPOINT}"


def get_image_url(path: str) -> str:
    """
    获取完整图片URL
    
    Args:
        path: 相对路径，如 "products/ylx-158-1.jpg"
    
    Returns:
        str: 完整的图片URL
    """
    base = get_image_base_url()
    return f"{base}/{path}"


# 产品目录配置
PRODUCT_CATALOG = {
    "玉露香梨": {
        "category_name": "玉露香梨",
        "description": "蒲县特产，皮薄肉厚，汁多味甜，富含多种维生素",
        "origin": "山西省临汾市蒲县被子垣有机果园",
        "certification": ["有机认证", "中国农大科技小院"],
        "harvest_season": "9-10月",
        "storage_method": "0-5°C冷藏，可保存30天",
        "skus": [
            {
                "sku_code": "YLX-158-9E",
                "name": "有机玉露香梨天地盖礼盒",
                "specs": {
                    "枚数": 9,
                    "规格": "85-95mm",
                    "净重": "6.5kg"
                },
                "price": 158,
                "original_price": 198,
                "target_scene": "送礼/节日",
                "packaging": "天地盖礼盒",
                "images": [
                    "products/ylx-158-1.jpg",
                    "products/ylx-158-2.jpg"
                ],
                "stock": 100
            },
            {
                "sku_code": "YLX-128-7E",
                "name": "玉露香梨精品礼盒",
                "specs": {
                    "枚数": 7,
                    "规格": "85-95mm",
                    "净重": "5kg"
                },
                "price": 128,
                "original_price": 158,
                "target_scene": "送礼",
                "packaging": "精品礼盒",
                "images": [
                    "products/ylx-128-1.jpg"
                ],
                "stock": 150
            },
            {
                "sku_code": "YLX-79-6E",
                "name": "玉露香梨手提福利盒",
                "specs": {
                    "枚数": 6,
                    "规格": "80-90mm",
                    "净重": "3.2kg"
                },
                "price": 79,
                "target_scene": "引流/家庭装",
                "packaging": "手提礼盒",
                "images": [
                    "products/ylx-79-1.jpg"
                ],
                "stock": 200
            }
        ]
    },
    
    "维纳斯黄金苹果": {
        "category_name": "维纳斯黄金苹果",
        "description": "日本引进品种，果肉金黄，香甜脆爽，营养丰富",
        "origin": "山西省临汾市蒲县被子垣有机果园",
        "certification": ["有机认证", "中国农大科技小院"],
        "harvest_season": "10-11月",
        "storage_method": "常温保存7天，冷藏可延长至30天",
        "skus": [
            {
                "sku_code": "WNS-158-12E",
                "name": "维纳斯苹果天地盖礼盒",
                "specs": {
                    "枚数": 12,
                    "规格": "75-80mm",
                    "净重": "4.5kg"
                },
                "price": 158,
                "target_scene": "送礼",
                "packaging": "天地盖礼盒",
                "images": [
                    "products/wns-158-1.jpg"
                ],
                "stock": 80
            },
            {
                "sku_code": "WNS-128-10E",
                "name": "维纳斯苹果精品礼盒",
                "specs": {
                    "枚数": 10,
                    "规格": "75-80mm",
                    "净重": "3.8kg"
                },
                "price": 128,
                "target_scene": "送礼",
                "packaging": "精品礼盒",
                "images": [
                    "products/wns-128-1.jpg"
                ],
                "stock": 100
            },
            {
                "sku_code": "WNS-79-5E",
                "name": "维纳斯苹果家庭装",
                "specs": {
                    "枚数": 5,
                    "规格": "65-75mm",
                    "净重": "4.5kg"
                },
                "price": 79,
                "target_scene": "日常消费",
                "packaging": "对开箱",
                "images": [
                    "products/wns-79-1.jpg"
                ],
                "stock": 150
            }
        ]
    },
    
    "深加工产品": {
        "category_name": "深加工产品",
        "description": "延长销售周期，解决鲜果季节性难题",
        "skus": [
            {
                "sku_code": "PG-68-250G",
                "name": "有机苹果脆片礼盒",
                "specs": {
                    "单袋": "50g",
                    "盒数": 5,
                    "总重": "250g"
                },
                "price": 68,
                "target_scene": "零食/伴手礼",
                "shelf_life": "12个月",
                "images": [
                    "products/pg-68-1.jpg"
                ],
                "stock": 300
            },
            {
                "sku_code": "YLX-JU-158",
                "name": "玉露香梨汁礼盒",
                "specs": {
                    "规格": "248ml×10瓶",
                    "总重": "2.5kg"
                },
                "price": 158,
                "target_scene": "健康饮品",
                "shelf_life": "18个月",
                "images": [
                    "products/ylx-ju-158-1.jpg"
                ],
                "stock": 200
            },
            {
                "sku_code": "PG-88-500G",
                "name": "混合果干礼盒",
                "specs": {
                    "包含": "苹果干、梨干、红枣",
                    "总重": "500g"
                },
                "price": 88,
                "target_scene": "健康零食",
                "shelf_life": "12个月",
                "images": [
                    "products/pg-88-1.jpg"
                ],
                "stock": 250
            }
        ]
    }
}

# 营销活动配置
MARKETING_CAMPAIGNS = {
    "new_user_discount": {
        "name": "新用户首单立减",
        "type": "coupon",
        "discount_amount": 20,
        "min_order_amount": 79,
        "valid_for_days": 7,
        "description": "新用户下单满79元立减20元"
    },
    "gift_box_bundle": {
        "name": "礼盒组合优惠",
        "type": "bundle",
        "products": ["YLX-158-9E", "WNS-158-12E"],
        "bundle_price": 288,
        "original_price": 316,
        "description": "玉露香梨+维纳斯苹果双礼盒"
    },
    "bulk_purchase": {
        "name": "批量采购优惠",
        "type": "tier_discount",
        "tiers": [
            {"min_quantity": 5, "discount_rate": 0.05},   # 5件9.5折
            {"min_quantity": 10, "discount_rate": 0.1},   # 10件9折
            {"min_quantity": 20, "discount_rate": 0.15}   # 20件85折
        ],
        "description": "买得越多，优惠越大"
    }
}

# 物流配置
SHIPPING_CONFIG = {
    "free_shipping_threshold": 158,  # 满158包邮
    "default_shipping_fee": 12,
    "express_companies": [
        {"code": "SF", "name": "顺丰速运", "extra_fee": 8},
        {"code": "JD", "name": "京东物流", "extra_fee": 5},
        {"code": "YTO", "name": "圆通速递", "extra_fee": 0}
    ],
    "remote_areas": [
        "西藏", "新疆", "青海", "宁夏", "内蒙古", "黑龙江"
    ],
    "remote_area_fee": 20,
    "default_shipping_method": "YTO"
}

# 溯源信息模板
TRACEABILITY_TEMPLATE = {
    "farm_info": {
        "name": "蒲县被子垣有机果园",
        "location": "山西省临汾市蒲县",
        "area": "500亩",
        "certification": "有机认证编号：XXXXXX",
        "tech_support": "中国农业大学科技小院",
        "images": [
            "farm/overview.jpg",
            "farm/organic-cert.jpg"
        ]
    },
    "cultivation_process": [
        {
            "stage": "春季施肥",
            "date": "3月",
            "description": "施用有机肥，改良土壤",
            "image": "process/fertilization.jpg"
        },
        {
            "stage": "花期管理",
            "date": "4月",
            "description": "人工授粉，疏花疏果",
            "image": "process/pollination.jpg"
        },
        {
            "stage": "绿色防控",
            "date": "5-8月",
            "description": "物理防治+生物防治，不使用化学农药",
            "image": "process/pest-control.jpg"
        },
        {
            "stage": "采摘包装",
            "date": "9-10月",
            "description": "人工采摘，当日包装发货",
            "image": "process/harvest.jpg"
        }
    ],
    "quality_inspection": {
        "items": ["农药残留检测", "重金属检测", "糖度检测"],
        "report_url": "reports/quality-report.pdf"
    }
}
