#!/bin/bash
# 输出文件验证脚本
#
# 功能：验证生成的输出文件是否有效
# 输入：文件路径（第一个参数）
# 输出：验证结果（0=成功，1=失败）
#
# 使用方法：
#   ./scripts/validate_output.sh /path/to/output.pdf

set -e  # 遇到错误立即退出

# 获取输出文件路径
OUTPUT_FILE="${1:-}"

# 验证输出文件
if [ -z "$OUTPUT_FILE" ]; then
    echo "错误: 未提供输出文件路径" >&2
    echo "使用方法: $0 <output_file>" >&2
    exit 1
fi

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "错误: 输出文件不存在: $OUTPUT_FILE" >&2
    exit 1
fi

# 获取文件扩展名
FILE_EXT="${OUTPUT_FILE##*.}"
FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null)

echo "验证输出文件..."
echo "文件路径: $OUTPUT_FILE"
echo "文件类型: $FILE_EXT"
echo "文件大小: $FILE_SIZE bytes"

# 检查文件大小（空文件无效）
if [ "$FILE_SIZE" -lt 100 ]; then
    echo "错误: 输出文件太小或为空" >&2
    exit 1
fi

# 根据文件类型进行验证
case "$FILE_EXT" in
    pdf)
        # PDF文件验证（检查文件头）
        if ! head -c 4 "$OUTPUT_FILE" | grep -q "%PDF"; then
            echo "错误: 无效的PDF文件" >&2
            exit 1
        fi
        echo "✓ PDF文件验证通过"
        ;;

    docx|doc)
        # DOCX/DOC文件验证（检查ZIP头或OLE头）
        if ! head -c 4 "$OUTPUT_FILE" | grep -qP "PK\x03\x04|\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"; then
            echo "错误: 无效的Word文档" >&2
            exit 1
        fi
        echo "✓ Word文档验证通过"
        ;;

    md|markdown)
        # Markdown文件验证
        if ! grep -qE "^#{1,6}\s+" "$OUTPUT_FILE"; then
            echo "警告: Markdown文件可能缺少标题" >&2
        fi
        echo "✓ Markdown文件验证通过"
        ;;

    html|htm)
        # HTML文件验证
        if ! grep -qiE "<!DOCTYPE|<html|<body" "$OUTPUT_FILE"; then
            echo "错误: 无效的HTML文件" >&2
            exit 1
        fi
        echo "✓ HTML文件验证通过"
        ;;

    txt)
        # TXT文件验证（检查是否为纯文本）
        if file -b "$OUTPUT_FILE" | grep -qiv "text"; then
            echo "错误: 无效的文本文件" >&2
            exit 1
        fi
        echo "✓ 文本文件验证通过"
        ;;

    *)
        echo "注意: 未知文件类型，跳过详细验证" >&2
        ;;
esac

echo "✓ 输出文件验证成功"
exit 0
