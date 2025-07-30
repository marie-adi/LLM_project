
<img width="1584" height="396" alt="fondo README" src="https://github.com/user-attachments/assets/4cd9f1d1-f715-4452-8103-269f64cf03d8" />

<h1 align="center">LLM project</h1>

<p align="center">
  Agents for content generators • Dockerized • FastAPI + Gradio + Chroma DB
</p>

---

## 🧭 Table of Contents

- [📌 Project Overview](#-project-overview)
- [🎯 Target Audience](#-target-audience)
- [⚙️ Features & Limitations](#️-features--limitations)
- [🚀 Future Improvements](#-future-improvements)
- [🛠️ Tools & Technologies](#-tools--technologies)
- [🧪 Model Architecture](#-model-architecture)
- [📁 Project Structure](#-project-structure)
- [✍ Deployment Instructions](#-deployment-instructions)
- [👩💻 Contributors](#-contributors)

---

## 📌 Project Overview

<p align="justify">
  
**FinancIA** combines advanced language models with a simple interface, allowing users, journalists, and content creators to create clear, accurate, and up-to-date content on the economy, investments, cryptocurrencies, and more.
This solution seeks to streamline the creation of financial content, maintaining accessible language without losing rigor, and adapting to different formats such as blogs, social media, and newsletters.

## The platform supports:

- ### 📝 Dynamic Content Generation  
  Generate customized textual content for multiple social media platforms including **Instagram**, **Twitter**, and **LinkedIn**, all from a simple prompt.

- ### 💼 Advanced Financial Agent  
  An intelligent agent specialized in **finance**, offering expert-level analysis and reasoning to assist with complex financial topics.

- ### 📚 Retrieval-Augmented Generation (RAG)  
  Answer complex questions using information retrieved from a specialized **knowledge base**, including support for **PDF documents**, ensuring context-rich and well-grounded responses.

- ### 📈 Real-Time Financial Data Analysis  
  Seamless integration with **Yahoo Finance** to access and analyze real-time market data, enabling the creation of content that reflects the **latest financial trends**.

- ### 🎨 AI-Powered Image Generation  
  Transform textual descriptions into **unique AI-generated images**, providing impactful **visual support** for your content.

- ### 🎯 Audience Segmentation  
  Tailor content to specific **demographics** — including **age group**, **language**, and **geographical region** — to maximize **relevance** and **engagement**.

---

## 🎯 Target Audience

- **Content creators**
- **Community manager**
- **Social media manager**

---

## ⚙️ Features & Limitations

### ✅ Features
<br>

**🧠 Multi-Model Architecture**

  This project integrates several AI models and services, each optimized for specific tasks, to deliver intelligent, personalized, and dynamic content generation.
  
  **🤖 Core Models**
  
  - **🦅 Horus**
      A model optimized for fast content generation, designed to quickly produce high-quality textual outputs.
  
  - **💼 Isis**
      An advanced reasoning agent specialized in finance, capable of understanding complex economic data and producing insightful financial content.
<br>

**🔍 Retrieval-Augmented Generation (RAG)**

  - **📚 RAG with ChromaDB**
    Implements a retrieval-augmented generation pipeline using ChromaDB (a vector database).
    This allows the system to:

    - Search relevant documents in real time

    - Enrich model responses with specific and updated information
<br>

**👥 Advanced Audience Segmentation**

  - **🎯 Personalized Content Generation**
    Automatically adapts output based on:

    - Age group

    - Target platform (Instagram, Twitter, LinkedIn)

    - Region or language

✅ Ensures every message is audience-aware, platform-specific, and contextually relevant.

<br>

**🖼️ Integrated Image Generator**

  - **🎨 Text-to-Image Capability**
    
    Includes a tool to generate images from text descriptions, likely powered by Stability AI or similar services, supporting the visual needs of generated content.
<br>

**🌐 External Data Integrations**

  - **📈 Yahoo Finance**
    
    Real-time financial data retrieval via Yahoo Finance API to support economic analysis and market updates.

  - **📄 PDF Processing**
    
    Ability to extract text and knowledge from PDF documents, enhancing the system's internal data sources.
<br>

**⚙️ Modular & Scalable API**

  - **🧩 REST API Design**
    The backend is organized into modular routes:

    - `/content`

    - `/agent`

    - `/query`

    - `/image`
      
      This architecture allows for easy maintenance and scalable feature integration.
<br>

**⚡ Fast Inference Engine**

  - **🚀 Groq API Integration**
    
    Supports ultra-fast language model inference using the Groq API, improving model response times and overall performance..
<br>

### ⚠️ Limitations

- The technology used for the frontend (Gradio) limits us in its design.
- The time to develop the project was short

---

## 🚀 Future Improvements

- Expand the database with more pdfs
- Add **more languages** to our app
- improvements in the frontend

---

## 🛠️ Tools & Technologies

### ⚙️ Backend

![FastAPI](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)
![Uvicorn](https://img.shields.io/badge/-Uvicorn-6E4C1E)
![LangChain](https://img.shields.io/badge/-LangChain-92C63D)
![Pydantic](https://img.shields.io/badge/-Pydantic-09A3D5)
![Loguru](https://img.shields.io/badge/-Loguru-FFFFFF)

### 🧠 Models

![SentenceTransformers](https://img.shields.io/badge/-SentenceTransformers-6A1B9A)
![Groq](https://img.shields.io/badge/-Groq-09A3D5)
![langchainOllama](https://img.shields.io/badge/-langchainOllama-646CFF)

### 🌐 Frontend

![Gradio](https://img.shields.io/badge/-Gradio-61DAFB)
![Pillow (PIL)](https://img.shields.io/badge/-Pillow-06B6D4)


### 🧱 Database & Infrastructure

![ChromaDB](https://img.shields.io/badge/-ChromaDB-3ECF8E)
![RAG](https://img.shields.io/badge/-RAG-6A1B9A)
![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white)
![Yfinance](https://img.shields.io/badge/-Yfinance-FFFFFF)
![Pypdf](https://img.shields.io/badge/-Pypdf-0078D4)

---

## 🧪 Model Architecture



<p align="center">
  <img src="" alt="Diagrama de Arquitectura del Sistema" width="700"/>
</p>

## 📁 Project Structure
📦 Proyecto  
├── 📝 README.md  
├── 📁 client   
│   ├── 🐍 \_\_init\_\_.py  
│   └── 🚀 app.py  
├── 📄 requirements.txt  
├── 📁 server  
│   ├── 📁 agents  
│   │   ├── 🐍 \_\_init\_\_.py  
│   │   └── 🤖 finance_agent.py  
│   ├── 📁 database  
│   │   ├── 📁 chroma_data/  
│   │   ├── 🗃️ chroma_db.py  
│   │   ├── 📁 data_pdfs/  
│   │   ├── 🧹 delete_from_db.py  
│   │   └── 🔍 inspect_db.py  
│   ├── 🚀 main.py  
│   ├── 📁 prompts  
│   │   ├── 📁 age_groups/  
│   │   ├── 📄 base.txt  
│   │   ├── 📁 dialects/  
│   │   ├── 📁 languages/  
│   │   └── 📁 platforms/  
│   ├── 📁 routes  
│   │   ├── 🧠 agent.py  
│   │   ├── ✍️ content.py  
│   │   ├── 🖼️ image.py  
│   │   ├── ❓ query.py  
│   │   └── 📈 yahoo.py  
│   ├── 📁 services  
│   │   ├── 🤖 lm_engine.py  
│   │   ├── 🧩 prompt_builder.py  
│   │   └── 🔍 query_engine.py  
│   ├── 📁 tools  
│   │   ├── 🖼️ generate_image.py  
│   │   ├── ✍️ generate_post.py  
│   │   ├── 📄 pdf_fetcher.py  
│   │   └── 📈 yahoo_data.py  
│   └── 📁 utils  
│       └── 📏 query_depth.py  

---

## ✍ Deployment Instructions

📋 Prerequisites

Before you begin, make sure you have:

    Python 3.10

    pip

    Git (optional but recommended)

    Ollama if using local models (e.g., LLaMA2, Mistral)

    (Optional) Virtualenv for managing virtual environments

🧪 1. Clone the repository

    git clone https://github.com/your-username/your-repo.git
    cd your-repo

🐍 2. Create and activate a virtual environment (optional but recommended)

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

📦 3. Install dependencies

    pip install --upgrade pip
    pip install -r requirements.txt

🧠 4. Download required models (SpaCy, Ollama, etc.)
For SpaCy:

    python -m spacy download en_core_web_sm

If using Ollama models:

Make sure you have Ollama installed and running.

Example to load LLaMA 3:

    ollama run llama3

🔐 5. Configure environment variables

Create a .env file in the project root and add your variables (e.g.):

    # Groq API Key for LLM access
    GROQ_API_KEY="YOUR_GROQ_API_KEY"
    
    # Stability AI API Key for image generation
    STABILITY_API_KEY="YOUR_STABILITY_API_KEY"

▶️ 6. Start the backend server

From the root directory, run:

    uvicorn server.main:app --reload

This will launch the FastAPI server at http://localhost:8000.

💻 7. Run the client (if applicable)

If you're using a Gradio or custom client, run:

    python client/app.py

📂 Expected folder structure

You can include a visual representation of your folder structure (already done with icons earlier 👍).
✅ Verify it's working

Open your browser and visit:

    Interactive API docs: http://localhost:8000/docs

    Gradio client (if used): http://localhost:7860/



---
## 👩‍💻 Contributors
We are AI students with a heart and passion for building better solutions for real problems.
Feel free to explore, fork, or connect with us for ideas, feedback, or collaborations.


| Name                  | GitHub                                                                                                                   | LinkedIn                                                                                                                                             |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Yael Parra**         | [![GitHub](https://img.shields.io/badge/GitHub-c4302b?logo=github&logoColor=white)](https://github.com/Yael-Parra)      | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/yael-parra/)                |
| **Polina Terekhova Pavlova**    | [![GitHub](https://img.shields.io/badge/GitHub-c4302b?logo=github&logoColor=white)](https://github.com/fintihlupik)            | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/polina-terekhova-pavlova/)               |
| **Mariela Adimari**  | [![GitHub](https://img.shields.io/badge/GitHub-c4302b?logo=github&logoColor=white)](https://github.com/marie-adi)     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mariela-adimari/)             |
| **Abigail Masapanta Romero**        | [![GitHub](https://img.shields.io/badge/GitHub-c4302b?logo=github&logoColor=white)](https://github.com/abbyenredes)       | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/abigail-masapanta-romero/)                   |
