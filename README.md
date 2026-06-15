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
- **修复双击计数不更新** — 三层 bug 叠加排查与修复（详见下方）

### v2.1（特别版 for 47cat）

- 自定义互动菜单文本、双击计数修复、FLAC BGM

### v2.0

- 修复 chroma-key 绿边问题：增加 alpha 通道二值化处理，消除 LANCZOS 缩放产生的半透明边缘

### v1.0

- 基于 Codex 奶龙 spritesheet 的初版桌面宠物
- 可变帧率渲染管线、9 状态动画、物理系统、粒子效果、BGM 播放

---

## 🐛 双击计数 Debug 专题

> v3.0 修复了一个三层 bug 叠加导致的「双击后计数器数字不变」问题，以下是排查过程和结论。

### 症状

双击宠物后，爱心粒子正常飘出，但右键菜单中「被摸: 0 次」始终不变化。

### 根因：三层 bug 叠加

| 层 | 问题 | 影响 |
|----|------|------|
| **事件层** | Windows 上 `overrideredirect(True)` 窗口下，tkinter 可能不投递 `<Double-Button-1>` 事件。原因是双击序列中 `<Double-Button-1>` 会取代第二个 `<ButtonPress-1>`，导致原始的手动 `time.time()` 间隔检测永远收不到第二次 press | 双击回调从未执行 |
| **菜单层** | `self._pet_menu_idx = self.menu.index("end")` 在计数器菜单项 `add_command` **之前**取值，导致索引指向分隔符（而非计数器标签）。`entryconfigure(分隔符, label=...)` 静默无效果 | 菜单 label 未更新 |
| **异常层** | `try: ... except: pass` 吞掉了所有异常 | 没有错误提示，问题完全不可见 |

### 修复方案

1. **双击双保险**：保留 `<Double-Button-1>` 绑定 + 新增 `_on_mouse_down` 内手动 `time.time()` 检测（400ms 阈值），两个入口调用同一个 `_do_pet()` 方法，通过 `_last_click_time` 归零互斥防重复触发
2. **菜单索引修正**：`_pet_menu_idx` 移到 `add_command` 之后取值，确保精确指向计数器标签
3. **参考对照**：与同仓库 `desktop-pet-yuexinmiao`（月薪喵）项目对比确认事件处理模式

### 关键代码变更

```python
# _on_mouse_down: 手动双击检测（作为 <Double-Button-1> 的后备）
def _on_mouse_down(self, event):
    now = time.time()
    if now - self._last_click_time < 0.4:   # 400ms 内两次 press
        self._last_click_time = 0
        self.dragging = False
        self._do_pet()
        return
    self._last_click_time = now
    self.dragging = True
    # ...

# _on_double_click: tkinter 原生双击，与手动检测互斥
def _on_double_click(self, event):
    if self._last_click_time == 0:  # 已被手动检测处理
        return
    self._last_click_time = 0
    self._do_pet()

# _build_menu: 索引必须先 add 后取值
self.menu.add_command(label="  被摸: 0 次", state="disabled")
self._pet_menu_idx = self.menu.index("end")  # 移到这里
```

## 📄 License

MIT
