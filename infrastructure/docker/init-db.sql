-- 智农链销数据库初始化脚本
-- 创建必要的扩展和初始配置

-- 创建UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建全文搜索配置(中文分词)
-- CREATE EXTENSION IF NOT EXISTS pg_jieba;

-- 设置时区
SET timezone = 'Asia/Shanghai';

-- 创建数据库(如果使用单独的SQL文件初始化)
-- CREATE DATABASE zhinong_db ENCODING 'UTF8' LC_COLLATE 'zh_CN.UTF-8' LC_CTYPE 'zh_CN.UTF-8';
