import csv
from itertools import combinations, chain
import pandas as pd

# Đọc dữ liệu
DATASET_PATH = 'D:\KPDL\khai_pha_du_lieu\DataSetA.csv'
MIN_SUP = 0.05   # min support
MIN_CONF = 0.5    # min confidence

def load_transactions(path):
    transactions = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            # Loại bỏ các phần tử rỗng
            transaction = [item.strip() for item in row if item.strip()]
            if transaction:
                transactions.append(transaction)
    return transactions

def get_frequent_itemsets(transactions, min_sup):
    itemsets = []
    support_data = {}
    n_transactions = len(transactions)
    # Đếm tần suất từng item
    item_count = {}
    for transaction in transactions:
        for item in transaction:
            item_count[frozenset([item])] = item_count.get(frozenset([item]), 0) + 1
    # Lọc các item có support >= min_sup
    L1 = set()
    for item, count in item_count.items():
        support = count / n_transactions
        if support >= min_sup:
            L1.add(item)
            support_data[item] = support
    Lk = L1
    k = 2
    def has_infrequent_subset(candidate, Lk_prev):
        for subset in combinations(candidate, len(candidate) - 1):
            if frozenset(subset) not in Lk_prev:
                return True
        return False
    while Lk:
        itemsets.extend(Lk)
        # Sinh ứng viên với kiểm tra tập con phổ biến
        candidates = set()
        for i in Lk:
            for j in Lk:
                union = i.union(j)
                if len(union) == k and not has_infrequent_subset(union, Lk):
                    candidates.add(union)
        candidate_count = {}
        for transaction in transactions:
            t_set = set(transaction)
            for candidate in candidates:
                if candidate.issubset(t_set):
                    candidate_count[candidate] = candidate_count.get(candidate, 0) + 1
        Lk = set()
        for candidate, count in candidate_count.items():
            support = count / n_transactions
            if support >= min_sup:
                Lk.add(candidate)
                support_data[candidate] = support
        k += 1
    return itemsets, support_data

def generate_association_rules(frequent_itemsets, support_data, min_conf):
    rules = []
    for itemset in frequent_itemsets:
        if len(itemset) < 2:
            continue
        for i in range(1, len(itemset)):
            for antecedent in combinations(itemset, i):
                antecedent = frozenset(antecedent)
                consequent = itemset - antecedent
                if not consequent:
                    continue
                conf = support_data[itemset] / support_data[antecedent]
                if conf >= min_conf:
                    rules.append((set(antecedent), set(consequent), support_data[itemset], conf))
    return rules

def main():
    transactions = load_transactions(DATASET_PATH)
    print(f"Số lượng giao dịch: {len(transactions)}")
    frequent_itemsets, support_data = get_frequent_itemsets(transactions, MIN_SUP)
    # Chuyển thành DataFrame
    df = pd.DataFrame([
        {"itemset": tuple(sorted(itemset)), "support": support_data[itemset]}
        for itemset in frequent_itemsets
    ])
    # Sắp xếp DataFrame theo support giảm dần
    df = df.sort_values(by='support', ascending=False).reset_index(drop=True)
    print(f"\nDataFrame các tập phổ biến (frequent itemsets) với min_sup={MIN_SUP}:")
    print(df)
    rules = generate_association_rules(frequent_itemsets, support_data, MIN_CONF)
    # Chuyển luật kết hợp thành DataFrame
    rules_df = pd.DataFrame([
        {
            'antecedent': tuple(sorted(antecedent)),
            'consequent': tuple(sorted(consequent)),
            'support': support,
            'confidence': conf
        }
        for antecedent, consequent, support, conf in rules
    ])
    # print(f"\nDataFrame các luật kết hợp (association rules) với min_conf={MIN_CONF}:")
    
    print(rules_df)
    
#     query = rules_df[
#     rules_df['antecedent'].apply(lambda x: 'Sweet' in x) 
#     # rules_df['antecedent'].apply(lambda x: set(['Milk']).issubset(x)) &
#     # rules_df['consequent'].apply(lambda x: 'Bread' in x)
# ]
#     print(query)
    query = df[
    df['itemset'].apply(lambda x: 'Tea Powder' in x) 
    # rules_df['antecedent'].apply(lambda x: set(['Milk']).issubset(x)) &
    # rules_df['consequent'].apply(lambda x: 'Bread' in x)
]
    print(query)

if __name__ == '__main__':
    main()
