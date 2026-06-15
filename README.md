# 🐉 奶龙 - 桌面宠物

一只可爱的奶龙桌面宠物，会在你的屏幕上跑来跑去、跳舞、招手、发呆。

## ✨ 功能

- 🎬 **10种动画状态** - 待机、左跑、右跑、跳舞、跳跃、招手、等待、失败、审查、下落
- 🖱️ **丰富交互** - 拖拽移动、双击抚摸（爱心粒子）、物理下落
- 🎵 **循环背景音乐** - 自动播放，右键菜单可开关
- 📋 **右键菜单** - 切换跳舞/散步/跳跳/招手/等待 5 种动画，开关音效
- 🪂 **物理引擎** - 拖到空中松手会自由落体，碰到边缘反弹
- ❤️ **抚摸计数** - 记录你摸了奶龙多少次
- 🖼️ **spritesheet 渲染管线** - 基于 Codex 精灵表规格，可变帧率，PIL 全像素合成

## 🚀 快速开始

### 直接运行（需要 Python 环境）

```bash
pip install -r requirements.txt
python nailong_desktop_pet.py
```

### 打包为独立 exe（不需要 Python 环境）

```bash
build.bat
```

打包后的 exe 位于 `dist/NailongPet.exe`，包含所有依赖，可直接分发运行。

## 📁 项目结构

```
desktop-pet-nailong/
├── nailong_desktop_pet.py         # 标准版主程序
├── nailong_desktop_pet_special.py # 特别版（for 47cat）
├── spritesheet.webp               # 精灵表素材（192×208 每帧，8列×9行）
├── Banda AK-47 - 我是奶龙（星光闪闪）.flac  # 背景音乐
├── build.bat                      # 一键打包脚本
├── requirements.txt               # Python 依赖
├── README.md                      # 项目文档
└── gifs/                          # 原始 GIF 素材（保留，供参考）
```

## 🎮 操作说明

| 操作 | 效果 |
|------|------|
| 左键拖拽 | 移动奶龙位置 |
| 空中松手 | 奶龙自由落体 |
| 双击 | 抚摸奶龙，飘出爱心 |
| 右键 | 打开菜单，切换动画/开关音乐 |
| Esc | 退出 |

## 🔧 依赖

- Python >= 3.8
- Pillow >= 9.0.0
- pygame >= 2.0.0
- pyinstaller >= 5.0（打包用）

## 📋 更新日志

### v3.0

- **BGM 升级**：《Banda AK-47 - 我是奶龙（星光闪闪）》FLAC 高品质音源，音量 30%
- **修复双击计数不更新**：三层 bug 叠加排查 —— ① `overrideredirect` 窗口下 tkinter 可能不投递 `<Double-Button-1>`，采用手动 `time.time()` 400ms 间隔检测 + tkinter 原生双击双保险互补，`_last_click_time` 归零互斥防重复；② `_pet_menu_idx` 在计数器菜单项 `add_command` 之前取值导致索引偏移到分隔符，`entryconfigure` 静默失败；③ `try/except: pass` 吞掉异常使问题完全不可见。修复后双击爱心粒子 + 菜单计数同步更新。
- 参考同仓库月薪喵项目确认事件处理模式

### v2.1（特别版 for 47cat）

- 自定义互动菜单文本、双击计数修复、FLAC BGM

### v2.0

- 修复 chroma-key 绿边问题：增加 alpha 通道二值化处理，消除 LANCZOS 缩放产生的半透明边缘

### v1.0

- 基于 Codex 奶龙 spritesheet 的初版桌面宠物
- 可变帧率渲染管线、9 状态动画、物理系统、粒子效果、BGM 播放

## 📄 License

MIT
