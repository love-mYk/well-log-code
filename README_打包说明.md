# WellCorrelator v5.3 — Windows 打包指南

## 📦 文件清单

```
打包文件夹/
├── V5.3.py                  # 源代码
├── wellcorrelator.ico       # 应用图标
├── build.bat                # 一键打包脚本 ← 双击运行这个
└── README_打包说明.md        # 本文件
```

## 🚀 使用步骤

### 前提条件
- 一台 **Windows 电脑**（Win10/Win11）
- 安装了 **Python 3.10+**（[下载地址](https://www.python.org/downloads/)）
  - ⚠️ 安装时**必须勾选** `Add Python to PATH`

### 打包流程

1. 把以上 **4 个文件**放到同一个文件夹里
2. **双击 `build.bat`**，等待打包完成（首次约 3-5 分钟）
3. 完成后会生成 `dist\WellCorrelator_v5.3\` 文件夹
4. 把整个 `dist\WellCorrelator_v5.3` 文件夹压缩成 **zip**
5. 发给别人，解压后双击 `WellCorrelator_v5.3.exe` 即可运行

## ⚡ 如果想打包成单个 .exe 文件

编辑 `build.bat`，把 `--onedir` 改成 `--onefile`：

```diff
-     --onedir ^
+     --onefile ^
```

**注意**：单文件模式启动会慢几秒（需解压临时文件），但只有一个 exe 更方便分发。

## ❓ 常见问题

| 问题 | 解决方法 |
|------|----------|
| 双击 build.bat 闪退 | 右键 → 以管理员身份运行 |
| 提示找不到 Python | 安装 Python 时没勾选 PATH，重新安装 |
| 杀毒软件报毒 | 添加信任/白名单，PyInstaller 生成的 exe 常被误报 |
| 打包后 exe 启动报错 | 确保 build.bat 里所有依赖都安装成功 |
