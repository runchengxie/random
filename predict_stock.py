from sklearn.linear_model import LinearRegression

def predict_stock_price():
    # 我们的简单数据：今天的价格 vs. 明天的价格
    X = [[100], [101], [102], [103], [104]]  # 今天的价格
    y = [101, 102, 103, 104, 105]             # 明天的价格
    
    # 创建模型
    model = LinearRegression()
    model.fit(X, y)
    
    # 预测明天的价格
    today_price = [[105]]
    predicted_price = model.predict(today_price)
    print(f"预测明天的股价是: {predicted_price[0]:.2f}") 

# 调用函数
predict_stock_price()