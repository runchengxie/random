from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

def load_finbert():
    # 加载FinBERT模型和分词器
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    return tokenizer, model

def analyze_sentiment(text, tokenizer, model):
    # 对输入文本进行分词
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    
    # 使用模型进行预测
    outputs = model(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    # 获取预测结果
    labels = ['positive', 'negative', 'neutral']
    sentiment = labels[predictions.argmax().item()]
    scores = predictions[0].detach().numpy()
    
    return {
        'sentiment': sentiment,
        'scores': {label: float(score) for label, score in zip(labels, scores)}
    }

def main():
    # 加载模型
    print("Loading FinBERT model...")
    tokenizer, model = load_finbert()
    
    # 示例文本
    texts = [
        "Company X reported strong earnings growth and increased dividend.",
        "The stock market crashed due to economic concerns.",
        "The company maintained stable performance in Q3."
    ]
    
    # 分析每个文本的情感
    print("\nAnalyzing sentiments...")
    for text in texts:
        result = analyze_sentiment(text, tokenizer, model)
        print(f"\nText: {text}")
        print(f"Sentiment: {result['sentiment']}")
        print("Scores:")
        for label, score in result['scores'].items():
            print(f"  {label}: {score:.4f}")

if __name__ == "__main__":
    main()
