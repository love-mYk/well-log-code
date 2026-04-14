# 🪨 WellCorrelator

**双井测井曲线地层对比工具** — PyQt6 + PyQtGraph

## ✨ 功能特性

- **LAS 数据导入** — 直接加载标准 LAS 测井数据文件
- **多曲线显示** — 支持 GR / RT / DEN / CNL 等常用测井曲线
- **交互式分层** — 可视化添加/编辑/删除 Top 层位线，拖拽调整深度
- **Zone 颜色管理** — 相同 Zone 在两口井中颜色自动一致
- **曲线变面积填充** — 支持左/右参考线充填，直观展示岩性变化
- **DTW 相似度分析** — 基于动态时间规整的曲线形态对比
- **数据保存/加载** — JSON 格式保存分层与对比结果

## 🖥️ 界面预览

> 双井并排显示，每井支持多道曲线，分层线贯穿所有道

## 📦 依赖

```
Python 3.10+
PyQt6
pyqtgraph
numpy
pandas
lasio (可选)
```

## 🚀 快速开始

```bash
# 安装依赖
pip install PyQt6 pyqtgraph numpy pandas lasio

# 运行
python V5.3.py
```

## 🏗️ 打包为 Windows exe

1. 将项目文件拷贝到 Windows 电脑
2. 双击 `build.bat` 等待打包完成
3. 在 `dist/` 目录获取可执行文件

详细说明见 `README_打包说明.md`

## 📁 文件结构

```
WellCorrelator/
├── V5.3.py                    # 主程序
├── build.bat                  # Windows 打包脚本
├── wellcorrelator.ico         # 应用图标
├── README.md                  # 本文件
└── README_打包说明.md          # 打包详细说明
```

## 📄 License

MIT
