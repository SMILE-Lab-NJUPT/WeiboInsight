<p align="center">
  <h1 align="center"> WeiboInsight: Advanced Weibo Data Scraper & Text Analyzer </h1>
</p>

<p align="center">
  <img src="images/icon.png" width="200" alt="微博爬虫 icon">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Scrapy-2.x-orange.svg?logo=scrapy&logoColor=white" alt="Scrapy">
  <img src="https://img.shields.io/badge/Playwright-✓-brightgreen.svg?logo=playwright&logoColor=white" alt="Playwright Ready">
  <img src="https://img.shields.io/badge/MongoDB-✓-green.svg?logo=mongodb&logoColor=white" alt="MongoDB">
  <img src="https://img.shields.io/badge/NLP-Jieba_Gensim_Scikit--learn-purple.svg" alt="NLP Tools">
  </p>

<p align="center">
  <strong><em>by B23042424 Haokuan YUAN</em> from NJUPT</strong>
</p>

<p align="center">
  <a href="#✨-features">Features</a> •
  <a href="#🛠️-tech-stack">Tech Stack</a> •
  <a href="#🎯-core-functionality">Core Functionality</a> •
  <a href="#📋-environment-requirements">Requirements</a> •
  <a href="#🚀-getting-started">Getting Started</a> •
  <a href="#🏃‍♀️-how-to-run">How to Run</a> •
  <a href="#💡-important-considerations">Important Considerations</a> •
  <a href="#📂-project-structure">Project Structure</a> •
  <a href="#🤝-contributing">Contributing</a> •
  <a href="#📜-license">License</a>
</p>

---

**WeiboInsight** is a comprehensive solution for collecting and analyzing data from Weibo (新浪微博). It leverages the power of Scrapy for efficient, asynchronous web scraping and integrates Playwright to handle dynamically loaded content. Once data is gathered, a suite of NLP tools including Jieba, Gensim, and Scikit-learn are employed for insightful text analysis, covering segmentation, topic modeling (LDA), and text clustering (TF-IDF + K-Means). Data is persistently stored in MongoDB.

## ✨ Features

* **🚀 High-Performance Asynchronous Scraping:** Built with Scrapy for speed and efficiency.
* **🤖 Dynamic Content Handling:** Seamlessly integrates Playwright (via `scrapy-playwright`) to scrape JavaScript-heavy pages.
* **🔍 Targeted Data Collection:** Focus on specific topics or keywords.
* **🧹 Data Preprocessing:** Includes essential data cleaning steps.
* **🌏 Chinese Text Segmentation:** Utilizes Jieba for accurate word tokenization.
* **📊 Advanced Text Analytics:**
    * **Topic Modeling:** Employs Gensim's Latent Dirichlet Allocation (LDA) to discover hidden thematic structures.
    * **Text Clustering:** Uses Scikit-learn's TF-IDF and K-Means to group similar Weibo posts.
* **💾 Persistent Storage:** Stores scraped data reliably in MongoDB.
* **🛡️ Basic Anti-Anti-Spider Measures:**
    * User-Agent Rotation.
    * Proxy Rotation (requires user-supplied proxies).
    * Configurable download delays and auto-throttling.
* **📝 Customizable Stopword List:** Enhance analysis accuracy by filtering out common, irrelevant words.

## 🛠️ Tech Stack

| Category          | Technology / Library                                                                                                   |
| :---------------- | :--------------------------------------------------------------------------------------------------------------------- |
| **Web Scraping** | <img src="https://img.shields.io/badge/Scrapy-Framework-orange?logo=scrapy&logoColor=white" alt="Scrapy"> <img src="https://img.shields.io/badge/Playwright-Dynamic_Content-green?logo=playwright&logoColor=white" alt="Playwright"> |
| **NLP & Analysis**| <img src="https://img.shields.io/badge/Jieba-Chinese_Segmentation-blue" alt="Jieba"> <img src="https://img.shields.io/badge/Gensim-Topic_Modeling_(LDA)-yellow" alt="Gensim"> <img src="https://img.shields.io/badge/Scikit--learn-Clustering_&_TFIDF-purple?logo=scikitlearn&logoColor=white" alt="Scikit-learn"> <img src="https://img.shields.io/badge/Pandas-Data_Manipulation-blue?logo=pandas&logoColor=white" alt="Pandas"> <img src="https://img.shields.io/badge/NumPy-Numerical_Computing-blue?logo=numpy&logoColor=white" alt="NumPy"> |
| **Database** | <img src="https://img.shields.io/badge/MongoDB-NoSQL_Database-darkgreen?logo=mongodb&logoColor=white" alt="MongoDB">         |
| **Core Language** | <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white" alt="Python">                       |
| **Environment** | <img src="https://img.shields.io/badge/pip-Package_Manager-informational?logo=pypi&logoColor=white" alt="pip"> <img src="https://img.shields.io/badge/venv-Virtual_Environment-gray" alt="venv"> |

*(For optimal display, ensure you are viewing this on a platform that renders HTML images, or replace `img` tags with actual images/icons if using a Markdown editor that supports local image paths or different embedding methods.)*

## 🎯 Core Functionality

1.  **Define Target Keywords:** Specify topics or hashtags of interest.
2.  **Crawl Weibo:** The Scrapy spider navigates Weibo, searches for posts matching the keywords, and handles pagination and dynamic content loading with Playwright.
3.  **Extract Data:** Key information such as post content, user details (optional, if selectors are set up), post time, etc., is extracted.
4.  **Store in MongoDB:** Raw and processed data is saved to a MongoDB database.
5.  **Text Preprocessing:** Clean text, remove noise, and perform Chinese word segmentation using Jieba.
6.  **Feature Extraction:** Convert text data into numerical representations using TF-IDF.
7.  **Topic Modeling (LDA):** Identify underlying topics within the collected posts using Gensim.
8.  **Text Clustering (K-Means):** Group similar posts based on their content.
9.  **Output Results:** Display analysis summaries, top terms per topic/cluster, etc.

## 📋 Environment Requirements

* **Python:** Version 3.8 or higher.
* **MongoDB:** A running instance of MongoDB.
* **Playwright Browsers:** Browser binaries for Playwright. These are typically downloaded automatically upon first use or can be installed manually:
    ```bash
    playwright install
    ```

## 🚀 Getting Started

Follow these steps to get the project up and running on your local machine.

### 1. Clone the Repository

```bash
git clone [YOUR_PROJECT_GIT_REPOSITORY_ADDRESS]
cd [PROJECT_DIRECTORY_NAME]
```
### 2. Set Up a Virtual Environment (Recommended)
- Linux/macOS:
```bash
    python3 -m venv venv
source venv/bin/activate
```

- Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
- Ensure your virtual environment is activated, then run:
```bash
pip install -r requirements.txt
```
### 4. Configure MongoDB
- Make sure your MongoDB service is operational.
- Update the MongoDB connection details in **spider/scrapy_project/weibo_collector/settings.py** if they differ from the defaults:
```Python

# spider/scrapy_project/weibo_collector/settings.py
MONGO_URI = 'mongodb://localhost:27017'
MONGO_DATABASE = 'weibo_data'
```
### 5. Configure Proxies (⚠️ Highly Recommended)
Weibo employs stringent anti-scraping measures. Using high-quality proxies is crucial for stable and large-scale data collection.

- Modify PROXY_LIST in **spider/scrapy_project/weibo_collector/settings.py**:
```Python

# spider/scrapy_project/weibo_collector/settings.py

PROXY_LIST = [
    'http://user1:pass1@proxy_host1:port',
    'http://user2:pass2@proxy_host2:port',
    # ... add your high-quality proxies here
]
```
- If you don't have proxies, you can leave PROXY_LIST empty or comment out the ProxyMiddleware in DOWNLOADER_MIDDLEWARES. However, this significantly increases the risk of your IP being blocked.
### 6. Configure Scraping Keywords (Optional)
Define the topics you want to scrape by editing the keywords list in **spider/scrapy_project/weibo_collector/spiders/weibo_spider.py**:

```Python

# spider/scrapy_project/weibo_collector/spiders/weibo_spider.py
class WeiboSpider(scrapy.Spider):
    # ...
    def start_requests(self):
        keywords = ["#YourFirstInterestingTopic#", "#AnotherTopic#", "KeywordSearch"]
        # ...
```
7. Prepare Stopword List (Optional but Recommended)
A basic stopwords.txt is included. For superior analysis, use a more comprehensive Chinese stopword list.

- Name your custom list **stopwords.txt**.
- Place it in:
    - **spider/scrapy_project/weibo_collector/** (alongside pipelines.py)
    - OR in the same directory as the **analyze_weibo_data.py** script. The analysis script will automatically attempt to load it.

## 🏃‍♀️ How to Run
### 1. Execute the Weibo Scraper
Navigate to the Scrapy project directory (where **scrapy.cfg** is located):

```Bash
cd spider/scrapy_project
scrapy crawl weibo
Monitor the console output for progress and potential errors. Data will be saved to your configured MongoDB database.
```

### 2. Run the Data Analysis Script
Once sufficient data has been collected, navigate to the directory containing **analyze_weibo_data.py** (typically the project root):

```Bash

# If you are in spider/scrapy_project, go back to the root:
# cd ../..
python analyze_weibo_data.py
```The script will fetch data from MongoDB, perform the analysis (segmentation, TF-IDF, K-Means clustering, LDA topic modeling), and print the results to the console.
```
## 💡 Important Considerations
- Anti-Scraping Countermeasures:
    - Weibo's anti-scraping mechanisms are robust and subject to change.
    - Adjust Request Rate: Fine-tune **DOWNLOAD_DELAY**, **AUTOTHROTTLE_ENABLED**, **AUTOTHROTTLE_START_DELAY**, **AUTOTHROTTLE_MAX_DELAY**, and **CONCURRENT_REQUESTS_PER_DOMAIN** in settings.py to be respectful and avoid detection.- Premium Proxies: Free or low-quality proxies are often ineffective. Invest in reliable, rotating residential or datacenter proxies.
    - CAPTCHA Handling: The current **CaptchaMiddleware** (if enabled and configured, e.g., with a service like TwoCaptcha) might need updates or more sophisticated solutions for complex CAPTCHAs.
    - Login Simulation: For accessing content that requires login, implementing a login flow will significantly increase complexity and maintenance. (This project currently focuses on public data).
    - Selector Updates: Weibo's website structure (CSS selectors) can change without notice. If the spider breaks, you'll need to inspect the new page structure using browser developer tools and update the selectors in **weibo_spider.py**.
- Data Volume & Performance:
    - Ensure your MongoDB instance has adequate storage for large datasets.
    - For very large-scale analysis, consider optimizing the analysis script (e.g., batch processing, more efficient data structures, distributed computing).
- Legal & Ethical Use:
    -Always comply with Weibo's Terms of Service and relevant data privacy laws and regulations.
    - Respect user privacy. Do not collect or use data in a way that could harm individuals.
    - Use the scraped data responsibly and ethically. 
## 📂 Project Structure
```bash
.
├── analyze_weibo_data.py     # Main script for text analysis
├── spider/
│   ├── scrapy.cfg                # Scrapy project configuration file
│   └── scrapy_project/           # Main Scrapy project module
│       ├── __init__.py
│       ├── items.py              # Defines data structures (Scrapy Items)
│       ├── middlewares.py        # Custom Scrapy middlewares (e.g., Proxy, User-Agent, Captcha)
│       ├── pipelines.py          # Scrapy item pipelines (e.g., data cleaning, MongoDB storage)
│       ├── settings.py           # Scrapy project settings
│       └── spiders/              # Contains Scrapy spiders
│           ├── __init__.py
│           └── weibo_spider.py   # The Weibo spider logic
├── requirements.txt            # Python package dependencies
├── README.md                   # This file
└── stopwords.txt               # List of stopwords for text analysis (user-provided or default)
```
## 🤝 Contributing
Contributions are welcome! If you'd like to improve WeiboInsight, please feel free to:
- Fork the repository.
- Create a new branch (git checkout -b feature/YourAmazingFeature).
- Make your changes.
- Commit your changes (git commit -m 'Add some AmazingFeature').
- Push to the branch (git push origin feature/YourAmazingFeature).   
- Open a Pull Request.

Please ensure your code adheres to good coding practices and includes relevant documentation or tests if applicable.
