# WaterQuality_Analyzer

**基于大模型（Ollama + Qwen2.5）的水质监测与智能分析系统**

一个使用本地大模型实现水质数据智能分析、趋势预测和报告生成的智慧水利应用。

---

## ✨ 一键运行（推荐）

双击项目根目录下的 `run.bat` 即可自动启动：

1. 启动 Ollama（qwen2.5:14b）
2. 启动 Streamlit 前端界面

---

## 📋 项目结构

```bash
WaterQuality_Analyzer/
├── data/                          # 原始分年份水质数据
├── preprocessing/                 # 数据清洗与合并
│   ├── water_quality_data_merger.py
│   └── water_quality_preprocessor.py
├── analysis/                      # 大模型分析核心
│   └── water_quality_ollama_analyzer.py
├── streamlit_app/                 # Streamlit 可视化界面
│   └── water_quality_streamlit.py
├── reports/                       # 自动生成的分析报告
├── docs/                          # 文档与进度
├── CLAUDE.md                      # AI 辅助开发规范
├── requirements.txt
├── run.bat
└── README.md