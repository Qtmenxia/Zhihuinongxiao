# 静态资源目录

此目录用于存放产品图片、农场照片、溯源流程图等静态资源。

## 🗂️ 目录结构

```
static/images/
├── products/              # 产品图片（必需）
│   ├── ylx-158-1.jpg      # 玉露香梨158元礼盒图1
│   ├── ylx-158-2.jpg      # 玉露香梨158元礼盒图2
│   ├── ylx-128-1.jpg      # 玉露香梨128元礼盒
│   ├── ylx-79-1.jpg       # 玉露香梨79元家庭装
│   ├── wns-158-1.jpg      # 维纳斯苹果158元礼盒
│   ├── wns-128-1.jpg      # 维纳斯苹果128元礼盒
│   ├── wns-79-1.jpg       # 维纳斯苹果家庭装
│   ├── pg-68-1.jpg        # 苹果脆片礼盒
│   ├── ylx-ju-158-1.jpg   # 玉露香梨汁礼盒
│   └── pg-88-1.jpg        # 混合果干礼盒
├── farm/                  # 农场照片（溯源用）
│   ├── overview.jpg       # 果园全景
│   └── organic-cert.jpg   # 有机认证证书
├── process/               # 种植流程图（溯源用）
│   ├── fertilization.jpg  # 施肥阶段
│   ├── pollination.jpg    # 授粉阶段
│   ├── pest-control.jpg   # 绿色防控
│   └── harvest.jpg        # 采摘阶段
└── reports/               # 质检报告
    └── quality-report.pdf # 质检报告PDF
```

## 📷 图片规格要求

| 类型 | 尺寸 | 格式 | 大小限制 |
|------|------|------|----------|
| 产品主图 | 800×800px 以上 | JPG/PNG | ≤2MB |
| 产品详情图 | 宽度≥750px | JPG/PNG | ≤2MB |
| 农场照片 | 1200×800px | JPG | ≤3MB |
| 流程图 | 600×400px | JPG/PNG | ≤1MB |

## 🔧 开发环境配置

1. 将图片放入对应目录
2. FastAPI会自动挂载静态文件服务
3. 访问方式：`http://localhost:8000/static/images/products/ylx-158-1.jpg`

## ☁️ 生产环境配置（OSS）

1. 在 `.env` 文件中配置：
   ```env
   DEBUG=false
   OSS_BUCKET=zhinong-assets
   OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
   OSS_ACCESS_KEY=your_access_key
   OSS_ACCESS_SECRET=your_access_secret
   ```

2. 上传图片到OSS，保持相同目录结构

3. 代码中使用 `get_image_url()` 会自动返回OSS路径

## 📝 命名规范

- **产品图片**: `{sku简码}-{序号}.jpg`
  - 例：`ylx-158-1.jpg` (玉露香梨158元款第1张)
- **农场照片**: `{描述}.jpg`
  - 例：`overview.jpg`, `organic-cert.jpg`
- **流程图片**: `{阶段英文}.jpg`
  - 例：`fertilization.jpg`, `harvest.jpg`

## 🖼️ 图片缺失处理

如果图片文件不存在，前端应显示占位图。建议在 `static/images/` 下放置：
- `placeholder-product.jpg` - 产品占位图
- `placeholder-farm.jpg` - 农场占位图
