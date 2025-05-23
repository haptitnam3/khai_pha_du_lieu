# dùng thuật toán có sẵn

from mlxtend.frequent_patterns import fpgrowth
from mlxtend.preprocessing import TransactionEncoder
import pandas as pd

# Đọc và làm sạch dữ liệu
file_path = 'DataSetA.csv'
with open(file_path, 'r') as file:
    transactions = [
        [item.strip() for item in line.strip().split(',') if item.strip()]
        for line in file if line.strip()
    ]


# Encode dữ liệu
te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df = pd.DataFrame(te_ary, columns=te.columns_)

# Áp dụng thuật toán FP-Growth
results = fpgrowth(df, min_support=0.01, use_colnames=True)

# Gán chỉ số dòng từ 0 tăng dần
results.reset_index(drop=True, inplace=True)

# In kết quả
print("\n🎯 Các tập mục phổ biến (min_support = 0.5):\n")
print(results.to_string(index=True))
