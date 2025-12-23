# 🌍 Landmark Recognition / 地标识别系统

[![Streamlit](https://img.shields.io/badge/Streamlit-App-blue)](https://streamlit.io/)  
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)  
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black)](https://github.com/Jerrywjr/landMarkFinder_deploy)

**Live Demo / 在线演示:** [Streamlit App](https://202511iselandmarkfinder-rm6fwkkitlryewpyxztspk.streamlit.app/)  
**Source Code / 源代码:** [GitHub Repository](https://github.com/Jerrywjr/landMarkFinder_deploy)

---

## Table of Contents / 目录

1. [Project Overview / 项目概述](#project-overview--项目概述)  
2. [Features Implemented / 已实现功能](#features-implemented--已实现功能)  
3. [Implementation Details / 技术实现细节](#implementation-details--技术实现细节)  
4. [Development Process / 开发过程](#development-process--开发过程)  
5. [Problems & Solutions / 遇到的问题及解决方案](#problems--solutions--遇到的问题及解决方案)  
6. [Helpful Hints for Others / 开发建议](#helpful-hints-for-others--开发建议)  
7. [Future Improvements / 未来改进方向](#future-improvements--未来改进方向)  

---

## 1. Project Overview / 项目概述

**English:**  
Landmark Recognition is a web-based application that allows users to upload photos of landmarks and receive automatic identification along with a short introduction. The system is designed to work under free model constraints and ensure robustness even when multi-modal models are temporarily unavailable.

**中文:**  
地标识别系统是一个网页应用，用户可以上传地标照片，并获得自动识别结果以及简短的介绍。系统在免费模型条件下运行，即使多模态模型暂时不可用，也保证系统的稳定性。

---

## 2. Features Implemented / 已实现功能

| Feature / 功能 | Description / 描述 |
|----------------|------------------|
| **Image Upload & Preview / 图片上传与预览** | Users can upload JPG/PNG images. Preview image is displayed with a fixed maximum height (260px) to avoid page overflow. <br>用户可以上传 JPG/PNG 图片，预览图固定最大高度，避免页面过长。 |
| **Multi-language Support / 多语言支持** | Supports English and Chinese. All UI elements update according to selected language. <br>支持中英文切换，所有按钮、标签、占位符和提示信息随语言变化。 |
| **Landmark Recognition / 地标识别** | Uses Qwen 2.5 VL free model for image-based recognition. <br>使用 Qwen 2.5 VL 免费模型进行图像地标识别。 |
| **Fallback Text Mode / 文字输入备用模式** | When the VL model fails, users can manually input the landmark name; system generates introduction using Xiaomi MiMo-V2-Flash (text-only). <br>当 VL 模型失败时，用户可手动输入地标名称，由 Xiaomi MiMo-V2-Flash 文本模型生成介绍。 |
| **Dual Column Layout / 左右布局** | Left: image upload, preview, language selection; Right: result display with TTS. <br>左侧为上传、预览和语言选择，右侧显示结果并支持语音播报。 |
| **Text-to-Speech / 语音播报** | Automatically reads out the recognition result in the selected language. <br>自动用选定语言朗读识别结果。 |
| **Robust Error Handling / 错误处理** | Handles API failures gracefully with user-friendly messages and fallback mechanisms. <br>优雅处理 API 异常，并提供备用机制和用户提示。 |

---

## 3. Implementation Details / 技术实现细节

**English:**  
- **Framework:** Streamlit  
- **Models Used:**  
  - `qwen/qwen-2.5-vl-7b-instruct:free` — Vision-Language model for image recognition  
  - `xiaomi/mimo-v2-flash:free` — Text-only model for fallback introduction  
- **Deployment:** Streamlit Cloud  
- **Image Handling:** Uploaded images converted to Base64 for API calls; preview height fixed to 260px  
- **Language Support:** Dictionary-based UI text selection for English and Chinese  
- **Session State:** `st.session_state` to maintain VL failure flag and results  
- **TTS Implementation:** Browser SpeechSynthesis for language-aware playback  

**中文:**  
- **框架:** Streamlit  
- **使用模型:**  
  - `qwen/qwen-2.5-vl-7b-instruct:free` — 图像识别多模态模型  
  - `xiaomi/mimo-v2-flash:free` — 文字备用介绍模型  
- **部署:** Streamlit Cloud  
- **图片处理:** 上传图片转换为 Base64 调用 API，预览高度固定 260px  
- **多语言支持:** 使用字典统一管理 UI 文本  
- **状态管理:** 使用 `st.session_state` 保存 VL 失败标志和识别结果  
- **语音播报:** 浏览器内置 SpeechSynthesis 支持中英文  

---

## 4. Development Process / 开发过程

**English:**  
1. Built initial prototype with image upload and VL model recognition.  
2. Encountered frequent VL model 502/503 errors.  
3. Implemented dual-model architecture with fallback text model.  
4. Refactored Streamlit app using session_state for state management.  
5. Redesigned UI into left-right columns with fixed-size image preview.  
6. Added multi-language support and text-to-speech.  

**中文:**  
1. 初步搭建原型，实现图片上传与 VL 模型识别。  
2. 遇到免费 VL 模型频繁 502/503 错误。  
3. 引入双模型架构，增加文字输入备用模型。  
4. 使用 session_state 管理状态，解决 Streamlit rerun 问题。  
5. 左右布局重新设计，图片预览固定高度，防止页面滚动。  
6. 增加中英文支持及语音播报功能。  

---

## 5. Problems & Solutions / 遇到的问题及解决方案

| Problem / 问题 | Solution / 解决方案 |
|----------------|------------------|
| VL free model frequently returns 502/503 | Fallback text-only model (MiMo-V2-Flash) for stable introduction <br>免费 VL 模型经常 502/503 → 使用文本备用模型（MiMo-V2-Flash）生成介绍 |
| Streamlit rerun prevents text input fallback | Used `st.session_state` to track failure and preserve results <br>Streamlit rerun 导致文字输入无法触发 → 用 session_state 保存状态 |
| Large images stretch page and cause scrolling | Fixed image preview height 260px using CSS <br>大图片撑大页面 → 限制预览高度 260px |
| Multi-language buttons/messages hard-coded | Created a dictionary `UI` mapping all text for English/Chinese <br>按钮/文本硬编码 → 用字典统一管理中英文文本 |
| Need voice output | TTS with browser SpeechSynthesis, language-aware <br>需要语音播报 → 浏览器 TTS 支持中英文 |

---

## 6. Helpful Hints for Others / 开发建议

**English:**  
- Free VL models are often unstable; always implement a text-only fallback.  
- Use `st.session_state` to preserve state across reruns in Streamlit.  
- Fix image preview height to avoid page overflow.  
- Use dictionary-based UI text management for multi-language support.  
- Browser-based TTS is simple and cross-platform.  

**中文:**  
- 免费 VL 模型经常不稳定，建议总是实现文字备用机制。  
- 使用 `st.session_state` 保持状态，解决 Streamlit rerun 问题。  
- 图片预览固定高度，防止页面撑开。  
- 使用字典管理 UI 文本，方便多语言切换。  
- 浏览器内置 TTS 简单跨平台可用。  

---

## 7. Future Improvements / 未来改进方向

**English:**  
- Result card layout (Name / Location / Intro separated)  
- History panel for past recognized landmarks  
- Download results as TXT/Markdown  
- Mobile layout optimization and dark mode  

**中文:**  
- 结果卡片化（名称 / 位置 / 介绍 分块显示）  
- 增加历史记录面板  
- 支持导出识别结果为 TXT/Markdown  
- 移动端布局优化及暗色模式  

---

> Developed by **Jerry Wang / 王杰瑞**
