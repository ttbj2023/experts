# 微信公众号排版 HTML/CSS 开发参考指南

**版本**：2026 最新版
**更新日期**：2026-02-18
**适用场景**：公众号排版开发、自定义模板制作

> 本指南基于微信公众平台最新的编辑器过滤规则、内置浏览器渲染特性，以及官方合作的行业规范整理，所有规则均经过实际场景验证，可直接用于生产环境。

---

## 目录

- [一、核心开发前提与底层过滤规则](#一核心开发前提与底层过滤规则)
  - [1.1 不可突破的核心原则](#11-不可突破的核心原则)
  - [1.2 编辑器 HTML 清洗核心规则](#12-编辑器-html-清洗核心规则)
  - [1.3 渲染环境基础规范](#13-渲染环境基础规范)
- [二、HTML 标签完整支持白名单](#二html-标签完整支持白名单)
  - [2.1 完全支持的标签（无限制，稳定生效）](#21-完全支持的标签无限制稳定生效)
  - [2.2 有限支持的标签（有严格限制，需谨慎使用）](#22-有限支持的标签有严格限制需谨慎使用)
  - [2.3 完全禁用的标签（绝对不可使用，会被直接过滤）](#23-完全禁用的标签绝对不可使用会被直接过滤)
- [三、CSS 样式完整支持规范](#三css-样式完整支持规范)
  - [3.1 核心支持规则](#31-核心支持规则)
  - [3.2 完全支持的 CSS 属性（稳定生效，无兼容问题）](#32-完全支持的-css-属性稳定生效无兼容问题)
  - [3.3 有限支持的 CSS 属性（兼容性差，有严格限制）](#33-有限支持的-css-属性兼容性差有严格限制)
  - [3.4 完全禁用的 CSS 特性](#34-完全禁用的-css-特性)
- [四、特殊元素开发规范](#四特殊元素开发规范)
  - [4.1 图片开发规范](#41-图片开发规范)
  - [4.2 超链接开发规范](#42-超链接开发规范)
  - [4.3 代码块开发规范](#43-代码块开发规范)
- [五、SVG 交互排版开发规范](#五svg-交互排版开发规范)
  - [5.1 核心支持规则](#51-核心支持规则)
  - [5.2 核心支持的 SVG 标签与属性白名单](#52-核心支持的-svg-标签与属性白名单)
  - [5.3 动画属性白名单（attributeName）](#53-动画属性白名单attributename)
  - [5.4 严格限制与禁止项](#54-严格限制与禁止项)
- [六、开发调试与避坑指南](#六开发调试与避坑指南)
  - [6.1 标准开发流程](#61-标准开发流程)
  - [6.2 高频问题与解决方案](#62-高频问题与解决方案)
  - [6.3 开发工具推荐](#63-开发工具推荐)
- [七、可直接复用的开发模板](#七可直接复用的开发模板)
  - [7.1 基础排版通用模板](#71-基础排版通用模板)
  - [7.2 两列图文卡片模板](#72-两列图文卡片模板)
  - [7.3 三列并列卡片模板](#73-三列并列卡片模板)

---

## 一、核心开发前提与底层过滤规则

### 1.1 不可突破的核心原则

| 规则项 | 核心要求 | 违反后果 |
|--------|----------|----------|
| **样式唯一合法形式** | 仅支持标签内联 `style` 属性，不支持 `<style>` 样式块、外部 CSS 文件、`<link>` 样式引入 | 样式被完全过滤，排版失效 |
| **选择器限制** | 不支持类选择器、ID 选择器、伪类/伪元素（`:hover`/`::before` 等）、后代选择器 | 选择器完全失效，样式不生效 |
| **安全过滤规则** | 所有可执行代码、潜在风险标签/属性会被直接剥离 | 标签被删除、属性被清空，甚至内容无法保存 |
| **媒体资源限制** | 图片、音视频必须使用微信公众平台素材库的 CDN 地址 | 外部资源无法加载、被屏蔽 |

### 1.2 编辑器 HTML 清洗核心规则

1. **属性过滤**：自动剥离所有 `id` 属性、`on*` 开头的事件属性（`onclick`/`onload` 等）、`class` 属性仅保留但无实际作用（无法绑定样式）

2. **标签清洗**：非白名单内的标签会被直接删除，或自动转为 `p`/`span` 等基础标签

3. **样式剥离**：非白名单内的 CSS 属性会被直接从 `style` 中移除，部分风险属性会被强制置空

4. **内容规范**：连续空格会被合并为 1 个，换行符 `\n` 会被转为 `<br>`，代码块需特殊处理避免缩进丢失

5. **链接校验**：非公众号内部链接、非白名单域名的链接会被过滤或添加安全跳转校验

### 1.3 渲染环境基础规范

- **内容区尺寸**：公众号文章内容区最大宽度为 **677px**，移动端默认宽度为屏幕宽度（主流 375px-430px），开发时建议最大宽度不超过 100%，避免横向滚动

- **渲染内核**：iOS 端基于 WKWebView，安卓端基于微信 X5 内核，均兼容 CSS3 基础特性，无需兼容极低版本浏览器

- **深色模式**：微信会自动对文章颜色进行反转适配，开发时建议通过 `data-color-mode` 属性控制适配行为，避免颜色错乱

- **默认样式**：公众号自带全局默认样式（行高 1.6-1.8、默认字体、段落间距等），自定义样式需通过内联样式覆盖

---

## 二、HTML 标签完整支持白名单

### 2.1 完全支持的标签（无限制，稳定生效）

| 标签 | 核心用途 | 支持的属性 | 开发注意事项 |
|------|----------|------------|--------------|
| **p** | 正文段落，核心排版标签 | `style`、`align`（不推荐，用 `text-align` 替代） | 公众号默认段落标签，自带上下外边距，比手动换行更稳定，避免大段文本无包裹直接放在 body 中 |
| **span** | 行内文本装饰，局部样式控制 | `style`、`leaf`（微信内置属性，无需手动添加） | 唯一稳定的行内标签，用于局部文本高亮、变色、改字号，无默认样式 |
| **br** | 强制换行 | 无 | 仅用于同一段落内的换行，不会产生额外段落间距，禁止用多个 `<br>` 实现段落间距（用 p 标签+margin 替代） |
| **strong/b** | 文本加粗 | `style` | 推荐用 `strong`（语义化更好），二者效果一致，可通过 style 覆盖加粗权重 |
| **em/i** | 文本斜体 | `style` | 推荐用 `em`，二者效果一致，适合标注专业术语、引用内容 |
| **u** | 文本下划线 | `style` | 仅用于下划线效果，链接的下划线建议用 `text-decoration` 控制 |
| **del/s** | 删除线 | `style` | 适合标注原价、作废内容，可通过 style 自定义删除线样式 |
| **h1-h3** | 分级标题 | `style` | h1 建议 1 篇仅用 1 次（主标题），h2/h3 用于二级/三级小标题，h4-h6 可兼容但不推荐（语义层级混乱） |
| **ul/ol/li** | 有序/无序列表 | `style` | 支持自定义 `list-style-type`（圆点、数字、空心等），建议通过 `padding-left` 控制缩进，避免默认样式错乱 |
| **blockquote** | 引用块 | `style` | 自带左边框和内边距，可通过 style 完全自定义背景、边框、间距，适合引用、备注内容 |
| **code** | 行内代码 | `style` | 适合行内短代码，默认等宽字体，可自定义背景、内边距、圆角 |
| **pre** | 块级代码块 | `style` | 适合多行代码，需处理空格和换行（用 `\u00A0` 替代普通空格避免缩进丢失），超长内容建议开启自动换行 |
| **section/div** | 布局容器 | `style` | 微信编辑器原生大量使用 `section`，比 `div` 兼容性更好，不会被自动转为 p 标签，推荐用于布局容器 |
| **hr** | 分隔线 | `style` | 可自定义高度、背景、边框、外边距，实现个性化分隔线效果 |

### 2.2 有限支持的标签（有严格限制，需谨慎使用）

| 标签 | 支持范围 | 核心限制 |
|------|----------|----------|
| **a（超链接）** | 1. 仅支持跳转公众号已发布文章链接、微信小程序路径，外部 http/https 链接仅认证服务号可有限使用，个人号会被直接过滤<br>2. 仅支持 `href`、`target="_blank"`、`style` 属性，其他属性会被剥离<br>3. 不支持锚点跳转（id 属性被过滤，`href="#xxx"` 失效） |
| **img（图片插入）** | 1. src 必须使用微信素材库 CDN 地址（`mmbiz.qpic.cn` 域名），外部链接、Base64 图片会被屏蔽<br>2. 支持 `style`、`width`、`height`、`alt` 属性，建议设置 `max-width:100%` 避免溢出<br>3. 不支持 `onload`、`onerror` 等事件属性 |
| **table/thead/tbody/tr/td/th** | 1. 仅支持简单表格，复杂合并单元格（`colspan`/`rowspan`）兼容性差，易出现排版错乱<br>2. 仅支持 `border`、`padding`、`width`、`text-align`、`background` 等基础样式<br>3. 不支持 `table-layout: fixed` 以外的复杂布局属性 |
| **svg** | 1. 仅支持白名单内的标签和属性，需符合《融媒体 SVG 交互设计技术规范》<br>2. 不支持内嵌 `script`、外部资源、Base64 图片<br>3. 动画仅支持 SMIL 规范，不支持 CSS 动画<br>4. 详细规则见本文第五部分 |

### 2.3 完全禁用的标签（绝对不可使用，会被直接过滤）

所有涉及脚本、外部嵌入、表单交互、页面完整结构的标签均被完全禁用，包括但不限于：

- **脚本类**：`script`、`noscript`、`embed`、`object`
- **嵌入类**：`iframe`、`frame`、`frameset`
- **表单类**：`form`、`input`、`textarea`、`button`、`select`、`option`
- **页面结构类**：`html`、`head`、`body`、`meta`、`link`、`header`、`footer`、`nav`、`aside`
- **其他风险类**：`canvas`、`video`、`audio`（音视频请使用微信官方 `mpvideo`/`mpvoice` 标签）

---

## 三、CSS 样式完整支持规范

### 3.1 核心支持规则

1. 所有样式必须写在标签的 `style` 属性中，格式为 `style="属性名: 值; 属性名2: 值2;"`，单条样式结尾分号可省略，多条建议保留

2. 颜色值推荐使用十六进制格式（`#333333`），兼容性最好，也支持 `rgb()`/`rgba()`，不支持 `hsl()` 格式

3. 尺寸单位优先使用 **px**（最稳定），也支持 `%`、`vw`、`vh`，不支持 `rem`、`em`（部分场景解析异常）

4. 带私有前缀的属性需补充标准属性，例如 `-webkit-border-radius` 配合 `border-radius` 使用，提升兼容性

### 3.2 完全支持的 CSS 属性（稳定生效，无兼容问题）

#### 文本样式类

| 属性 | 支持范围 | 开发建议 |
|------|----------|----------|
| **font-size** | 全支持，无单位限制 | 正文推荐 15-16px，注释 12-13px，标题 18-24px，避免小于 12px（微信最小字号限制） |
| **font-weight** | 支持数值（100-900）和关键字（normal/bold） | 加粗用 700/bold，常规用 400/normal，不推荐使用极细/极粗字重（部分字体不支持） |
| **font-style** | 支持 normal/italic/oblique | 斜体用 italic，避免使用 oblique（兼容性差） |
| **color** | 全支持，十六进制/rgb/rgba | 正文推荐 `#333333`/`#444444`，避免纯黑 `#000000`（视觉压迫感强），rgba 注意透明度适配深色模式 |
| **text-align** | 支持 left/center/right/justify | 正文推荐左对齐，标题可居中，长文本不推荐两端对齐（易出现字间距错乱） |
| **line-height** | 支持数值、带单位数值 | 正文推荐 1.5-1.75，标题推荐 1.2-1.4，无单位数值兼容性最好（自动继承字号） |
| **letter-spacing** | 全支持 | 正文推荐 0.5px，标题推荐 1-2px，提升可读性，避免过大导致排版错乱 |
| **text-decoration** | 支持 none/underline/line-through/overline | 下划线用 underline，删除线用 line-through，链接默认下划线可通过 none 去除 |
| **text-indent** | 全支持 | 段首缩进用 2em，仅中文排版推荐使用，英文不建议 |
| **word-break** | 支持 normal/break-all/keep-all | 长文本、英文单词推荐用 break-all，避免换行溢出 |
| **white-space** | 支持 normal/pre/nowrap | 代码块用 pre-wrap，避免换行失效，单行文本不换行用 nowrap |

#### 盒模型与布局类

| 属性 | 支持范围 | 开发建议 |
|------|----------|----------|
| **width/max-width/min-width** | 全支持 | 容器推荐 `max-width: 100%`，避免固定宽度导致移动端溢出，不推荐设置 height 固定值（适配内容自适应） |
| **margin** | 全支持，四个方向均可单独设置 | 段落间距用 `margin-bottom`，避免同时设置上下 margin（外边距折叠），负值 margin 仅部分场景生效，不推荐使用 |
| **padding** | 全支持，四个方向均可单独设置 | 容器内边距优先使用，比 margin 更稳定，无折叠问题 |
| **display** | 支持 block/inline/inline-block/flex/none | 推荐用 flex 实现多列布局，兼容性良好；inline-block 用于行内块元素；none 用于隐藏元素，稳定生效 |
| **flex 相关属性** | 支持 flex-direction/justify-content/align-items/flex-wrap/flex/gap | 公众号对 flex 布局兼容性良好，是实现多列布局的首选，建议添加 `flex-wrap: wrap` 避免移动端溢出 |
| **box-sizing** | 支持 border-box/content-box | 推荐全局用 `box-sizing: border-box`，避免内边距导致容器宽度溢出 |

#### 边框与背景类

| 属性 | 支持范围 | 开发建议 |
|------|----------|----------|
| **border** | 全支持，可单独设置四个方向的边框、样式、颜色、圆角 | 支持 solid/dashed/dotted 等边框样式，推荐简写格式 `border: 1px solid #e5e7eb;` |
| **border-radius** | 全支持，支持百分比、固定数值 | 圆角效果稳定，图片、卡片均可使用，圆形用 50%，注意配合 `overflow: hidden` 使用 |
| **background-color** | 全支持，十六进制/rgb/rgba | 纯色背景完全兼容，渐变背景仅支持简单线性渐变，复杂渐变建议用图片替代 |
| **box-shadow** | 基础支持 | 支持简单阴影 `box-shadow: 0 2px 8px rgba(0,0,0,0.1);`，多层阴影、复杂阴影部分场景会被过滤，不推荐使用 |
| **opacity** | 全支持，数值 0-1 | 透明度效果稳定，注意半透明元素在深色模式的适配 |

### 3.3 有限支持的 CSS 属性（兼容性差，有严格限制）

| 属性 | 支持情况 | 核心限制 |
|------|----------|----------|
| **position** | 基本不支持 | `position: relative` 部分场景可生效，absolute/fixed/sticky 会被直接过滤，完全失效，禁止使用 |
| **z-index** | 完全不支持 | 无定位属性的情况下，z-index 无任何作用，会被直接过滤 |
| **float** | 兼容性极差 | 仅简单场景可生效，复杂布局会出现高度塌陷、排版错乱，强烈不推荐使用，用 flex 布局替代 |
| **transform** | 部分支持 | 简单的 rotate/scale 可在部分设备生效，复杂变换会被过滤，且 iOS 和安卓端表现不一致，不推荐使用 |
| **transition/animation** | 完全不支持 | 无 style 标签无法定义关键帧，属性会被直接过滤，动效请使用 SVG SMIL 动画实现 |
| **background-image** | 严格限制 | 仅支持微信素材库 CDN 的图片链接，不支持渐变、svg 背景，且兼容性差，不推荐使用 |
| **overflow** | 部分支持 | `overflow: hidden` 可配合 border-radius 使用，scroll/auto 会被过滤，无法实现滚动容器 |
| **grid 布局** | 完全不支持 | 所有 grid 相关属性都会被过滤，禁止使用 |

### 3.4 完全禁用的 CSS 特性

1. **所有 CSS 规则**：`@media` 媒体查询、`@keyframes` 关键帧、`@font-face` 自定义字体、`@import` 样式引入

2. **所有选择器**：类选择器、ID 选择器、伪类/伪元素、属性选择器、后代选择器等

3. **所有涉及交互、动效、定位的复杂属性**，以及可能引发安全问题的属性

---

## 四、特殊元素开发规范

### 4.1 图片开发规范

#### 必填步骤

图片必须先上传至微信公众平台「素材管理-图片素材」，上传后右键复制图片链接，替换到 `src` 属性中。

#### 标准代码示例

```html
<!-- 基础居中图片，推荐使用 -->
<p style="text-align: center; margin: 16px 0;">
  <img
    src="https://mmbiz.qpic.cn/xxx/0?wx_fmt=png"
    alt="图片描述"
    style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);"
  />
</p>
```

#### 避坑提示

- 禁止使用本地路径、外部图床链接、Base64 编码图片，会被直接屏蔽
- 必须设置 `max-width: 100%; height: auto;`，避免图片溢出屏幕、变形
- 图片宽度建议不超过 2000px，文件大小不超过 10MB，避免加载缓慢

### 4.2 超链接开发规范

#### 支持的链接类型

- 公众号已发布文章的永久链接（最稳定，全账号支持）
- 微信小程序路径（需填写小程序 AppID 和路径，全账号支持）
- 微信白名单内的官方链接，认证服务号可支持已备案的企业官网链接

#### 标准代码示例

```html
<!-- 公众号文章链接 -->
<a href="https://mp.weixin.qq.com/s/xxx" target="_blank" style="color: #1890ff; text-decoration: none; border-bottom: 1px solid #1890ff;">
  点击跳转相关文章
</a>
```

#### 避坑提示

- 个人号禁止使用外部 http/https 链接，会被直接过滤
- 不支持锚点跳转（id 属性被过滤，`href="#xxx"` 完全失效）
- 链接颜色建议统一，避免频繁更换颜色影响阅读体验

### 4.3 代码块开发规范

#### 核心问题

微信会合并连续空格、转换换行符，导致代码缩进丢失、换行错乱，需特殊处理。

#### 标准代码示例

```html
<pre style="background-color: #f6f8fa; padding: 16px; border-radius: 8px; overflow-x: auto; font-family: monospace; font-size: 14px; line-height: 1.5; color: #333;">
function helloWorld() {
\u00A0\u00A0console.log("Hello WeChat!");
}
</pre>
```

#### 避坑提示

- 用 `\u00A0` 替代普通空格，避免缩进被合并
- 代码内换行用 `<br>` 替代 `\n`，确保换行生效
- 长代码建议设置 `overflow-x: auto`，避免横向溢出

---

## 五、SVG 交互排版开发规范

公众号 SVG 交互排版是唯一支持的动效、交互实现方式，需严格遵守微信官方合作制定的《融媒体 SVG 交互设计技术规范》。

### 5.1 核心支持规则

1. 仅支持 SVG 1.1 规范，不支持 SVG 2.0 新增特性
2. 动画仅支持 SMIL 规范，不支持 CSS 动画、JS 交互
3. 所有资源必须内嵌，不支持外部链接、外部图片、Base64 资源
4. 所有动画属性必须在官方白名单内，超出白名单的属性会被直接过滤

### 5.2 核心支持的 SVG 标签与属性白名单

| 标签类型 | 支持的标签 | 核心支持的属性 |
|----------|-----------|---------------|
| **基础结构** | svg、g、defs | width、height、viewBox、id（SVG 内可生效）、fill、stroke |
| **图形元素** | rect、circle、ellipse、line、polyline、polygon、path | 所有基础绘图属性，x、y、d、r、points 等 |
| **文本元素** | text、tspan | x、y、font-size、fill、text-anchor，需添加 `leaf=""` 属性避免被过滤 |
| **动画元素** | animate、animateTransform、animateMotion、set | 仅支持白名单内的 attributeName，详见下方 |
| **其他元素** | clipPath、mask | 基础裁剪、遮罩功能，复杂效果兼容性差 |

### 5.3 动画属性白名单（attributeName）

仅以下属性可用于 SVG 动画，超出范围会被直接过滤：

1. **基础属性**：x、y、width、height、opacity、visibility、r
2. **路径与图形**：d、points、fill、stroke、stroke-width、stroke-dasharray、stroke-dashoffset、stroke-linecap
3. **变换属性**：translate、scale、rotate、skewX、skewY（仅用于 animateTransform）
4. **路径动画**：path（仅用于 animateMotion）

### 5.4 严格限制与禁止项

1. 禁止使用 `script` 标签、`on*` 事件属性，所有 JS 交互完全失效
2. 禁止使用 `externalResourcesRequired`、`xlink:href` 引用外部资源
3. 宽度/高度动画的 `repeatCount` 禁止设置为 `indefinite`（无限循环），会被强制改为 undefined 导致动画失效，仅支持固定循环次数
4. 禁止使用负 margin、负 translate 实现超出视口的隐藏内容，会被过滤
5. 禁止使用会导致页面高度动态变化的无限循环动画，避免干扰留言区等页面模块

---

## 六、开发调试与避坑指南

### 6.1 标准开发流程

1. **本地编写**：在 VS Code、CodePen 等工具中编写 HTML 代码，使用内联样式，提前规避禁用的标签和属性

2. **代码转换**：使用 juice 等工具将 CSS 样式批量内联化，处理代码块的空格、换行问题

3. **粘贴测试**：将渲染后的 HTML 内容（不是源码）复制，粘贴到公众号编辑器中，不要直接粘贴源码

4. **预览校验**：点击公众号编辑器「预览」，发送到手机微信，检查样式是否生效、有无错乱、图片是否正常显示

5. **问题排查**：若样式丢失，在编辑器中切换到「HTML 模式」，查看代码是否被过滤，定位被剥离的属性/标签，替换为兼容方案

### 6.2 高频问题与解决方案

| 常见问题 | 核心原因 | 解决方案 |
|----------|----------|----------|
| **粘贴后样式完全丢失** | 使用了 `<style>` 标签、非内联样式，或禁用的 CSS 属性 | 所有样式改为内联 style 属性，移除禁用的属性和标签 |
| **代码块缩进、换行错乱** | 微信合并连续空格、转换换行符 | 用 `\u00A0` 替代普通空格，`\n` 替换为 `<br>`，使用 pre+code 组合 |
| **图片无法显示** | 使用了外部图床、本地路径、Base64 图片 | 图片必须上传到微信素材库，使用 mmbiz 域名的链接 |
| **flex 布局在手机端错乱** | 未设置 `flex-wrap: wrap`，固定宽度溢出 | 给 flex 容器添加 `flex-wrap: wrap;`，子元素设置 min-width 避免溢出 |
| **电脑端预览正常，手机端样式错乱** | 使用了固定大宽度、禁用的属性，或单位不兼容 | 所有容器设置 `max-width: 100%`，优先使用 px 单位，避免百分比高度 |
| **链接无法点击、被过滤** | 使用了外部链接、个人号使用非公众号文章链接 | 个人号仅使用公众号已发布文章链接，认证号按规则使用外链 |

### 6.3 开发工具推荐

| 工具类型 | 推荐工具 | 用途说明 |
|----------|----------|----------|
| **CSS 内联化** | juice | 开源工具，批量将 CSS 转为内联样式 |
| **Markdown 转公众号 HTML** | Markdown Nice、bm.md、Typora+配套插件 | 快速将 Markdown 转为兼容的公众号 HTML |
| **代码编辑器** | VS Code（搭配 HTML/CSS 插件）、CodePen | 在线实时预览，代码高亮 |
| **SVG 交互开发** | JZ Creator、135 编辑器 SVG 工具、秀米 SVG 编辑器 | 可视化设计 SVG 交互效果 |
| **浏览器插件** | 壹伴助手、新媒体管家 | 支持直接在公众号编辑器中编辑 HTML、预览效果 |

---

## 七、可直接复用的开发模板

### 7.1 基础排版通用模板

```html
<!-- 公众号文章基础排版模板 -->
<section style="max-width: 100%; box-sizing: border-box; padding: 0 16px;">
  <!-- 主标题 -->
  <h1 style="font-size: 24px; color: #222222; line-height: 1.3; text-align: center; margin: 24px 0 12px; font-weight: 700; letter-spacing: 1px;">
    文章主标题
  </h1>

  <!-- 副标题/引言 -->
  <p style="font-size: 15px; color: #666666; line-height: 1.6; text-align: center; margin: 0 0 32px;">
    文章副标题/引言内容，补充说明文章主题
  </p>

  <!-- 正文段落 -->
  <p style="font-size: 16px; color: #333333; line-height: 1.75; letter-spacing: 0.5px; margin: 0 0 16px;">
    这里是正文第一段内容，通过<span style="color: #1890ff; font-weight: 700;">span标签</span>实现局部文本高亮，<strong>strong标签实现加粗</strong>，<em>em标签实现斜体</em>。
  </p>

  <p style="font-size: 16px; color: #333333; line-height: 1.75; letter-spacing: 0.5px; margin: 0 0 24px;">
    这里是正文第二段内容，保持统一的字号、行高、颜色，确保排版规范，阅读体验舒适。
  </p>

  <!-- 二级标题 -->
  <h2 style="font-size: 20px; color: #222222; line-height: 1.4; margin: 32px 0 16px; font-weight: 700; padding-left: 12px; border-left: 4px solid #1890ff;">
    二级小标题
  </h2>

  <!-- 无序列表 -->
  <ul style="margin: 0 0 24px; padding-left: 24px;">
    <li style="font-size: 16px; color: #333333; line-height: 1.75; margin: 8px 0;">列表项1</li>
    <li style="font-size: 16px; color: #333333; line-height: 1.75; margin: 8px 0;">列表项2</li>
    <li style="font-size: 16px; color: #333333; line-height: 1.75; margin: 8px 0;">列表项3</li>
  </ul>

  <!-- 引用块 -->
  <blockquote style="margin: 24px 0; padding: 16px; background-color: #f5f7fa; border-left: 4px solid #1890ff; border-radius: 0 4px 4px 0;">
    <p style="font-size: 15px; color: #666666; line-height: 1.6; margin: 0;">
      这里是引用内容，适合标注引用、备注、重点提示等内容，和正文形成视觉区分。
    </p>
  </blockquote>

  <!-- 居中图片 -->
  <p style="text-align: center; margin: 24px 0;">
    <img
      src="https://mmbiz.qpic.cn/xxx/0?wx_fmt=png"
      alt="图片描述"
      style="max-width: 100%; height: auto; border-radius: 8px;"
    />
  </p>

  <!-- 分隔线 -->
  <hr style="height: 1px; background-color: #e5e7eb; border: none; margin: 32px 0;" />

  <!-- 结尾段落 -->
  <p style="font-size: 16px; color: #333333; line-height: 1.75; letter-spacing: 0.5px; margin: 0;">
    文章结尾内容，总结全文，引导读者互动。
  </p>
</section>
```

### 7.2 两列图文卡片模板

```html
<!-- 两列图文卡片，flex布局，移动端自适应 -->
<section style="display: flex; align-items: center; gap: 16px; padding: 16px; border: 1px solid #e5e7eb; border-radius: 8px; margin: 24px 0; flex-wrap: wrap;">
  <!-- 左侧图片 -->
  <div style="flex: 0 0 120px; width: 120px;">
    <img
      src="https://mmbiz.qpic.cn/xxx/0?wx_fmt=png"
      alt="卡片图片"
      style="width: 100%; height: auto; border-radius: 4px;"
    />
  </div>
  <!-- 右侧文本 -->
  <div style="flex: 1; min-width: 200px;">
    <p style="font-size: 17px; color: #222; font-weight: 700; margin: 0 0 8px;">卡片标题</p>
    <p style="font-size: 14px; color: #666; line-height: 1.6; margin: 0;">
      卡片描述内容，补充说明相关信息，支持多行文本，自适应容器宽度。
    </p>
  </div>
</section>
```

### 7.3 三列并列卡片模板

```html
<!-- 三列并列卡片，移动端自动换行 -->
<section style="display: flex; gap: 12px; margin: 24px 0; flex-wrap: wrap;">
  <div style="flex: 1; min-width: 180px; padding: 16px; background-color: #f5f7fa; border-radius: 8px;">
    <p style="text-align: center; font-size: 16px; color: #1890ff; font-weight: 700; margin: 0 0 8px;">标题1</p>
    <p style="text-align: center; font-size: 14px; color: #666; line-height: 1.5; margin: 0;">
      卡片内容描述，支持多行文本，自适应宽度。
    </p>
  </div>
  <div style="flex: 1; min-width: 180px; padding: 16px; background-color: #f5f7fa; border-radius: 8px;">
    <p style="text-align: center; font-size: 16px; color: #1890ff; font-weight: 700; margin: 0 0 8px;">标题2</p>
    <p style="text-align: center; font-size: 14px; color: #666; line-height: 1.5; margin: 0;">
      卡片内容描述，支持多行文本，自适应宽度。
    </p>
  </div>
  <div style="flex: 1; min-width: 180px; padding: 16px; background-color: #f5f7fa; border-radius: 8px;">
    <p style="text-align: center; font-size: 16px; color: #1890ff; font-weight: 700; margin: 0 0 8px;">标题3</p>
    <p style="text-align: center; font-size: 14px; color: #666; line-height: 1.5; margin: 0;">
      卡片内容描述，支持多行文本，自适应宽度。
    </p>
  </div>
</section>
```

---

## 附录：开发检查清单

在开发微信公众号排版时，请务必检查以下项目：

- [ ] 所有样式均使用内联 `style` 属性，无 `<style>` 标签或外部 CSS
- [ ] 仅使用白名单内的 HTML 标签，无禁用标签（script、iframe、form 等）
- [ ] 仅使用白名单内的 CSS 属性，无禁用属性（position、float、animation 等）
- [ ] 图片已上传至微信素材库，src 使用 mmbiz.qpic.cn 域名链接
- [ ] 超链接符合账号类型限制（个人号仅用公众号文章链接）
- [ ] 代码块使用 `\u00A0` 替代空格，避免缩进丢失
- [ ] 所有容器设置 `max-width: 100%`，避免移动端溢出
- [ ] flex 布局添加 `flex-wrap: wrap`，确保移动端自适应
- [ ] 无固定高度设置，使用内容自适应高度
- [ ] SVG 动画符合 SMIL 规范，无无限循环动画

---

**文档维护说明**：

本文档基于 2026 年 2 月的最新规则整理，如微信公众平台更新规则，请及时更新本文档。

如有任何疑问或补充，请联系项目维护人员。
