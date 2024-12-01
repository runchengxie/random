import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import requests

# 首先需要下载必要的NLTK数据
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

# 下载 Loughran-McDonald 词典
def download_lm_dictionary():
    # 使用 Notre Dame's Software Repository 的词典源
    base_url = "https://raw.githubusercontent.com/jingmouren/gitee_qianlima_LOUGHRAN_MCDONALD/main/data"
    positive_url = f"{base_url}/positive.txt"
    negative_url = f"{base_url}/negative.txt"
    
    try:
        # 下载积极词汇
        positive_response = requests.get(positive_url, timeout=10)
        positive_response.raise_for_status()  # 检查响应状态
        positive_words = set(word.strip().lower() for word in positive_response.text.split('\n') if word.strip())
        
        # 下载消极词汇
        negative_response = requests.get(negative_url, timeout=10)
        negative_response.raise_for_status()  # 检查响应状态
        negative_words = set(word.strip().lower() for word in negative_response.text.split('\n') if word.strip())
        
        # 验证词典大小
        if len(positive_words) < 10 or len(negative_words) < 10:
            raise ValueError("Downloaded dictionaries are too small")
            
    except Exception as e:
        print(f"警告：在线词典下载失败 ({str(e)})，使用内置的简单词典")
        # 使用内置词典
        positive_words = {
            'strong', 'positive', 'growth', 'increase', 'improved',
            'growing', 'pleased', 'exceeded', 'success', 'successful',
            'gain', 'profitable', 'healthy', 'grew', 'effective',
            'excellent', 'outstanding', 'superior', 'robust', 'innovative',
            'confident', 'achievement', 'progress', 'advantage', 'beneficial'
        }
        negative_words = {
            'weak', 'negative', 'decline', 'decrease', 'decreased',
            'loss', 'difficult', 'challenging', 'challenges', 'failed',
            'poor', 'adverse', 'unfavorable', 'disappointing', 'down',
            'risk', 'uncertain', 'weakness', 'deteriorate', 'concerned',
            'crisis', 'problem', 'threat', 'volatile', 'unstable'
        }
    
    print(f"词典大小：积极词 {len(positive_words)} 个，消极词 {len(negative_words)} 个")
    return positive_words, negative_words

def analyze_sentiment(text, positive_words, negative_words):
    # 分词
    tokens = word_tokenize(text.lower())
    
    # 移除停用词
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # 打印分词结果以进行调试
    print("\n分词结果：", tokens)
    
    # 找出匹配的积极和消极词
    positive_matches = [word for word in tokens if word in positive_words]
    negative_matches = [word for word in tokens if word in negative_words]
    
    # 打印匹配到的词
    print("\n匹配到的积极词：", positive_matches)
    print("匹配到的消极词：", negative_matches)
    
    # 计算积极和消极词的数量
    positive_count = len(positive_matches)
    negative_count = len(negative_matches)
    
    # 计算情感得分
    total_words = len(tokens)
    sentiment_score = (positive_count - negative_count) / total_words if total_words > 0 else 0
    
    return {
        'positive_words': positive_count,
        'negative_words': negative_count,
        'total_words': total_words,
        'sentiment_score': sentiment_score
    }

# 示例文本（这里用一个简短的earnings call片段作为示例）
sample_text = """
We are pleased to report strong financial results for the quarter. 
Our revenue grew by 15% year-over-year, exceeding market expectations. 
However, we faced some challenges in our supply chain operations.
Despite these challenges, we maintained healthy profit margins through effective cost management.
"""

# 主程序
if __name__ == "__main__":
    # 下载词典
    positive_words, negative_words = download_lm_dictionary()
    
    # 分析文本
    results = analyze_sentiment(sample_text, positive_words, negative_words)
    
    # 打印结果
    print("\nAnalysis Results:")
    print(f"Positive words: {results['positive_words']}")
    print(f"Negative words: {results['negative_words']}")
    print(f"Total words analyzed: {results['total_words']}")
    print(f"Sentiment score: {results['sentiment_score']:.4f}")