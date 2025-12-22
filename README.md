# 🌍 Landmark Finder (ISE_LandMarkFinder)

这是一个使用 **Streamlit** 开发的地标识别网站，用户可以上传建筑/景点照片，AI 自动识别并给出简短描述。

👉 **在线演示地址：**  
https://202511iselandmarkfinder‑rm6fwkkitlryewpyxztspk.streamlit.app/ (已上线)

---

## 🧠 项目简介

这个项目使用 OpenRouter 提供的多模态大模型（如 `qwen/qwen‑2.5‑vl‑7b‑instruct:free`）来识别用户上传的图片内容，进而判断出该图片中的地标建筑，并返回地点及简短介绍。  
适合用于快速搭建 AI 辅助的图片识别演示或旅游相关网站。

---

## 🚀 主要功能

✅ 支持上传图片识别地标  
✅ 返回建筑/景点名字  
✅ 返回地点（城市/国家）  
✅ 简短 3‑4 句介绍  
✅ 自动部署到 Streamlit Cloud，无需后端服务器

---

## 📦 技术栈

| 技术 | 用途 |
|------|------|
| 🧪 Python | 核心语言 |
| 🖥️ Streamlit | Web 展示界面 |
| 🧠 OpenRouter API | 调用大模型识别图像 |
| 📡 Streamlit Cloud | 部署 & 托管 |

---

## 💻 本地运行指南

### 1️⃣ 克隆仓库

```bash
git clone https://github.com/<你的用户名>/<你的仓库名>.git
cd <你的仓库名>
