# 错词清零模式JavaScript错误修复

## 问题描述

在错词清零模式下，点击"提交答案并进入下一轮"按钮时出现JavaScript错误：

```
Uncaught TypeError: Cannot read properties of null (reading 'options')
    at showErrorClearRoundResult ((index):2371:76)
```

## 错误原因

在错词清零模式下，词书选择器(`book-select`)和单元选择器(`list-select`)被隐藏了，但`showErrorClearRoundResult`和`showErrorClearCompletion`函数仍然尝试访问这些元素来获取词书和单元名称，导致JavaScript错误。

## 修复方案

### 1. 在错词清零模式初始化时保存词书和单元信息

在错词清零模式启动时，先获取词书和单元信息，然后保存到`errorClearModeData`对象中：

```javascript
// 获取当前选择的词书和单元信息
const selectedBookName = document.getElementById('book-select').options[document.getElementById('book-select').selectedIndex]?.text || '未知词书';
const selectedListName = document.getElementById('list-select').options[document.getElementById('list-select').selectedIndex]?.text || '未知单元';

// 初始化错词清零模式数据
errorClearModeData = {
    isActive: true,
    currentRound: 1,
    originalQuestions: [...questions],
    currentQuestions: [...questions],
    incorrectWords: [],
    roundResults: [],
    bookName: selectedBookName,  // 新增：保存词书名称
    listName: selectedListName   // 新增：保存单元名称
};
```

### 2. 修改结果显示函数使用保存的信息

修改`showErrorClearRoundResult`和`showErrorClearCompletion`函数，使用保存的词书和单元信息：

```javascript
// 获取当前选择的词书和单元信息（从保存的数据中获取）
const selectedBookName = errorClearModeData.bookName || '未知词书';
const selectedListName = errorClearModeData.listName || '未知单元';
```

### 3. 更新所有errorClearModeData初始化

确保所有地方的`errorClearModeData`初始化都包含新的字段：

```javascript
errorClearModeData = {
    isActive: false,
    currentRound: 1,
    originalQuestions: [],
    currentQuestions: [],
    incorrectWords: [],
    roundResults: [],
    bookName: '',      // 新增
    listName: ''       // 新增
};
```

## 修改的文件

- `templates/index.html`

## 修改的函数

1. **错词清零模式初始化**（在startBtn事件监听器中）
2. **showErrorClearRoundResult** - 轮次结果显示
3. **showErrorClearCompletion** - 完成界面显示
4. **resetQuizState** - 重置状态函数
5. **页面顶部的errorClearModeData初始化**

## 测试验证

修复后，错词清零模式应该能够：

1. 正常显示轮次结果，包含词书和单元信息
2. 正常显示完成界面，包含完整的考核信息
3. 不再出现JavaScript错误
4. 按钮响应正常

## 兼容性

- 保持与现有功能的完全兼容
- 不影响其他模式的功能
- 保持原有的用户体验 