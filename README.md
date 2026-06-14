# 🐉 奶龙 - 桌面宠物

一只可爱的奶龙桌面宠物，会在你的屏幕上跑来跑去、跳舞、招手、发呆。

## ✨ 功能

- 🎬 **9种动画状态** - 待机、左右跑、跳舞、跳跃、招手、等待、失败、审查、下落
- 🖱️ **丰富交互** - 拖拽移动、双击抚摸（爱心粒子）、物理下落
- 🎵 **循环背景音乐** - 自动播放，右键菜单可开关
- 📋 **右键菜单** - 切换任意动画状态
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
├── nailong_desktop_pet.py   # 主程序
├── spritesheet.webp          # 精灵表素材（192×208 每帧，8列×9行）
├── music.mp3                 # 背景音乐
├── build.bat                 # 一键打包脚本
├── NailongPet.spec           # PyInstaller 配置
├── requirements.txt          # Python 依赖
└── gifs/                     # 原始 GIF 素材（保留，供参考）
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

### v2.0

- 修复 chroma-key 绿边问题：增加 alpha 通道二值化处理，消除 LANCZOS 缩放产生的半透明边缘

### v1.0

- 基于 Codex 奶龙 spritesheet 的初版桌面宠物
- 可变帧率渲染管线、9 状态动画、物理系统、粒子效果、BGM 播放

## 📄 License

MIT
