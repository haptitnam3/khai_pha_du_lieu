import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

# Đọc dữ liệu
def load_transactions(path):
    transactions = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            row = [item.strip() for item in line.strip().split(',') if item.strip()]
            if row:
                transactions.append(row)
    return transactions

DATASET_PATH = 'D:/KPDL/khai_pha_du_lieu/DataSetA.csv'
MIN_SUP = 0.05
MIN_CONF = 0.5

transactions = load_transactions(DATASET_PATH)
te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df = pd.DataFrame(te_ary, columns=te.columns_)

# Apriori
frequent_itemsets = apriori(df, min_support=MIN_SUP, use_colnames=True)
# Sắp xếp theo support giảm dần
frequent_itemsets = frequent_itemsets.sort_values(by='support', ascending=False).reset_index(drop=True)
print('Frequent Itemsets:')
print(frequent_itemsets)

query = frequent_itemsets[
    frequent_itemsets['itemsets'].apply(lambda x: 'Tea Powder' in x) 
    # rules_df['antecedent'].apply(lambda x: set(['Milk']).issubset(x)) &
    # rules_df['consequent'].apply(lambda x: 'Bread' in x)
]
print(query)
# Association Rules
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=MIN_CONF)
print('\nAssociation Rules:')
print(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])

