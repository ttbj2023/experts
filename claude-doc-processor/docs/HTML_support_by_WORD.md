# Word兼容HTML格式开发规范手册
## HTML→可编辑DOCX转换工具专用
### 文档定位
本手册为**自动化PDF转DOCX工具开发**的核心参考规范，所有内容均基于Microsoft Word自研HTML解析引擎的底层逻辑制定，覆盖中文教辅、出版物等复杂排版场景的核心需求，确保生成的HTML满足：
1.  Word 2016/2019/365全版本正常打开，无乱码、无裂图、无排版错乱
2.  所有元素（文本、公式、表格、图片）另存为DOCX后可原生编辑
3.  数学公式可直接进入Word公式编辑器修改，无位图化
4.  复杂排版（多栏、标题层级、列表、注释）1:1还原出版物效果

---

## 一、前置核心认知（开发底层逻辑）
Word的HTML解析逻辑与浏览器完全不同，是本手册所有规范的核心前提：
1.  **兼容范围**：仅支持 **HTML 4.01 核心子集 + CSS 2.1 核心子集**，完全不兼容HTML5新特性、CSS3高级属性
2.  **解析逻辑**：HTML标签/属性 → 映射为Word原生样式/对象，而非浏览器的DOM渲染；不支持的标签/属性会被直接忽略，甚至导致全局排版错乱
3.  **核心目标**：放弃浏览器端的高级渲染能力，完全适配Word的原生映射规则，优先保证「可编辑性」和「排版稳定性」
4.  **单位规范**：所有尺寸优先使用Word原生单位`pt`（磅），中文排版标准：五号字=10.5pt、小四=12pt、四号=14pt

---

## 二、基础文档结构规范（必写，零容错）
### 2.1 固定文档骨架（所有生成的HTML必须严格遵循）
```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <!-- 必须放在head最顶部，唯一解决中文乱码的方案 -->
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <!-- 文档标题，自动映射为Word文档标题属性 -->
    <title>转换生成文档</title>
    <!-- 唯一合法的样式写入方式：内部style标签，禁止外部样式表、@import -->
    <style type="text/css">
        /* 全局样式、元素样式统一写在此处 */
    </style>
    <!-- 仅用于浏览器端公式渲染，Word会完全忽略JS执行，仅扫描特定公式标签 -->
    <script type="text/javascript" async
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
    </script>
</head>
<body>
    <!-- 正文内容，必须使用规范内的标签 -->
</body>
</html>
```

### 2.2 合法HTML标签清单（按优先级分类）
#### 2.2.1 必用标签（100%兼容，优先使用）
| 标签分类 | 合法标签 | 核心用途与映射规则 |
|----------|----------|---------------------|
| 结构标签 | `<html>` `<head>` `<body>` | 文档基础骨架，缺一不可 |
| 标题标签 | `<h1>`~`<h6>` | 自动映射为Word内置「标题1-6」样式，支持批量修改格式、生成目录，**标题层级必须用此标签，禁止用div模拟** |
| 段落标签 | `<p>` | 核心正文容器，映射为Word「正文」样式，唯一稳定的段落分隔方案，禁止用多个`<br>`模拟段落 |
| 行内容器 | `<span>` | 唯一稳定的行内文本样式容器，用于局部修改字体、颜色、格式，无兼容问题 |
| 文本格式 | `<strong>`/`<b>` `<em>`/`<i>` `<u>` `<s>` `<sup>` `<sub>` | 映射为Word原生加粗、斜体、下划线、删除线、上标、下标，完美适配脚注、简单公式、单位标注 |
| 列表标签 | `<ol>` `<ul>` `<li>` | 映射为Word原生可编辑列表，支持自动编号、层级嵌套，**题目编号必须用此标签，禁止纯文本手写序号** |
| 表格标签 | `<table>` `<tr>` `<td>` `<th>` | 映射为Word原生表格，支持合并单元格、边框、边距设置 |
| 图片标签 | `<img>` | 唯一稳定的图片插入方案，必须配合base64内嵌使用 |
| 换行标签 | `<br>` | 仅用于段落内强制软换行，不产生段间距 |

#### 2.2.2 可用标签（有限兼容，特定场景使用）
| 标签 | 兼容说明 | 限制条件 |
|------|----------|----------|
| `<div>` | 仅作为块级容器使用，支持基础宽高、边距、边框 | 禁止嵌套超过3层，禁止用于布局，不支持Flex/Grid，非必要不使用 |
| `<font>` | 虽HTML4已废弃，但Word兼容性拉满 | 仅用于老版本Word兼容，优先用CSS+span替代 |
| `<hr>` | 可渲染默认水平线 | CSS修改样式基本无效，非必要不使用 |

#### 2.2.3 禁用标签（100%不兼容，写了必出问题）
- HTML5语义化标签：`<section>` `<article>` `<header>` `<footer>` `<nav>` `<figure>` `<figcaption>`
- 多媒体/容器标签：`<video>` `` `<iframe>` `<canvas>` `<template>` `<noscript>`
- 表单标签：`<form>` `<input>` `<select>` `<button>` `<textarea>`
- 其他：`<svg>`（老版本Word完全不兼容，非必要禁用）、自定义标签

### 2.3 CSS兼容规范（仅支持以下内容，禁止超范围使用）
#### 2.3.1 合法选择器（仅支持以下类型，嵌套不超过2层）
✅ 标签选择器：`body` `p` `h1` `ol` 等
✅ 类选择器：`.two-column` `.formula-block` 等（最常用，最稳定）
✅ ID选择器：`#page-container` 等（支持，不推荐）
✅ 后代选择器：`ol li` `p span` 等（嵌套≤2层）

❌ 完全禁用：伪类/伪元素、属性选择器、相邻兄弟选择器、通配符选择器

#### 2.3.2 100%兼容CSS属性（放心使用）
| 属性分类 | 合法属性 | 最佳实践 |
|----------|----------|----------|
| 字体文本 | `font-family` `font-size` `font-weight` `font-style` `text-decoration` `color` `text-align` `text-indent` `line-height` | 1. 字体仅用Word内置字体：`"宋体", "Times New Roman", "黑体", "Cambria Math"`，禁止自定义字体<br>2. 字号优先用`pt`，行高优先用倍数（如`1.6`）<br>3. 中文首行缩进用`text-indent: 2em;`，完全兼容 |
| 盒模型 | `width` `height` `margin` `padding` `border` `background-color` | 1. `margin`仅块级元素生效，对应Word段前段后距<br>2. `border`仅支持`solid`/`dashed`/`dotted`三种样式，禁用圆角<br>3. 颜色仅支持十六进制、RGB，禁用`rgba`透明度 |
| 页面控制 | `@page` `page-break-before` `page-break-after` `break-inside` | 1. `@page`可设置页面尺寸、页边距，示例：`@page { size: A4; margin: 20pt 30pt; }`<br>2. `break-inside: avoid;`可避免标题、图片、公式被分栏/分页拆分，Word原生支持 |

#### 2.3.3 有限兼容CSS属性（特定场景可用）
| 属性 | 兼容说明 | 限制条件 |
|------|----------|----------|
| `column-count` | 【多栏布局唯一稳定方案】完美映射Word原生分栏功能 | 配套`column-gap`（栏间距）、`column-rule`（栏间分隔线）全支持，禁止用float/Flex做分栏 |
| `float` | 仅基础`left/right`支持 | 极易导致跨页排版错乱，非必要禁用，禁止用于多栏布局 |
| `display` | 仅支持`block`/`inline`/`none` | `inline-block`兼容性极差，`flex`/`grid`完全禁用 |
| `vertical-align` | 仅对表格单元格`<td>`、`<sup>/<sub>`生效 | 行内元素使用基本无效，禁用 |
| `white-space` | 仅`pre`/`nowrap`生效 | 用于保留代码/公式的空格格式 |

#### 2.3.4 完全禁用CSS属性
所有CSS3高级属性、现代布局属性全量禁用，包括但不限于：
- 现代布局：`display: flex/grid`、`gap`、`place-content`等
- 定位相关：`position: absolute/fixed`、`z-index`、`top/left/right/bottom`
- CSS3特效：`border-radius`、`box-shadow`、`transform`、`transition`、`animation`、渐变
- 其他：`overflow`、`opacity`、`rgba/hsla`透明度、媒体查询、`max-width/min-width`

---

## 三、核心元素开发规范（工具开发核心模块）
### 3.1 图片嵌入规范（100%无裂图，可编辑）
#### 3.1.1 核心支持规则
1.  唯一稳定方案：**base64内嵌data URI**，绝对禁止使用本地路径、外部HTTP链接，否则Word打开必裂图
2.  支持格式：仅`PNG`、`JPG/JPEG`，SVG老版本Word完全不兼容，禁止使用
3.  宽高控制：优先使用原生`width`/`height`属性，其次用内联`style`，禁止用CSS类控制图片尺寸
4.  映射规则：Word打开后会将内嵌图片转为原生嵌入对象，另存为DOCX后可直接裁剪、修改格式

#### 3.1.2 开发示例
```html
<!-- 正确示例：base64内嵌，原生属性控制宽高 -->
<p style="text-align: center;">
    <img 
        src="data:image/png;base64,这里替换为图片base64编码" 
        width="300pt" 
        alt="图1 箱线图示例"
    >
</p>
<p style="text-align: center; font-size: 9.5pt;">图1 第4题箱线图</p>

<!-- 错误示例：本地路径、外部链接、CSS类控制尺寸 -->
<img src="./images/fig1.png" class="figure-img">
<img src="https://example.com/fig1.jpg">
```

#### 3.1.3 避坑指南
1.  图片base64编码无需换行，直接拼接在`src`属性内
2.  大图建议压缩后再转base64，避免HTML文件过大导致Word打开卡顿
3.  图注必须用`<p>`标签单独编写，禁止用`<figcaption>`（完全不兼容）
4.  给图片包裹的`<p>`标签设置`text-align: center;`，可实现图片居中，兼容性拉满

### 3.2 多栏版式规范（出版物/教辅双栏核心方案）
#### 3.2.1 核心支持规则
1.  唯一稳定方案：CSS `column-count` 属性，完美映射Word原生「分栏」功能，跨页自动排版，不会出现表格分栏的单元格锁死问题
2.  配套属性全支持：`column-gap`（栏间距，建议≥20pt）、`column-rule`（栏间分隔线，与出版物样式匹配）
3.  防拆分规则：给标题、图片、公式块添加`break-inside: avoid;`，避免被拆分到两栏
4.  映射规则：Word打开后会转为原生分栏格式，另存为DOCX后可直接在「布局」选项卡中修改分栏设置

#### 3.2.2 开发示例（适配教辅双栏场景）
```html
<style>
    /* 双栏全局样式 */
    .two-column {
        column-count: 2;
        column-gap: 24pt;
        column-rule: 1pt solid #cce0f5;
        margin: 10pt 0;
    }
    /* 防拆分：标题、图片、公式块不跨栏 */
    h2, .figure, .formula-block {
        break-inside: avoid;
    }
</style>

<!-- 双栏内容容器 -->
<div class="two-column">
    <!-- 左栏内容 -->
    <h2>[复习巩固]</h2>
    <ol>
        <li>题目内容</li>
        <li>题目内容</li>
    </ol>

    <!-- 右栏内容，无需手动分栏，Word自动排版 -->
    <h2>[综合运用]</h2>
    <ol start="6">
        <li>题目内容</li>
        <li>题目内容</li>
    </ol>
</div>
```

#### 3.2.3 避坑指南
1.  绝对禁止用`<table>`、`float`做双栏布局，会导致跨页内容锁死、排版错乱
2.  分栏容器内禁止嵌套多层`<div>`，最多1层嵌套，否则会导致分栏失效
3.  栏间分隔线仅支持`solid`实线样式，其他样式兼容性极差
4.  如需单栏+双栏混合排版，单独给双栏内容包裹容器，不要给全局`body`设置分栏

### 3.3 数学公式规范（核心需求：可进入公式编辑器编辑）
#### 3.3.1 核心支持规则
1.  最佳兼容方案：`<script type="math/tex">` 标签，Word 2016及以上版本100%支持，也是Typora导出HTML可被Word识别公式的核心原理
2.  映射逻辑：Word打开HTML时，会扫描该标签，直接将内部的LaTeX源码转为Word原生OMML公式格式，另存为DOCX后，双击即可进入公式编辑器自由修改
3.  格式区分：
    - 行内公式：`<script type="math/tex">LaTeX源码</script>`，随段落排版
    - 块级公式：`<script type="math/tex; mode=display">LaTeX源码</script>`，自动居中，单独成段，对应Word块级公式
4.  次选方案：MathML `<math>` 标签，有限兼容，仅用于老版本Word，LLM生成成本高，非必要不使用
5.  禁用方案：公式位图，仅能显示，无法编辑，完全不符合需求，万不得已时禁用

#### 3.3.2 开发示例
```html
<style>
    .formula-block {
        margin: 8pt 0;
        text-align: center;
        break-inside: avoid;
    }
</style>

<!-- 行内公式示例 -->
<p>（2）方差计算公式为 <script type="math/tex">s^2 = \frac{1}{n}\sum_{i=1}^n (x_i-\overline{x})^2</script>，计算结果如下：</p>

<!-- 块级公式示例 -->
<div class="formula-block">
    <script type="math/tex; mode=display">
        \frac{30×60×75\%+40×60×60\%+50×40×47.5\%}{60×75\%+60×60\%+40×47.5\%}=37.4(\mathrm{元})
    </script>
</div>

<!-- 简单上下标：优先用原生标签，兼容性更强 -->
<p>方差结果：s<sup>2</sup><sub>A</sub>=127.25 ℃<sup>2</sup></p>
```

#### 3.3.3 避坑指南
1.  LaTeX源码无需HTML转义，直接写在标签内即可，Word原生识别
2.  块级公式必须包裹在设置了`break-inside: avoid;`的容器内，避免被分栏/分页拆分
3.  公式内的单位、文本用`\mathrm{}`包裹，避免被识别为变量，与出版物格式统一
4.  禁止将LaTeX源码写在注释内，Word仅扫描标签内的文本内容
5.  简单上下标、平方、单位优先用`<sup>/<sub>`标签，兼容性比LaTeX更强

### 3.4 表格规范（映射为Word原生可编辑表格）
#### 3.4.1 核心支持规则
1.  优先使用**HTML原生属性**控制表格样式，CSS仅用于辅助修改字体、颜色，`border-collapse`完全不兼容
2.  必须属性：`border`（边框宽度）、`cellpadding`（单元格内边距）、`cellspacing`（单元格间距，固定为0）
3.  合并单元格：`colspan`（横向合并）、`rowspan`（纵向合并）100%兼容，映射为Word原生合并单元格
4.  对齐方式：单元格内用原生`align`（水平）、`valign`（垂直）属性控制，兼容性比CSS更强
5.  映射规则：Word打开后转为原生表格，另存为DOCX后可直接修改边框、合并拆分单元格、调整宽高

#### 3.4.2 开发示例
```html
<!-- 正确示例：原生属性优先，兼容拉满 -->
<table border="1" cellpadding="4" cellspacing="0" width="100%">
    <thead>
        <tr>
            <th align="center" width="30%">组别</th>
            <th align="center" width="35%">平均数</th>
            <th align="center" width="35%">方差</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td align="center">A组</td>
            <td align="center">4℃</td>
            <td align="center">127.25</td>
        </tr>
        <tr>
            <td align="center">B组</td>
            <td align="center">20℃</td>
            <td align="center">53.1875</td>
        </tr>
    </tbody>
</table>

<!-- 错误示例：仅用CSS控制边框，无原生属性 -->
<table style="border: 1px solid #333;">...</table>
```

#### 3.4.3 避坑指南
1.  禁止用`<div>`模拟表格，必须用原生`<table>`系列标签，否则无法转为Word可编辑表格
2.  表格宽度优先用`%`相对单位，适配Word页面宽度，避免超出页面
3.  老版本Word对`<thead>`/`<tbody>`的样式支持极差，核心样式直接写在`<td>`/`<th>`标签上
4.  表格内的公式依然用`<script type="math/tex">`标签，完全兼容
5.  给表格包裹的`<p>`标签设置`break-inside: avoid;`，避免表格被分页拆分

### 3.5 列表规范（教辅题目编号核心）
#### 3.5.1 核心支持规则
1.  必须用原生`<ol>`/`<ul>`/`<li>`标签，映射为Word原生可编辑列表，修改题目后编号自动更新，禁止用纯文本手写序号
2.  原生属性全支持：
    - `<ol>`的`type`属性：`1`（数字）、`A`（大写字母）、`a`（小写字母）、`I`（大写罗马）、`i`（小写罗马）
    - `<ol>`的`start`属性：设置起始编号，适配跨栏、分页的题目序号承接
    - `<ul>`的`type`属性：`disc`（实心圆）、`circle`（空心圆）、`square`（实心方块）
3.  多级列表：嵌套`<ol>`/`<ul>`可实现多级编号，Word完美识别层级关系

#### 3.5.2 开发示例（适配教辅题目场景）
```html
<style>
    ol li {
        margin: 5pt 0;
    }
    /* 二级列表：(1)(2)格式 */
    ol li ol {
        list-style-type: none;
        margin: 4pt 0 4pt 15pt;
    }
    ol li ol li::before {
        content: "(" counter(list-item) ") ";
    }
</style>

<!-- 一级有序列表：题目编号 -->
<ol>
    <li>
        下列说法正确的是（）
        <!-- 二级有序列表：选项 -->
        <ol type="A">
            <li>选项内容A</li>
            <li>选项内容B</li>
            <li>选项内容C</li>
            <li>选项内容D</li>
        </ol>
    </li>
    <li>
        <ol>
            <li>第一小问内容</li>
            <li>第二小问内容</li>
        </ol>
    </li>
</ol>

<!-- 跨页承接编号：start属性 -->
<ol start="6">
    <li>第6题内容</li>
    <li>第7题内容</li>
</ol>
```

#### 3.5.3 避坑指南
1.  禁止用`<p>`标签+纯文本手写编号，否则另存为DOCX后无法自动更新，修改题目必乱号
2.  多级列表嵌套不超过3层，否则Word会识别错误层级
3.  CSS修改列表样式兼容性极差，优先用原生`type`属性实现
4.  双栏布局中，跨栏的列表必须用`start`属性承接编号，避免编号重置

---

## 四、全流程开发最佳实践
### 4.1 自动化转换工具流水线规范
结合你的PDF转DOCX需求，推荐以下可落地的流水线，完全匹配本手册规范：
1.  **PDF拆解**：用PyMuPDF提取文本块、图片、页面尺寸、布局坐标，生成整页预览图
2.  **内容结构化**：多模态LLM输入预览图+粗文本，输出：
    - 结构化文本内容，公式用`[FORMULA_X]`占位、图片用`[IMAGE_X]`占位
    - 标题层级、列表嵌套关系、分栏标识
    - LaTeX公式列表、图片base64编码列表
3.  **HTML生成**：基于本手册的规范模板，替换占位符，生成符合Word兼容规则的HTML
4.  **兼容性校验**：自动检查生成的HTML是否存在禁用标签/属性，提前规避排版风险
5.  **DOCX转换**：Word打开HTML后，可通过VBA/COM组件自动化另存为DOCX，无需手动操作

### 4.2 全局样式统一规范（避免排版错乱）
1.  全局统一设置中文字体为`宋体`，西文字体为`Times New Roman`，公式字体为`Cambria Math`，匹配国内出版物/教辅的默认格式
2.  正文固定字号`10.5pt`，行高`1.6`，标题层级字号按h1-h6递减，统一设置段前段后距
3.  全局页面固定为A4尺寸，页边距上下20pt、左右30pt，避免不同设备打开页面尺寸错乱
4.  所有元素的对齐方式优先用原生属性，其次用`text-align`，禁止用复杂CSS实现对齐

---

## 五、兼容性测试验收标准
生成的HTML必须通过以下测试，方可作为合格的转换结果：
1.  **打开测试**：用Word 2016/2019/365打开，无中文乱码、无图片裂图、无标签源码泄露
2.  **排版测试**：多栏、标题、列表、表格排版还原，无内容错位、无跨页错乱
3.  **可编辑性测试**：
    - 文本、列表、表格可直接编辑修改
    - 所有公式双击可进入Word公式编辑器，可修改、可重新计算
    - 图片可裁剪、调整大小、修改环绕方式
4.  **格式映射测试**：另存为DOCX后，标题可生成目录，列表编号可自动更新，表格可原生编辑
5.  **稳定性测试**：保存关闭后重新打开，所有格式、内容无变化，无兼容性警告

---

## 六、禁用清单（红线规则，绝对不能触碰）
1.  禁止使用任何HTML5新标签、CSS3高级属性、现代布局方案
2.  禁止使用外部资源（外部图片、外部样式表、外部字体），所有资源必须内嵌
3.  禁止使用JS代码实现任何功能，仅保留MathJax的CDN引入（不执行）
4.  禁止用位图替代公式、用纯文本替代列表、用div模拟表格/标题
5.  禁止使用自定义字体、非内置字体，避免Word自动替换导致排版错乱
6.  禁止使用绝对定位、固定定位、浮动布局实现页面排版
7.  禁止使用任何带透明度的颜色、渐变、阴影、圆角等特效属性