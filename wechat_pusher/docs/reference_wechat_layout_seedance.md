# 微信公众号文章版式参考 - Seedance 2.0冲击波

> 来源文件：Seedance 2.0冲击波.html
> 分析日期：2025-02-19
> 版式风格：科技新闻报道 - 杂志风格

---

## 1. 整体排版规范

### 基础字体设置
```css
font-size: 16px
color: rgb(62, 62, 62)
text-align: justify
font-style: normal
font-weight: 400
```

### 正文容器
```css
font-size: 15px
padding: 0px 10px
line-height: 2
```

### 段落间距
```css
margin-top: 32px
margin-bottom: 32px
line-height: 1.75em
```

---

## 2. 开篇设计（核心亮点 - 杂志封面式布局）

### 整体结构
- **卡片式布局**：带阴影的卡片容器
- **图片+文字叠加**：图片上有说明文字
- **装饰性线条**：底部有彩色分隔线
- **作者信息**：灰色小字显示作者和编辑

### 卡片容器
```css
margin: 20px 0%
text-align: center
justify-content: center
display: flex
flex-flow: row
```

### 内层卡片
```css
display: inline-block
width: 95%
vertical-align: top
box-shadow: rgb(158, 158, 158) 0px 0px 4px
align-self: flex-start
```

### 图片说明文字
```css
font-size: 14px
color: rgb(160, 160, 160)
padding: 0px 10px
text-align: left
line-height: 2
letter-spacing: 0px
```

### 彩色分隔线设计
```css
/* 左侧深色线 */
display: inline-block
vertical-align: top
width: 50%
padding: 0px 0px 0px 2px
background-color: rgb(77, 75, 75)
height: 4px

/* 右侧浅色线 */
display: inline-block
vertical-align: top
width: 50%
padding: 0px 2px 0px 0px
background-color: rgb(171, 171, 171)
height: 1px
```

### HTML完整结构
```html
<section style="margin: 20px 0%; text-align: center; display: flex;">
  <section style="display: inline-block; width: 95%; box-shadow: rgb(158, 158, 158) 0px 0px 4px;">
    <!-- 图片 -->
    <section style="margin: 0px 0% -7px; line-height: 0;">
      <img src="..." style="width: 100%;" />
    </section>

    <!-- 图片说明 -->
    <section style="margin: 12px 0% 8px;">
      <section style="font-size: 14px; color: rgb(160, 160, 160);">
        <p>产业洗牌已然开始。</p>
      </section>
    </section>

    <!-- 装饰图标 -->
    <section style="text-align: right; margin: 10px 0px; transform: translate3d(-15px, 0px, 0px);">
      <img src="..." style="width: 25%;" />
    </section>

    <!-- 分隔线 -->
    <section>
      <section style="display: inline-block; width: 50%; background-color: rgb(77, 75, 75); height: 4px;"></section>
      <section style="display: inline-block; width: 50%; background-color: rgb(171, 171, 171); height: 1px;"></section>
    </section>
  </section>
</section>
```

---

## 3. 作者信息栏

### 样式
```css
font-size: 15px
padding: 0px 10px
text-align: left
color: rgb(160, 160, 160)
```

### HTML示例
```html
<section style="font-size: 15px; padding: 0px 10px; text-align: left; color: rgb(160, 160, 160);">
  <p>作者 | 郑敏芳 编辑 | 松壑</p>
</section>
```

---

## 4. 章节标题系统（独特设计 - 工业风数字编号）

### 整体结构
```
┌──────────────┬────────────────────┬──────────────┐
│   虚线       │      圆形徽章       │   虚线       │
│              │   ┌───────────┐    │              │
│              │   │    1      │    │              │
│              │   └───────────┘    │              │
└──────────────┴────────────────────┴──────────────┘
              章节标题文字
```

### 容器
```css
text-align: center
margin: 10px 0%
justify-content: center
display: flex
flex-flow: row
```

### 左右虚线
```css
display: inline-block
vertical-align: middle
width: 20%
align-self: center
```

### 虚线样式
```css
border-top: 1px dashed rgb(255, 255, 255)
```

### 圆形徽章（核心设计）
```css
/* 外层容器 */
display: inline-block
vertical-align: middle
width: 20%
align-self: center

/* 倾斜边框 */
width: 1.76em
height: 0.5em
margin-bottom: -0.5em
margin-left: 0.25em
border-left: 1px solid rgb(10, 10, 10)
border-right: 1px solid rgb(10, 10, 10)
transform: skew(-45deg)
-webkit-transform: skew(-45deg)
-moz-transform: skew(-45deg)
-o-transform: skew(-45deg)

/* 蓝色方块 */
width: 1.8em
height: 1.8em
margin-left: 0.5em
background-color: rgb(0, 138, 255)

/* 数字圆圈 */
width: 1.2em
height: 1.2em
margin-top: -0.88em
line-height: 1.2em
background-color: rgb(10, 10, 10)
color: rgb(255, 255, 255)
font-size: 17px

/* 底部标记 */
transform: rotate(-45deg)
-webkit-transform: rotate(-45deg)
-moz-transform: rotate(-45deg)
-o-transform: rotate(-45deg)

/* 底部横线 */
width: 0.68em
border-bottom: 1px solid rgb(10, 10, 10)
margin-left: 2em
margin-top: 0.4em
```

### 章节标题
```css
padding: 0px 10px
font-size: 15px
color: rgb(10, 10, 10)
text-align: center
font-weight: bold
```

### HTML完整结构
```html
<section style="text-align: center; margin: 10px 0%; display: flex;">
  <!-- 左虚线 -->
  <section style="display: inline-block; width: 20%;">
    <section style="border-top: 1px dashed rgb(255, 255, 255);"></section>
  </section>

  <!-- 圆形徽章 -->
  <section style="display: inline-block; width: 20%;">
    <section style="display: inline-block; overflow: hidden;">
      <!-- 倾斜边框 -->
      <section style="width: 1.76em; height: 0.5em; margin-bottom: -0.5em; border-left: 1px solid rgb(10, 10, 10); border-right: 1px solid rgb(10, 10, 10); transform: skew(-45deg);"></section>

      <!-- 蓝色方块 -->
      <section style="width: 1.8em; height: 1.8em; margin-left: 0.5em; background-color: rgb(0, 138, 255);"></section>

      <!-- 数字 -->
      <section style="width: 1.2em; height: 1.2em; margin-top: -0.88em; line-height: 1.2em; background-color: rgb(10, 10, 10); color: rgb(255, 255, 255); font-size: 17px;">
        <p>1</p>
      </section>

      <!-- 底部横线 -->
      <section style="transform: rotate(-45deg);">
        <section style="width: 0.68em; border-bottom: 1px solid rgb(10, 10, 10); margin-left: 2em; margin-top: 0.4em;"></section>
      </section>
    </section>
  </section>

  <!-- 右虚线 -->
  <section style="display: inline-block; width: 20%;">
    <section style="border-top: 1px dashed rgb(255, 255, 255);"></section>
  </section>
</section>

<!-- 标题文字 -->
<section style="padding: 0px 10px; font-size: 15px; color: rgb(10, 10, 10); text-align: center;">
  <p><strong>视频产能的爆炸</strong></p>
</section>
```

---

## 5. 正文内容样式

### 标准段落
```css
font-size: 15px
padding: 0px 10px
line-height: 2
margin: 32px 0px
line-height: 1.75em
```

### 字间距强调
```css
letter-spacing: 2px
```

### HTML示例
```html
<section style="font-size: 15px; padding: 0px 10px; line-height: 2;">
  <p style="margin: 32px 0px; line-height: 1.75em;">
    <span style="letter-spacing: 2px;">正文内容</span>
  </p>
</section>
```

---

## 6. 图片样式

### 基本样式
```css
class="rich_pages wxw-img"
width: 100%
height: auto
display: block
```

### HTML示例
```html
<section style="text-align: center;">
  <img
    data-src="图片URL"
    class="rich_pages wxw-img"
    style="width: 100%; height: auto;"
    alt="图片"
  />
</section>
```

---

## 7. 版权声明

### 样式
```css
font-size: 12px
color: rgb(136, 136, 136)
```

### HTML示例
```html
<p>
  <span style="font-size: 12px; color: rgb(136, 136, 136);">
    *本文为全天候科技原创作品，未经授权不得转载...
  </span>
</p>
```

---

## 8. 颜色方案

| 元素 | 颜色值 | RGB/HEX |
|------|--------|---------|
| 正文文字 | 深灰 | `rgb(62, 62, 62)` / `#3E3E3E` |
| 标题文字 | 纯黑 | `rgb(10, 10, 10)` / `#0A0A0A` |
| 主色调（蓝色） | 亮蓝 | `rgb(0, 138, 255)` / `#008AFF` |
| 作者信息 | 浅灰 | `rgb(160, 160, 160)` / `#A0A0A0` |
| 图片说明 | 浅灰 | `rgb(160, 160, 160)` / `#A0A0A0` |
| 版权声明 | 中灰 | `rgb(136, 136, 136)` / `#888888` |
| 徽章背景 | 纯黑 | `rgb(10, 10, 10)` / `#0A0A0A` |
| 分隔线深色 | 深灰 | `rgb(77, 75, 75)` / `#4D4B4B` |
| 分隔线浅色 | 浅灰 | `rgb(171, 171, 171)` / `#ABABAB` |
| 卡片阴影 | 中灰 | `rgb(158, 158, 158)` / `#9E9E9E` |

---

## 9. 字体与字号使用

| 用途 | 字号 | 字重/样式 |
|------|------|-----------|
| 正文内容 | 15px | normal |
| 段落文字 | 16px | normal |
| 作者信息 | 15px | normal |
| 图片说明 | 14px | normal |
| 章节标题 | 15px | **bold** |
| 章节数字 | 17px | normal |
| 版权声明 | 12px | normal |

---

## 10. 响应式与兼容性

### 宽度设置
- 卡片容器：`width: 95%`
- 章节标题各部分：`width: 20%`
- 图片：`width: 100%`

### 对齐方式
- 正文：`text-align: justify`（两端对齐）
- 标题：`text-align: center`
- 图片：`text-align: center`

---

## 11. 设计特点总结

### 优点
✅ **杂志感强**：卡片式布局+阴影，像杂志封面
✅ **视觉层次丰富**：通过字间距、颜色、大小区分内容
✅ **独特设计语言**：工业风的数字徽章设计
✅ **专业感强**：两端对齐、严格的网格系统
✅ **信息密度适中**：段落间距大（32px），阅读舒适

### 设计亮点
🎨 **卡片阴影**：`box-shadow: rgb(158, 158, 158) 0px 0px 4px` - 微妙的浮起效果
🎨 **彩色分隔线**：深色4px + 浅色1px的不对称设计
🎨 **字间距强调**：关键段落使用`letter-spacing: 2px`
🎨 **工业风徽章**：复杂的CSS变换创建的独特图标
🎨 **两端对齐**：`text-align: justify` - 传统排版风格

### 适用场景
- 📰 新闻报道
- 🔬 科技深度分析
- 📊 行业报告
- 🎯 专题策划
- 💼 商业评论

### 注意事项
⚠️ 章节徽章使用了多个CSS transform，兼容性需测试
⚠️ 两端对齐可能在某些内容下产生不自然的间距
⚠️ 虚线使用白色，仅适用于深色背景
⚠️ 卡片阴影在旧版微信可能显示异常

---

## 12. 与Demis Hassabis文章版式对比

| 特征 | Demis Hassabis | Seedance 2.0 |
|------|----------------|--------------|
| 标题风格 | 倾斜背景块 | 工业风徽章 |
| 主色调 | 深蓝 #004080 | 亮蓝 #008AFF |
| 标题结构 | 数字→标题 | 虚线+徽章+虚线→标题 |
| 开篇设计 | 灰色引用框 | 卡片式图片+说明 |
| 段落间距 | 16px | 32px |
| 字间距 | 1px | 2px（强调段落） |
| 对齐方式 | 左对齐 | 两端对齐 |
| 特色元素 | 文字阴影 | 卡片阴影+彩色线 |
| 整体风格 | 专业严谨 | 杂志时尚 |

---

## 13. 实现建议

### 方案A：简化版徽章（推荐）
原徽章过于复杂，建议简化为：
```html
<section style="text-align: center; margin: 20px 0;">
  <span style="display: inline-block; width: 40px; height: 40px; line-height: 40px; background-color: #008AFF; color: #fff; border-radius: 50%; font-size: 17px;">1</span>
  <h3 style="margin-top: 10px; font-size: 18px; color: #0A0A0A; font-weight: bold;">章节标题</h3>
</section>
```

### 方案B：CSS类名提取
```css
.wz-card-layout {
  margin: 20px 0%;
  text-align: center;
  display: flex;
}

.wz-card-inner {
  display: inline-block;
  width: 95%;
  box-shadow: rgb(158, 158, 158) 0px 0px 4px;
}

.wz-section-badge {
  display: inline-block;
  width: 40px;
  height: 40px;
  background-color: #008AFF;
  color: #fff;
  border-radius: 50%;
  line-height: 40px;
  font-size: 17px;
}

.wz-text-justify {
  text-align: justify;
}

.wz-letter-spacing {
  letter-spacing: 2px;
}
```

### 方案C：组件化封装
创建可复用的组件：
- `CardImage` - 卡片图片组件
- `SectionBadge` - 章节徽章组件
- `AuthorInfo` - 作者信息组件
- `CopyrightNotice` - 版权声明组件

---

**文档版本**: v1.0
**最后更新**: 2025-02-19
**维护者**: Claude Code
