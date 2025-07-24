# AI Image and Video Generation Workflow

这是一个使用 MiniMax API 自动生成图像和视频的工作流。

## 功能

- 根据关键词生成图像提示。
- 根据生成的提示生成图像。
- 根据图像生成视频。

## 文件说明

- `main_workflow.py`: 主工作流脚本，协调提示、图像和视频的生成。
- `prompt_generator.py`: 使用 MiniMax API 生成图像提示。
- `minimax_image_generator.py`: 使用 MiniMax API 生成图像。
- `minimax_video_generator.py`: 使用 MiniMax API 生成视频。
- `minimax_api_client.py`: MiniMax API 的通用客户端，处理 API 请求和响应。

## 如何运行

1. **安装依赖**:
   确保你安装了 Python 3.x。然后安装所需的库：
   ```bash
   pip install requests
   ```

2. **配置 API Key**:
   为了安全起见，API Key 不应硬编码在代码中。本项目支持以下两种配置方式（优先级从高到低）：

   a. **通过 `config.py` 文件配置 (推荐)**:
      在项目根目录下找到 `config.py` 文件。如果不存在，请手动创建。
      打开 `config.py` 并添加以下内容，将 `你的API_KEY` 替换为你的实际 MiniMax API Key：
      ```python
      MINIMAX_API_KEY = "你的API_KEY"
      ```
      这种方式方便管理，且不易泄露。

   b. **通过环境变量配置**:
      将你的 MiniMax API Key 设置为环境变量 `MINIMAX_API_KEY`。
      **Windows**:
      ```cmd
      set MINIMAX_API_KEY=你的API_KEY
      ```
      **macOS/Linux**:
      ```bash
      export MINIMAX_API_KEY=你的API_KEY
      ```
      请确保在运行脚本的同一个终端会话中设置环境变量。

3. **运行工作流**:
   ```bash
   python main_workflow.py --keywords "你的关键词"
   ```
   例如：
   ```bash
   python main_workflow.py --keywords "暴雨森林"
   ```

   脚本将依次执行提示生成、图像生成和视频生成，并将结果保存到当前目录。

## 注意事项

- 确保你的 MiniMax API Key 有足够的权限和余额来执行文本、图像和视频生成任务。
- 生成的图像和视频文件将保存在脚本运行的同一目录下。
