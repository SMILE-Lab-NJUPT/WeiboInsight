import pymongo
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from gensim import corpora, models
import jieba 
import numpy as np

MONGO_URI = 'mongodb://localhost:27017'
MONGO_DATABASE = 'weibo_data'
POSTS_COLLECTION = 'posts' 
STOP_WORDS = set([
    "的", "了", "我", "你", "他", "她", "它", "们", "是", "有", "在", "也", "都",
    "不", "就", "吧", "吗", "呢", "啊", "哦", "嗯", "嘿", "哈", "啦", "咯", "啧",
    "唰", "哼", "吁", "唉", "呀", "!", "\"", "#", "$", "%", "&", "'", "(", ")",
    "*", "+", ",", "-", ".", "/", ":", ";", "<", "=", ">", "?", "@", "[", "\\",
    "]", "^", "_", "`", "{", "|", "}", "~", "、", "。", "〈", "〉", "《", "》",
    "「", "」", "『", "』", "【", "】", "〔", "〕", "〖", "〗", "〘", "〙", "〚", "〛",
    "〜", "〝", "〞", "〟", "–", "—", "‘", "’", "“", "”", "…", " "
])
try:
    with open("stopwords.txt", "r", encoding="utf-8") as f:
        for line in f:
            STOP_WORDS.add(line.strip())
    print(f"分析脚本：成功加载 {len(STOP_WORDS)} 个停用词。")
except Exception as e:
    print(f"分析脚本：加载停用词文件失败: {e}。将使用内置的简单列表。")


def load_data_from_mongo():
    """从MongoDB加载数据"""
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    collection = db[POSTS_COLLECTION]
    data = list(collection.find({"segmented_text": {"$exists": True, "$ne": []}},
                                 {"text": 1, "segmented_text": 1, "author":1, "post_url": 1, "_id": 0}))
    client.close()
    print(f"从MongoDB加载了 {len(data)} 条数据进行分析。")
    processed_texts_list = [doc.get('segmented_text', []) for doc in data]
    processed_texts_str = [" ".join(words) for words in processed_texts_list]
    original_texts = [doc.get('text', '') for doc in data]
    
    return original_texts, processed_texts_str, processed_texts_list, data


def perform_text_clustering(texts_for_tfidf, num_clusters=5):
    """使用TF-IDF和KMeans进行文本聚类"""
    if not texts_for_tfidf:
        print("没有足够的文本数据进行聚类。")
        return None, None

    print(f"\n开始文本聚类 (K={num_clusters})...")
    vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, 
                                 stop_words=list(STOP_WORDS), 
                                 tokenizer=lambda x: x.split(), 
                                 token_pattern=None) 
    try:
        tfidf_matrix = vectorizer.fit_transform(texts_for_tfidf)
    except ValueError as e:
        print(f"TF-IDF向量化失败: {e}. 可能因为所有词都是停用词或不符合min_df/max_df条件。")
        return None, None

    if tfidf_matrix.shape[0] < num_clusters:
        print(f"警告: 文档数量 ({tfidf_matrix.shape[0]}) 少于聚类数量 ({num_clusters}). 将减少聚类数量。")
        num_clusters = max(1, tfidf_matrix.shape[0]) 
        if num_clusters == 0:
             print("没有可聚类的文档。")
             return None, None


    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
    try:
        kmeans.fit(tfidf_matrix)
    except Exception as e:
        print(f"KMeans 拟合失败: {e}")
        return None, None

    print("文本聚类完成。")
    return kmeans.labels_, vectorizer 

def perform_topic_modeling(tokenized_texts_list, num_topics=5, num_words=10):
    """使用Gensim进行LDA主题建模"""
    if not tokenized_texts_list or not any(tokenized_texts_list):
        print("没有足够的文本数据进行主题建模。")
        return None, None

    print(f"\n开始主题建模 (Topics={num_topics})...")
    dictionary = corpora.Dictionary(tokenized_texts_list)
    dictionary.filter_extremes(no_below=2, no_above=0.95)
    if not dictionary:
        print("Gensim 字典为空，无法创建语料库。可能所有词都被过滤掉了。")
        return None, None

    corpus = [dictionary.doc2bow(text) for text in tokenized_texts_list]
    corpus = [doc for doc in corpus if doc] 
    if not corpus:
        print("Gensim 语料库为空，无法进行主题建模。")
        return None, None

    try:
        lda_model = models.LdaMulticore(corpus=corpus,
                                        id2word=dictionary,
                                        num_topics=num_topics,
                                        random_state=42,
                                        chunksize=100,
                                        passes=10,
                                        alpha='asymmetric', 
                                        eta='auto',
                                        per_word_topics=True) 
    except Exception as e:
        print(f"LDA 模型训练失败: {e}")
        return None, None

    print("主题建模完成。")
    return lda_model, dictionary

def main():
    original_texts, processed_texts_str, processed_texts_list, all_data_docs = load_data_from_mongo()

    if not original_texts:
        print("未能从MongoDB加载到任何有效数据。请检查爬虫是否成功运行并存储了数据。")
        return
    num_clusters = 5 
    if len(original_texts) < num_clusters: 
        num_clusters = max(1, len(original_texts))

    cluster_labels, vectorizer = perform_text_clustering(processed_texts_str, num_clusters=num_clusters)

    if cluster_labels is not None and vectorizer is not None:
        print("\n--- 文本聚类结果 ---")
        for i, doc in enumerate(all_data_docs):
            if i < len(cluster_labels):
                doc['cluster_label'] = int(cluster_labels[i])
        terms = vectorizer.get_feature_names_out()
        order_centroids = None
        if hasattr(vectorizer, 'cluster_centers_'):
             pass

        for i in range(num_clusters):
            print(f"\nCluster {i}:")
            cluster_docs = [(doc.get('author', '未知'), doc.get('text', '')[:100]+"...", doc.get('post_url', ''))
                            for doc_idx, doc in enumerate(all_data_docs)
                            if doc_idx < len(cluster_labels) and cluster_labels[doc_idx] == i]
            for author, text_preview, url in cluster_docs[:5]:
                print(f"  - 作者: {author}, 内容: {text_preview}, 链接: {url}")
    num_topics = 5
    lda_model, dictionary = perform_topic_modeling(processed_texts_list, num_topics=num_topics)

    if lda_model and dictionary:
        print("\n--- LDA 主题模型结果 ---")
        topics = lda_model.print_topics(num_words=10)
        for topic_num, topic_words in topics:
            print(f"Topic #{topic_num}: {topic_words}")
    from collections import Counter
    all_words = [word for sublist in processed_texts_list for word in sublist]
    if all_words:
        word_counts = Counter(all_words)
        print("\n--- 高频词 Top 20 ---")
        for word, count in word_counts.most_common(20):
            print(f"{word}: {count}")

if __name__ == "__main__":
    try:
        jieba.initialize()
        print("Jieba 初始化完成。")
    except Exception as e:
        print(f"Jieba 初始化或加载用户词典失败: {e}")

    main()