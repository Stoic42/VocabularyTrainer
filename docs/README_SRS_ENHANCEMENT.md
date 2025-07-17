# SRS智能复习系统增强功能

## 概述

本次更新对SRS（间隔重复系统）进行了重大增强，实现了基于学生实际表现的智能复习机制。

## 核心改进

### 1. 错词优先策略
- **错词自动记录**：在标准测试模式下，答错的单词会自动记录到 `ErrorLogs` 表
- **错词优先复习**：SRS复习时优先选择有错误记录的单词
- **错误次数统计**：显示每个单词的错误次数，帮助识别薄弱环节

### 2. 智能掌握度评估
- **基于实际表现**：掌握度不再依赖主观评分，而是基于答题正确性
- **渐进式提升**：答对增加掌握度，答错降低掌握度
- **科学间隔算法**：根据掌握度自动计算下次复习间隔

### 3. 掌握度等级系统

| 等级 | 重复次数 | 颜色标识 | 说明 |
|------|----------|----------|------|
| 🔴 不熟悉 | 0 | 红色 | 从未答对或最近答错 |
| 🟡 初学 | 1 | 黄色 | 第一次答对，需要巩固 |
| 🟠 熟悉 | 2-3 | 橙色 | 多次答对，基本掌握 |
| 🟢 掌握 | 4-10 | 绿色 | 熟练程度较高 |
| 🔵 精通 | >10 | 蓝色 | 非常熟练，间隔较长 |

## 工作流程

### 标准测试模式
1. 学生进行单词拼写测试
2. 系统自动判断答案正确性
3. **答对**：增加掌握度，延长复习间隔
4. **答错**：记录到错词表，降低掌握度，缩短复习间隔
5. 更新 `StudentWordProgress` 表

### SRS智能复习模式
1. **优先选择错词**：从 `ErrorLogs` 表中有记录的单词开始
2. **补充到期单词**：如果错词不够，补充按间隔到期的单词
3. **显示详细信息**：包括掌握度、错误次数、下次复习日期
4. **智能评分**：学生可以主观评分，但系统会结合客观表现

## 技术实现

### 数据库表结构

#### StudentWordProgress 表
```sql
CREATE TABLE StudentWordProgress (
    student_id INTEGER,
    word_id INTEGER,
    repetitions INTEGER DEFAULT 0,  -- 掌握度（重复次数）
    interval INTEGER DEFAULT 1,      -- 复习间隔（天）
    next_review_date DATE,           -- 下次复习日期
    PRIMARY KEY (student_id, word_id)
);
```

#### ErrorLogs 表
```sql
CREATE TABLE ErrorLogs (
    error_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    word_id INTEGER,
    error_type TEXT,
    student_answer TEXT,
    error_date TEXT,
    FOREIGN KEY (word_id) REFERENCES Words(word_id)
);
```

### 核心算法

#### 掌握度更新算法
```python
if is_correct:
    if repetitions == 0:
        repetitions = 1
        interval = 1
    elif repetitions == 1:
        repetitions = 2
        interval = 6
    else:
        repetitions += 1
        interval = int(interval * 1.5)
else:
    if repetitions > 0:
        repetitions = max(0, repetitions - 1)
        interval = max(1, interval // 2)
```

#### 错词优先查询
```sql
-- 优先获取错词
SELECT w.*, p.*, 
       (SELECT COUNT(*) FROM ErrorLogs e WHERE e.word_id = w.word_id AND e.student_id = p.student_id) as error_count
FROM StudentWordProgress p
JOIN Words w ON p.word_id = w.word_id
WHERE p.student_id = ? AND EXISTS (SELECT 1 FROM ErrorLogs e WHERE e.word_id = w.word_id AND e.student_id = p.student_id)
ORDER BY error_count DESC, last_error_date DESC, p.next_review_date ASC
```

## 用户界面改进

### 1. 智能学习进度卡片
- 显示总单词数、已学习数、待复习数、平均间隔
- 最近学习的单词列表，带掌握度标识
- 紫色渐变背景，突出智能复习功能

### 2. SRS复习界面
- 标题改为"🔄 SRS智能复习"
- 说明文字强调"优先复习错词"
- 复习卡片显示掌握度等级和错误次数
- 掌握度用颜色和图标直观显示

### 3. 掌握度可视化
- 🔴 不熟悉（红色背景）
- 🟡 初学（黄色背景）
- 🟠 熟悉（橙色背景）
- 🟢 掌握（绿色背景）
- 🔵 精通（蓝色背景）

## 测试和验证

### 测试脚本
运行 `test_srs_enhancement.py` 来验证功能：

```bash
python test_srs_enhancement.py
```

### 测试内容
1. 检查数据库表结构
2. 验证掌握度计算逻辑
3. 测试错词优先查询
4. 模拟学习会话
5. 检查掌握度分布

## 使用建议

### 对学生
1. **定期进行标准测试**：建立准确的掌握度记录
2. **关注错词复习**：重点复习错误次数多的单词
3. **查看掌握度分布**：了解自己的学习进度

### 对教师
1. **监控错词统计**：识别学生的薄弱环节
2. **分析掌握度分布**：了解班级整体水平
3. **个性化指导**：根据掌握度数据提供针对性建议

## 未来扩展

1. **错词分析报告**：生成详细的错词分析报告
2. **学习路径推荐**：基于掌握度推荐学习路径
3. **遗忘曲线分析**：分析学生的遗忘模式
4. **自适应间隔**：根据个体差异调整间隔算法

## 注意事项

1. **数据一致性**：确保 `ErrorLogs` 和 `StudentWordProgress` 表的数据一致
2. **性能优化**：错词优先查询可能较慢，需要适当索引
3. **用户体验**：错词优先可能导致复习压力，需要平衡
4. **数据备份**：定期备份学习进度数据

---

*这个增强功能让SRS系统更加智能和个性化，真正基于学生的实际表现来安排复习计划。* 