# Demis Hassabis 风格转换优化说明

**更新日期**：2025-02-19
**版本**：v2.1 - 开篇引用框优化

---

## 优化内容概览

基于微信公众号的特性，我们对 Demis Hassabis 风格转换器进行了三项关键优化：

### 1. ✅ 移除主标题和作者信息

**原因**：
- 微信公众号文章自带标题、作者、封面图等元数据
- 正文重复显示会造成视觉冗余
- 节省阅读空间，提升阅读体验

**实现**：
```python
# 移除开头的 h1 标题（因为微信公众号已经有标题了）
first_h1 = soup.find("h1")
if first_h1:
    first_h1.decompose()
```

**效果对比**：

**优化前**：
```
┌─────────────────────────────────┐
│ 【引用框】摘要...               │
├─────────────────────────────────┤
│      文章标题                   │ ← 重复
│      作者：xxx                  │ ← 重复
├─────────────────────────────────┤
│ 01 文档说明                     │
└─────────────────────────────────┘
```

**优化后**：
```
┌─────────────────────────────────┐
│ 【引用框】摘要...               │
├─────────────────────────────────┤
│ 01 文档说明                     │ ← 直接开始正文
└─────────────────────────────────┘
```

---

### 2. ✅ 优化代码块样式

**原因**：
- 原始代码块样式单调，不易阅读
- 需要更好的视觉区分
- 提升代码可读性

**实现**：
```python
# 优化代码块样式
for pre in soup.find_all("pre"):
    code_content = pre.get_text()

    # 创建美化后的代码块
    code_html = f"""
    <section style="margin: 16px 0; padding: 0;">
        <section style="background-color: #f6f8fa; padding: 16px;
                          border-radius: 8px;
                          border-left: 4px solid #004080;
                          overflow-x: auto;">
            <code style="font-family: 'Courier New', Consolas, Monaco, monospace;
                          font-size: 13px;
                          line-height: 1.6;
                          color: #333;
                          white-space: pre-wrap;
                          word-break: break-all;">
                {code_content}
            </code>
        </section>
    </section>
    """
```

**样式特点**：
- **背景色**：`#f6f8fa` - 浅灰色，温和不刺眼
- **左侧边框**：`4px solid #004080` - 深蓝色，与主题色统一
- **圆角**：`8px` - 现代柔和
- **内边距**：`16px` - 舒适的阅读空间
- **字体**：`Courier New, Consolas, Monaco` - 专业等宽字体
- **字号**：`13px` - 适合移动端阅读
- **自动换行**：`white-space: pre-wrap` - 避免横向滚动
- **横向滚动**：`overflow-x: auto` - 超长代码可滚动

**行内代码优化**：
```python
# 行内代码 - 粉色高亮
code_html = f'<span style="background-color: #f6f8fa;
                           color: #d63384;
                           padding: 2px 6px;
                           border-radius: 4px;
                           font-family: \'Courier New\', Consolas, Monaco, monospace;
                           font-size: 0.9em;">
                {code_text}
              </span>'
```

**效果预览**：

**普通段落**：
这里是正文内容，其中包含 `行内代码` 示例。

**代码块**：
```python
def calculate_variance(data):
    """计算方差"""
    n = len(data)
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    return variance
```

---

### 3. ✅ LaTeX 公式处理（Unicode 数学符号）

**原因**：
- 微信公众号不支持 MathJax、KaTeX 等公式渲染库
- 不能使用外部 JavaScript 库
- 需要将公式转换为可读形式

**实现方案**：
- **行内公式** `$...$` → 蓝色背景 + Unicode 数学符号
- **块级公式** `$$...$$` → 灰色容器 + 蓝色背景 + Unicode 数学符号
- **LaTeX 转 Unicode**：自动转换常见数学符号

**实现代码**：
```python
def latex_to_unicode(latex):
    """将常见LaTeX公式转换为Unicode数学符号"""
    replacements = [
        # 希腊字母
        (r'\\alpha', 'α'), (r'\\beta', 'β'), (r'\\gamma', 'γ'),
        (r'\\pi', 'π'), (r'\\theta', 'θ'),

        # 运算符
        (r'\\pm', '±'), (r'\\times', '×'), (r'\\div', '÷'),
        (r'\\neq', '≠'), (r'\\leq', '≤'), (r'\\geq', '≥'),
        (r'\\infty', '∞'), (r'\\partial', '∂'),

        # 积分和求和
        (r'\\int', '∫'), (r'\\sum', 'Σ'), (r'\\prod', 'Π'),

        # 箭头
        (r'\\rightarrow', '→'), (r'\\leftarrow', '←'),

        # 分数和上下标
        (r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2'),
        (r'\^{([^}]+)\}', r'^\1'),
        (r'_{([^}]+)}', r'_\1'),

        # 平方根和幂
        (r'\\sqrt\{([^}]+)\}', r'√\1'),
        (r'\^2', '²'), (r'\^3', '³'),
    ]
    result = latex
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result)
    return result

# $$...$$ 块级公式
def replace_block_formula(match):
    latex_formula = match.group(1)
    unicode_formula = latex_to_unicode(latex_formula)
    return f'<section style="background-color: #f0f4f8; padding: 20px; border-radius: 8px; text-align: center; margin: 16px 0; border: 1px solid #cbd5e0;">\
        <span style="background-color: #e7f3ff; color: #004080; padding: 8px 16px; border-radius: 6px; font-family: \'Times New Roman\', serif; font-size: 16px; letter-spacing: 0.5px;">\
            {unicode_formula}\
        </span>\
       </section>'

# $...$ 行内公式
def replace_inline_formula(match):
    latex_formula = match.group(1)
    unicode_formula = latex_to_unicode(latex_formula)
    return f'<span style="background-color: #e7f3ff; color: #004080; padding: 2px 8px; border-radius: 4px; font-family: \'Times New Roman\', serif; font-size: 0.95em; font-style: italic;">\
        {unicode_formula}\
       </span>'
```

**样式说明**：
- **公式背景**：`#e7f3ff`（浅蓝色）- 与主题色统一
- **文字颜色**：`#004080`（深蓝色）- 主题色，高对比度
- **容器背景**：`#f0f4f8`（浅灰蓝色）- 柔和的边框
- **字体**：`Times New Roman` - 衬线字体，适合数学符号
- **斜体**：`font-style: italic` - 数学公式的标准样式（仅行内）

**转换示例**：

**行内公式**：
```
原始：$s^2 = \frac{1}{n}\sum_{i=1}^n (x_i-\overline{x})^2$
转换：s² = 1/nΣ_i=1^n (x_i-\overline{x})²
```

**块级公式**：
```
原始：$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$
转换：x = \frac{-b ± √b² - 4ac}{2a}
显示：
┌─────────────────────────────────────┐
│                                     │
│   x = \frac{-b ± √b² - 4ac}{2a}    │
│                                     │
└─────────────────────────────────────┘
```

**支持的 LaTeX 符号**：

| LaTeX | Unicode | 说明 |
|-------|---------|------|
| `\alpha`, `\beta`, `\gamma` | α, β, γ | 希腊字母 |
| `\pm`, `\times`, `\div` | ±, ×, ÷ | 运算符 |
| `\leq`, `\geq`, `\neq` | ≤, ≥, ≠ | 比较符号 |
| `\int`, `\sum`, `\prod` | ∫, Σ, Π | 积分求和 |
| `\rightarrow`, `\leftarrow` | →, ← | 箭头 |
| `\infty`, `\partial` | ∞, ∂ | 特殊符号 |
| `^2`, `^3` | ², ³ | 上标数字 |

---

## 后续处理建议

### LaTeX 公式的完整解决方案

**当前实现**：脚本已经实现了 LaTeX 到 Unicode 数学符号的自动转换（v2.0）。

对于复杂公式，建议采用以下方案之一：

#### 方案 A：使用图片（推荐，适合复杂公式）

1. **使用在线工具转换**：
   - [Mathpix](https://mathpix.com/) - LaTeX 截图工具
   - [CodeCogs](https://www.codecogs.com/latex/eqneditor.php) - 在线 LaTeX 编辑器
   - [KaTeX](https://katex.org/) - 渲染后截图

2. **在 Markdown 中直接使用图片**：
   ```markdown
   方差计算公式为：

   ![方差公式](https://your-image-host.com/formula1.png)
   ```

3. **上传图片到微信素材库**

#### 方案 B：使用 Unicode 数学符号（简单公式，已实现）

脚本已经实现了常见 LaTeX 符号到 Unicode 的转换，包括：
- 希腊字母：α, β, γ, π, θ...
- 运算符：±, ×, ÷, ≤, ≥, ≠...
- 积分求和：∫, Σ, Π...
- 箭头：→, ←, ⇔...
- 上标：², ³...

**使用方法**：直接在 Markdown 中使用 LaTeX 语法，脚本会自动转换：
```markdown
行内公式：$E = mc^2$
块级公式：$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$
```

#### 方案 C：混合使用（推荐）

- 简单公式使用 LaTeX，脚本自动转换为 Unicode
- 复杂公式（如矩阵、多行公式）预先转换为图片并插入

---

## 使用指南

### 基本用法

```bash
# 转换 Markdown 文件
python scripts/convert_demis_style_v2.py sample.md

# 指定输出文件
python scripts/convert_demis_style_v2.py sample.md output/sample.html
```

### 工作流程

1. **编写 Markdown** - 使用标准 Markdown 语法
2. **添加元数据**（可选）：
   ```yaml
   ---
   title: 文章标题
   author: 作者名
   summary: 文章摘要
   ---
   ```

3. **转换** - 运行转换脚本

4. **上传到草稿箱**：
   ```bash
   python scripts/upload_to_draft.py sample.html
   ```

5. **在微信后台**：
   - 检查草稿
   - 替换公式占位符（可选）
   - 调整细节
   - 发布

---

## 技术细节

### 支持的 Markdown 扩展

- `extra` - 额外功能
- `nl2br` - 换行转 `<br>`
- `sane_lists` - 健全的列表
- `fenced_code` - 围栏代码块
- `codehilite` - 代码高亮

### 生成的 HTML 特点

1. **完全内联样式** - 所有样式都在 `style` 属性中
2. **符合微信规范** - 仅使用白名单内的标签和属性
3. **响应式设计** - 适配移动端和桌面端
4. **语义化结构** - 清晰的章节划分

---

## 样式配置

### 主色调

```css
/* 深蓝色 - 主色调 */
#004080

/* 黄色 - 强调色 */
#FFDF21

/* 浅灰色 - 背景色 */
#f6f8fa

/* 深灰色 - 正文色 */
#333333
```

### 字体家族

```css
/* 主字体 */
Optima-Regular, PingFangTC-light

/* 标题字体 */
Futura-Medium

/* 代码字体 */
'Courier New', Consolas, Monaco, monospace

/* 数学公式字体 */
'Times New Roman', serif
```

---

### 4. ✅ 开篇引用框样式

**最新样式（v2.1）**：
- **背景色**：`rgba(96, 125, 139, 0.15)` - 半透明灰蓝色
- **左侧边框**：`4px solid #607D8B` - 灰蓝色强调边框
- **文字颜色**：`#455A64` - 深灰蓝色
- **圆角**：`12px` - 柔和的视觉效果
- **内边距**：`20px 24px` - 舒适的阅读空间

**设计理念**：
- 半透明背景让引用框更轻盈，不会过于抢眼
- 左侧边框提供视觉锚点，增加层次感
- 灰蓝色系与 Demis Hassabis 的深蓝色主题协调
- 去除 emoji 和渐变，更简洁专业

**样式演进**：
```
v1.0：灰色背景 → v2.0：蓝灰渐变 + emoji → v2.1：半透明灰蓝色 + 左侧边框
```

---

## 对比：v1.0 vs v2.0 vs v2.1

| 特性 | v1.0 | v2.0 | v2.1（当前版本） |
|------|------|------|-----------------|
| 主标题显示 | ✅ 显示 | ❌ 移除（微信自带） | ❌ 移除（微信自带） |
| 作者信息 | ✅ 显示 | ❌ 移除（微信自带） | ❌ 移除（微信自带） |
| 代码块样式 | 基础样式 | ✨ 优化样式（背景+边框+圆角+正确换行） | ✨ 优化样式（背景+边框+圆角+正确换行） |
| 行内代码 | 基础样式 | ✨ 粉色高亮 | ✨ 粉色高亮 |
| LaTeX 公式 | ❌ 不处理 | ✅ Unicode 数学符号（蓝色主题） | ✅ Unicode 数学符号（蓝色主题） |
| 列表样式 | 无样式 | ✨ 统一缩进和行高 | ✨ 统一缩进和行高 |
| 章节编号 | ✅ 自动编号 | ✅ 自动编号 | ✅ 自动编号 |
| 开篇引用框 | 灰色框 | 蓝灰渐变 + 阴影 + emoji | ✨ 半透明灰蓝色 + 左侧边框 |
| 倾斜标题 | ✅ skewX 效果 | ✅ skewX 效果 | ✅ skewX 效果 |

---

## 常见问题

### Q: 为什么移除了主标题？

A: 微信公众号后台会自动显示文章标题，在正文中重复显示会造成视觉冗余。

### Q: LaTeX 公式如何显示？

A: 脚本已实现 LaTeX 到 Unicode 数学符号的自动转换。对于简单公式，直接使用 `$...$` 或 `$$...$$` 即可；对于复杂公式（如矩阵），建议使用图片。

### Q: 如何让公式显示得更好看？

A: 对于简单公式，脚本已自动转换为 Unicode 符号（如 α, β, ±, √, ∫, Σ）；对于复杂公式，建议使用在线工具（如 Mathpix、CodeCogs）将 LaTeX 转换为高清图片。

### Q: 代码块的颜色可以自定义吗？

A: 可以！修改脚本中的 `border-left-color` 和 `background-color` 即可。

### Q: 开篇引用框的颜色可以改吗？

A: 可以！修改脚本第 257 行的样式：
- 背景颜色：修改 `background-color: rgba(96, 125, 139, 0.15)` 中的 rgba 值
- 边框颜色：修改 `border-left: 4px solid #607D8B` 中的颜色值
- 文字颜色：修改 `color: #455A64` 中的颜色值
- 透明度：调整 rgba 的第四个参数（0.0-1.0，越大越不透明）

---

## 未来优化方向

1. ~~**自动公式转图片**~~ ✅ 已实现 Unicode 转换，可选集成 Mathpix API
2. **更多配色方案** - 提供多种主题选择
3. **代码语法高亮** - 添加彩色语法高亮
4. **表格美化** - 优化表格样式
5. **图片处理** - 自动添加圆角、阴影
6. **更完整的 LaTeX 支持** - 支持矩阵、多行公式等复杂结构（建议使用图片）

---

**文档版本**: v2.1
**最后更新**: 2025-02-19
**维护者**: Claude Code
