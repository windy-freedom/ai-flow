# 自动化内容生成计划 (已完成)

## 目标
每日获取关键词（暂缓），利用MiniMax API生成简短的提示词，然后使用MiniMax API生成图片，最后使用MiniMax API生成视频，并保存所有生成内容。

## 核心组件与流程

### 1. 关键词获取
*   **状态：** 暂缓处理。

### 2. 提示词生成 (使用MiniMax API)
*   **服务：** MiniMax API。
*   **工具：** `prompt_generator.py` 脚本。
*   **流程：**
    *   接收用户输入的关键词。
    *   调用MiniMax API，根据关键词生成简短的提示词。
*   **参数配置：**
    *   模型选择：`"MiniMax-Text-01"` (默认)
    *   生成长度：简短 (用户偏好)

### 3. 图片生成 (使用MiniMax API)
*   **服务：** MiniMax API。
*   **工具：** `minimax_image_generator.py` 脚本。
*   **流程：**
    *   使用 `prompt_generator.py` 生成的提示词作为输入。
    *   调用MiniMax API生成图片。
    *   将生成的图片下载并保存到本地。
*   **参数配置：**
    *   模型 (`model`): `"image-01"` (默认)
    *   提示词 (`prompt`): 由 `prompt_generator.py` 动态生成。
    *   宽高比 (`aspect_ratio`): `"16:9"` (默认)
    *   响应格式 (`response_format`): `"url"`
    *   生成数量 (`n`): `3`
    *   提示词优化 (`prompt_optimizer`): `True`
    *   保存文件名格式: `YYYY-MM-DD-ai-art-序号.jpg`

### 4. 视频生成 (使用MiniMax API)
*   **服务：** MiniMax API。
*   **工具：** `minimax_video_generator.py` 脚本。
*   **流程：**
    *   使用上一步生成的图片作为输入。
    *   调用MiniMax API提交视频生成任务。
    *   查询任务状态直至完成。
    *   下载生成的视频。
*   **参数配置：**
    *   模型 (`model`): `"MiniMax-Hailuo-02"` (默认)
    *   视频提示词 (`prompt`): (无)
    *   首帧图片路径 (`your_file_path`): (动态设置为上一步生成的图片路径，例如 `d:/AI-image/2025-07-23-ai-art-001.jpg`)
    *   时长 (`duration`): `6` 秒
    *   分辨率 (`resolution`): `"768P"`

### 5. 文件保存
*   **命名模式：** `日期-关键词-提示词（关键单词）-序号` (例如: `2025-07-23-ai-art-001.jpg` 和 `2025-07-23-ai-art-video-001.mp4`)。
*   **保存方式：**
    *   下载生成的图片和视频。
    *   按照指定的命名模式保存到本地。

## 自动化工作流程概述

1.  **每日触发：** 脚本或任务调度器启动。
2.  **获取热点：** (暂缓)
3.  **提取关键词：** (暂缓)
4.  **生成提示词：** 调用 `prompt_generator.py`，根据用户提供的关键词生成简短的提示词。
5.  **生成图片：** 调用 `minimax_image_generator.py`，使用生成的提示词和默认参数生成图片，并保存到本地。
6.  **生成视频：** 调用 `minimax_video_generator.py`，使用上一步生成的图片和默认参数生成视频，并下载。
7.  **下载并保存：** 下载生成的图片和视频，并按照命名格式保存。

## 后续步骤与待确认事项

*   **实际运行时的提示词：** 如何从 `minimax_api_client.py` 获取单个“简短”提示词，并将其作为输入传递给 `minimax_image_generator.py`？ (此步骤已通过 `prompt_generator.py` 替代，但需要用户提供关键词)
*   **切换模式：** 当您准备好执行完整的自动化流程时，请告诉我，我将请求您切换到 ACT MODE。
