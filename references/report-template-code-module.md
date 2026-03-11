# {{module_name}} — 代码模块解读

> 📍 **模块信息**
> - **模块名称：** {{module_name}}
> - **对应论文章节：** {{paper_section}}
> - **主要文件：** {{primary_files}}
> - **生成时间：** {{generated_date}}

---

## 模块概述

**功能：** {{module_purpose}}

**在整体架构中的位置：**
<!-- INSTRUCTION: 说明此模块在数据流中处于哪个阶段，上游是谁，下游是谁 -->
{{module_position_in_pipeline}}

**输入/输出规格：**
- **输入：** {{module_inputs}}（包含张量形状，如 `(B, 3, 224, 224)`）
- **输出：** {{module_outputs}}（包含张量形状）

---

## 代码位置

| 文件路径 | 关键类/函数 | 作用 |
|----------|------------|------|
| `{{file_1}}` | `{{symbol_1}}` | {{symbol_1_purpose}} |
| `{{file_2}}` | `{{symbol_2}}` | {{symbol_2_purpose}} |
<!-- INSTRUCTION: 列出此模块涉及的所有文件 -->

---

## 逐函数/类详解

<!-- INSTRUCTION: 对此模块中每一个关键函数/类都要完整解读，不要跳过或合并 -->

### {{class_or_func_name}}

**与论文的对应：** {{paper_section_and_equation}}（例：对应论文 3.2 节 Eq.(5)）

**功能简述：** {{brief_purpose}}

```{{language}}
{{complete_code_with_line_numbers}}
```

**逐行注释：**
<!-- INSTRUCTION: 每段代码都要逐行或逐块注释，不允许跳过关键行 -->
- **第 {{line_start_1}}-{{line_end_1}} 行：** {{explanation_1}}
  - 张量形状变化：`{{shape_before}}` → `{{shape_after}}`（若有形状变化）
  - 参数量：{{param_count}}（若有可学习参数）
- **第 {{line_start_2}}-{{line_end_2}} 行：** {{explanation_2}}
- **第 {{line_start_3}}-{{line_end_3}} 行：** {{explanation_3}}
<!-- INSTRUCTION: 覆盖函数的每一个逻辑块 -->

**张量形状追踪（完整）：**
```
输入:    {{input_shape}}
步骤1 ({{op_1}}): {{shape_1}}
步骤2 ({{op_2}}): {{shape_2}}
...
输出:    {{output_shape}}
```

**关键设计细节：**
- {{design_detail_1}}（例：为什么这里用 GroupNorm 而非 BatchNorm？）
- {{design_detail_2}}

**容易踩坑的实现细节：**
- {{gotcha_1}}（例：注意 dim=1 是通道维，不是 batch 维）
- {{gotcha_2}}

**与论文描述的差异（如有）：**
<!-- INSTRUCTION: 若代码实现与论文文字/公式描述不完全一致，明确指出差异 -->
{{implementation_vs_paper_diff}}

<!-- INSTRUCTION: 为模块中每一个关键函数/类复制以上模板 -->

---

## 数据流追踪

<!-- INSTRUCTION: 从本模块的入口到出口，追踪数据完整流程 -->

```
{{data_flow_diagram}}
```

示例格式：
```
输入图像 (B,3,H,W)
    │
    ▼ Conv2d(3→64, k=3, s=1, p=1)
    │ (B,64,H,W)
    │
    ▼ BatchNorm2d(64)
    │ (B,64,H,W)
    │
    ▼ ReLU
    │ (B,64,H,W)
    │
    ▼ MaxPool2d(k=2, s=2)
    │ (B,64,H/2,W/2)
    │
    ▼ 输出
```

---

## 与其他模块的接口

| 方向 | 模块名 | 传递的数据 | 形状 |
|------|--------|-----------|------|
| 上游（输入来自） | {{upstream_module}} | {{upstream_data}} | {{upstream_shape}} |
| 下游（输出去往） | {{downstream_module}} | {{downstream_data}} | {{downstream_shape}} |

---

> 📝 由 paper-reader 生成 | 模块：{{module_name}}
