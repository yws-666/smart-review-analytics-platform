# 智评优选 —— 基于 Yelp 数据集的商业评论数据分析平台

> 大数据专业综合课程设计 · **个人开发** · 独立完成项目设计、后端架构与开发
> 从 Yelp 开源数据集（原始近 10 GB）清洗 53 万+ 条评论，构建覆盖用户端、商家后台、平台管理端的三端数据分析平台

## 项目亮点

- **Flask 应用工厂 + 5 个 Blueprint 模块化架构**：认证 / 商户 / 用户 / 商家 / 平台五个业务模块，交付 50 个 RESTful API 接口
- **53 万+ 条评论 ETL**：分块读取（每批 5 万条）+ 分批提交避免内存溢出；780 家商户自动归类 10 大类别，数据完整性 98.9%、一致性 100%
- **三层递进推荐算法**：用户偏好 → 协同过滤（余弦相似度）→ 内容匹配 + 热门兜底，1.5 秒超时保护保障接口稳定
- **性能优化**：批量 IN 查询消除 N+1、高频筛选字段建立索引
- **安全**：JWT 无状态认证、SHA-256 密码哈希、角色声明
- **9 张表 ORM 数据模型**（SQLAlchemy），商户表 34 个字段

## 功能实测

项目在新环境（Python 3.13 + 最新 Flask 栈）**一次启动成功**，49 项接口功能测试 45 项通过：

| 端 | 实测内容 |
|----|---------|
| 用户端 | 商户搜索、详情、评论、打卡、个性化推荐、收藏、浏览历史、偏好 |
| 商家后台 | 评论趋势、评分分布、评分雷达、情感趋势、评论词云、互动趋势 |
| 平台管理端 | 总览、类型分布、城市排行、月度趋势、星级分布、数据质量、用户行为等 11 项统计 |

## 目录结构

```
├── run.py                 # 启动入口（python run.py → http://127.0.0.1:5000）
├── app/                   # Flask 应用（工厂模式 + 5 Blueprint + ORM 模型 + 推荐算法）
├── web/                   # 前端（Vue + Chart.js 多页面）
├── scripts/               # 数据库初始化脚本
├── process_yelp_data.py / classify_business.py / compress_yelp_data.py  # ETL 脚本
├── 项目技术文档.md          # 架构、接口、算法、数据质量完整文档
└── requirements.txt        # 运行环境（版本已锁定）
```

> 📦 演示数据库 `data/travelreview.db`（255 MB，含 780 家商户、10 万+ 打卡、4,111 用户）超过 GitHub 单文件 100 MB 限制，以 95 MB 分卷存储于 `data/`。合并还原：
>
> ```bash
> # Linux / macOS / Git Bash
> cat data/travelreview.db.part* > data/travelreview.db
>
> # Windows CMD
> copy /b data\travelreview.db.part* data\travelreview.db
> ```
>
> 合并后按 `requirements.txt` 安装依赖，运行 `python run.py` 即可使用全部功能。

## 运行方式

```bash
pip install -r requirements.txt
python run.py          # 浏览器访问 http://127.0.0.1:5000
```

## 数据来源

原始数据来自 [Yelp Open Dataset](https://www.yelp.com/dataset)，版权归 Yelp 所有，遵循其许可条款仅用于课程教学。

- 声明详情：见 [数据来源声明.md](数据来源声明.md)（数据范围：`data/travelreview.db（分卷）`）
