
# coding: utf-8

# In[1]:


import pandas as pd
from sklearn.metrics import f1_score
import numpy as np
import xgboost as xgb
from numpy import loadtxt
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
# import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument('subject')
# args = parser.parse_args()


# In[ ]:


X = pd.read_csv('../data/tfidf_train.csv')
X.head(1)


# In[ ]:


Y_all = pd.read_csv('../data/input.csv')
Y_all.head(1)


# ### 验证

# In[ ]:


# In[ ]:


seed = 7
test_size = 1000
X_train, X_test, y_train, y_test = train_test_split(X, Y_all, test_size=test_size, random_state=seed)


# In[ ]:


params = {
    'booster': 'gbtree',
    'objective': 'multi:softmax',  # 多分类的问题
    'num_class': 4,               # 类别数，与 multisoftmax 并用
    'tree_method': 'gpu_hist',
#     'gamma': 0.1,                  # 用于控制是否后剪枝的参数,越大越保守，一般0.1、0.2这样子。
#     'max_depth': 12,               # 构建树的深度，越大越容易过拟合
#     'lambda': 2,                   # 控制模型复杂度的权重值的L2正则化项参数，参数越大，模型越不容易过拟合。
#     'subsample': 0.7,              # 随机采样训练样本
#     'colsample_bytree': 0.7,       # 生成树时进行的列采样
#     'min_child_weight': 3,
#     'silent': 1,                   # 设置成1则没有运行信息输出，最好是设置为0.
#     'eta': 0.007,                  # 如同学习率
#     'seed': 1000,
#     'nthread': 4,                  # cpu 线程数
}


# In[ ]:

subjects = {
    'price': '价格', 
    'interior': '内饰', 
    'power': '动力', 
    'surface': '外观', 
    'safety': '安全性', 
    'operation':'操控', 
    'gas' : '油耗', 
    'space': '空间', 
    'comfort': '舒适性', 
    'config': '配置'
}

print('validating...')
# f = open('./log', 'w', encoding="utf-8")
for sub in subjects.values():
    dtrain = xgb.DMatrix(X_train, y_train[sub])
    num_rounds = 500
    model = xgb.train(params, dtrain, num_rounds)

    dtest = xgb.DMatrix(X_test)
    pred = model.predict(dtest)

    print(sub, f1_score(y_test[sub], pred, average='macro'))
    # f.write('\n')
    print(sub, f1_score(y_test[sub], pred, average='micro'))
    # f.write('\n')
# f.close()



test_df = pd.read_csv('../data/tfidf_test.csv')
result = pd.DataFrame()
result['content_id'] = test_df['content_id']
for sub in subjects.values():
    dtrain = xgb.DMatrix(X, Y_all[sub])
    num_rounds = 500
    model = xgb.train(params, dtrain, num_rounds)

    dtest = xgb.DMatrix(test_df)
    pred = model.predict(dtest)
    result[sub] = pred


with open('../output/tfidf1.csv', 'w', encoding='utf-8') as f:
    line = '{},{},0,'
    f.write('content_id,subject,sentiment_value,sentiment_word')
    for index, row in result.iterrows():
        has = False
        for sub in subjects.values():
            if row[sub] != 3:
                has = True
                value = line.format(row['content_id'], sub)
                f.write('\n')
                f.write(value)
        if not has:
            value = line.format(row['content_id'], '价格')
            f.write('\n')
            f.write(value)


