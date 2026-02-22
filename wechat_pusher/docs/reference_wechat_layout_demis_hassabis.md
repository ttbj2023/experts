# 微信公众号文章版式参考 - Demis Hassabis访谈

> 来源文件：Demis Hassabis最新万字访谈.html
> 分析日期：2025-02-19
> 版式风格：科技访谈类 - 专业严谨风格

---

## 1. 整体排版规范

### 基础字体设置
```css
/* 全局字体 */
font-family: Optima-Regular, PingFangTC-light
font-size: 15px
line-height: 26px
color: #333 (rgb(51, 51, 51))
letter-spacing: 1px
word-break: break-word
```

### 段落间距
```css
margin-top: 16px
margin-bottom: 16px
```

---

## 2. 开篇引用框设计

### 外层容器
```css
width: 100%
padding: 0px 16px
```

### 灰色背景框
```css
width: 100%
text-align: left
background: rgb(237, 237, 237)
padding: 16px 14px 17px 16px
```

### 引用文字
```css
font-size: 14px
color: rgba(0, 0, 0, 0.65)
line-height: 26px
font-family: Futura-Medium
```

### HTML结构示例
```html
<section style="width: 100%; padding: 0px 16px;">
  <section style="width: 100%;">
    <section style="width: 100%; text-align: left; background: rgb(237, 237, 237); padding: 16px 14px 17px 16px;">
      <p style="font-size: 14px; color: rgba(0, 0, 0, 0.65); line-height: 26px;">
        引用内容
      </p>
    </section>
  </section>
</section>
```

---

## 3. 章节标题系统（核心设计亮点）

### 整体结构
```
┌─────────────────────────────┐
│          01                 │  ← 数字编号（居中、大字号、阴影）
│   ┌──────────────────┐      │
│   │  章节标题文字    │      │  ← 倾斜背景块（内层文字反向倾斜）
│   └──────────────────┘      │
└─────────────────────────────┘
```

### 数字编号样式
```css
font-weight: bold
font-size: 30px
color: #004080
line-height: 42px
text-shadow: 2px 2px 0px #FFDF21
word-break: break-word
text-align: center
font-family: Futura-Medium
```

### 倾斜背景块容器
```css
align-self: center
background: #004080
transform: skewX(-7deg)  /* 外层倾斜-7度 */
padding: 4px 16px 3px 16px
margin: 0 0 26px 0
```

### 内层文字（反向倾斜）
```css
transform: skewX(7deg)  /* 内层倾斜+7度，抵消外层倾斜 */
font-weight: bold
font-size: 18px
color: rgb(255, 255, 255)
line-height: 25px
word-break: break-word
font-family: Optima-Regular, PingFangTC-light
```

### HTML完整结构
```html
<section style="width: 100%; display: flex; flex-direction: column;">
  <!-- 数字编号 -->
  <section style="text-align: center;">
    <section style="font-weight: bold; font-size: 30px; color: #004080; line-height: 42px; text-shadow: 2px 2px 0px #FFDF21;">
      01
    </section>
  </section>

  <!-- 倾斜标题块 -->
  <section style="align-self: center; background: #004080; transform: skewX(-7deg); padding: 4px 16px 3px 16px; margin: 0 0 26px 0;">
    <section style="transform: skewX(7deg);">
      <section style="font-weight: bold; font-size: 18px; color: rgb(255, 255, 255); line-height: 25px;">
        章节标题文字
      </section>
    </section>
  </section>
</section>
```

---

## 4. 正文内容样式

### 标准段落
```css
font-size: 15px
margin-bottom: 16px
color: rgb(51, 51, 51)
margin-top: 16px
letter-spacing: 1px
font-family: Optima-Regular, PingFangTC-light
```

### 加粗强调文字
```css
font-weight: bold
```

### HTML示例
```html
<section style="font-size: 15px; margin-bottom: 16px; color: rgb(51, 51, 51); margin-top: 16px; letter-spacing: 1px;">
  普通文字，<span style="font-weight: bold;">加粗强调文字</span>，继续普通文字。
</section>
```

---

## 5. 图片样式

### 容器
```css
text-align: center
```

### 图片本身
```css
class="rich_pages wxw-img js_insertlocalimg"
display: block
width: auto (实际渲染约为660px)
height: auto
```

### HTML示例
```html
<section style="text-align: center;">
  <img
    class="rich_pages wxw-img"
    data-ratio="0.6990740740740741"
    data-src="图片URL"
    data-type="png"
    data-w="1080"
    style="width: 660.984px; height: auto;"
    alt="图片"
  />
</section>
```

---

## 6. 问答格式（Q&A）

### 问题样式
```css
font-size: 14px
font-weight: bold
font-family: Futura-Medium
```

### 答案样式
```css
font-size: 14px
font-family: Futura-Medium (正常字重)
```

### HTML示例
```html
<!-- 问题 -->
<section style="font-size: 15px; margin-bottom: 16px; color: rgb(51, 51, 51); margin-top: 16px; letter-spacing: 1px;">
  <span style="font-family: Futura-Medium; font-size: 14px; font-weight: bold;">
    Q1：这是问题？
  </span>
</section>

<!-- 答案 -->
<section style="font-size: 15px; margin-bottom: 16px; color: rgb(51, 51, 51); margin-top: 16px; letter-spacing: 1px;">
  <span style="font-family: Futura-Medium; font-size: 14px;">
    这是答案内容。
  </span>
</section>
```

---

## 7. 颜色方案

| 元素 | 颜色值 | RGB/HEX |
|------|--------|---------|
| 正文文字 | 深灰 | `rgb(51, 51, 51)` / `#333333` |
| 主色调（蓝色） | 深蓝 | `#004080` |
| 强调色（黄色） | 亮黄 | `#FFDF21` |
| 引用框背景 | 浅灰 | `rgb(237, 237, 237)` / `#EDEDED` |
| 引用框文字 | 半透明黑 | `rgba(0, 0, 0, 0.65)` |
| 标题文字 | 纯白 | `rgb(255, 255, 255)` / `#FFFFFF` |

---

## 8. 字体家族使用

| 用途 | 字体 |
|------|------|
| 正文内容 | `Optima-Regular, PingFangTC-light` |
| 引用框内容 | `Futura-Medium` |
| 数字编号 | `Futura-Medium` |
| 问答内容 | `Futura-Medium` |

---

## 9. 响应式与兼容性

### 微信公众号特有属性
```html
<meta name="wechat-enable-text-zoom-em" content="true">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=0,viewport-fit=cover">
```

### 文字缩放变量
```css
--content-font-scale: 100
--content-font-scale-percent: 100%
text-size-adjust: var(--content-font-scale-percent, inherit)
```

---

## 10. 设计特点总结

### 优点
✅ **视觉层次清晰**：通过大小、颜色、阴影区分标题级别
✅ **专业感强**：倾斜标题设计独特但不失稳重
✅ **配色协调**：深蓝+黄的经典配色，适合科技/商业内容
✅ **可读性好**：合理的字号、行距、字间距
✅ **结构化强**：章节编号+标题的形式便于导航

### 适用场景
- 📊 行业分析报告
- 💼 商业访谈
- 🔬 科技深度解读
- 📈 数据分析文章
- 🎯 案例研究

### 注意事项
⚠️ 字体家族（Optima、Futura）在非Apple设备上可能回退
⚠️ 倾斜效果需要使用transform，旧版微信可能不支持
⚠️ 文字阴影在某些设备上可能显示不一致

---

## 11. 实现建议

### 如果要在项目中应用此版式

#### 方案A：内联样式（推荐用于微信公众号）
直接使用上述HTML示例中的内联样式，确保兼容性。

#### 方案B：CSS类名（推荐用于网页）
将样式提取为CSS类，便于维护：
```css
.wz-section-number {
  font-weight: bold;
  font-size: 30px;
  color: #004080;
  line-height: 42px;
  text-shadow: 2px 2px 0px #FFDF21;
  text-align: center;
}

.wz-title-skewed {
  background: #004080;
  transform: skewX(-7deg);
  padding: 4px 16px 3px 16px;
  margin: 0 0 26px 0;
}

.wz-title-text {
  transform: skewX(7deg);
  font-weight: bold;
  font-size: 18px;
  color: #fff;
  line-height: 25px;
}
```

#### 方案C：Markdown扩展
如果使用Markdown，可以定义自定义语法：
```
### 01. 章节标题
```
然后通过转换器自动生成上述HTML结构。

---

**文档版本**: v1.0
**最后更新**: 2025-02-19
**维护者**: Claude Code
