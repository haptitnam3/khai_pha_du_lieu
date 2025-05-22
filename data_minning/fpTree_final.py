import csv
from collections import defaultdict, namedtuple
from typing import List, Dict, Optional
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# --------------------------------------------
# Định nghĩa Node cho FP-Tree
# --------------------------------------------
class FPNode:
    def __init__(self, item_name: str, count: int, parent):
        self.item = item_name
        self.count = count
        self.parent = parent
        self.children: Dict[str, 'FPNode'] = {}
        self.link = None  
    #item : tên mục, vd như milk
    #count : số lần xuất hiện, hỗ trợ tại node này 
    #parent : trỏ đến nút cha
    #children : dict chứa các node con
    #link : dùng để tạo danh sách liên kết các node có cùng tên item trong cây (cho header table).
    
    # Tăng số lần xuất hiện
    def increment(self, count: int):
        self.count += count

# --------------------------------------------
# Xây dựng FP-Tree
# --------------------------------------------
class FPTree:
    def __init__(self):
        self.root = FPNode(None, 1, None)
        self.header_table = defaultdict(list)
        #header_table: bảng chứa các item, ánh xạ đến danh sách các node tương ứng trong cây.

    # Hàm thêm 1 giao dịch vào FP-Growth
    #Từ nút gốc, duyệt qua từng item trong giao dịch
    #Nếu item đã có node con --> tăng count
    #Nếu chưa có --> tạo node mới
    def add_transaction(self, transaction: List[str]):
        current = self.root
        for item in transaction:
            if item in current.children:
                current.children[item].increment(1)
            else:
                new_node = FPNode(item, 1, current)
                current.children[item] = new_node
                self.header_table[item].append(new_node)
            current = current.children[item]

# --------------------------------------------
# Đọc dữ liệu từ CSV
# --------------------------------------------
#Mở file CSV, mỗi dòng là 1 giao dịch → chuyển thành danh sách các mục (items)
def read_transactions(filename: str) -> List[List[str]]:
    transactions = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            transaction = [item.strip() for item in row if item.strip()]
            if transaction:
                transactions.append(transaction)
    return transactions

# --------------------------------------------
# Tính tần suất item
# --------------------------------------------
# Duyệt qua toàn bộ giao dịch → đếm số lần xuất hiện mỗi item.
def get_item_supports(transactions: List[List[str]]) -> Dict[str, int]:
    item_counts = defaultdict(int)
    for transaction in transactions:
        for item in transaction:
            item_counts[item] += 1
    return dict(item_counts)

# --------------------------------------------
# Lọc item theo min support
# --------------------------------------------

#Lọc những item không đạt ngưỡng hỗ trợ tối thiểu min_support.
#Sắp xếp giao dịch theo tần suất giảm dần (rất quan trọng cho FP-tree).
def filter_items(transactions: List[List[str]], min_support: int, item_supports: Dict[str, int]) -> List[List[str]]:
    filtered = []
    for transaction in transactions:
        filtered_transaction = [item for item in transaction if item_supports.get(item, 0) >= min_support]
        filtered_transaction.sort(key=lambda x: (-item_supports[x], x))  # Giảm dần theo support
        if filtered_transaction:
            filtered.append(filtered_transaction)
    return filtered

# --------------------------------------------
# Tạo FP-tree từ giao dịch
# --------------------------------------------
def build_fp_tree(transactions: List[List[str]]) -> FPTree:
    tree = FPTree()
    for transaction in transactions:
        tree.add_transaction(transaction)
    return tree

# --------------------------------------------
# Lấy các đường dẫn từ node lên root
# --------------------------------------------
def ascend_fp_tree(node: FPNode) -> List[str]:
    path = []
    while node and node.parent and node.parent.item is not None:
        node = node.parent
        path.append(node.item)
    path.reverse()
    return path

# --------------------------------------------
# Tạo conditional pattern base
# --------------------------------------------
#Cho mỗi item, tạo danh sách các giao dịch liên quan đến item đó (dùng trong cây con).
def find_prefix_paths(base_pat: str, node_links: List[FPNode]) -> List[List[str]]:
    conditional_patterns = []
    for node in node_links:
        path = ascend_fp_tree(node)
        for _ in range(node.count):
            conditional_patterns.append(path)
    return conditional_patterns

# --------------------------------------------
# Hàm FP-Growth đệ quy
# --------------------------------------------

#Với mỗi item trong header table:
#Tính tổng support.
#Thêm vào tập mục thường xuyên.
#Tạo cây con (conditional FP-tree).
#Gọi đệ quy để mở rộng tập hợp.
def fp_growth(tree: FPTree, prefix: List[str], min_support: int, freq_itemsets: Dict[tuple, int]):
    for item, nodes in sorted(tree.header_table.items(), key=lambda x: len(x[1])):
        new_prefix = prefix + [item]
        support = sum(node.count for node in nodes)
        freq_itemsets[tuple(new_prefix)] = support

        conditional_patterns = find_prefix_paths(item, nodes)
        if conditional_patterns:
            item_supports = get_item_supports(conditional_patterns)
            filtered_patterns = filter_items(conditional_patterns, min_support, item_supports)
            conditional_tree = build_fp_tree(filtered_patterns)
            if conditional_tree.header_table:
                fp_growth(conditional_tree, new_prefix, min_support, freq_itemsets)

# --------------------------------------------
# Hàm FP-Growth đệ quy
# --------------------------------------------
def build_nx_graph(node, graph, parent_name=None):
    node_label = f"{node.item}:{node.count}"
    graph.add_node(node_label)

    if parent_name:
        graph.add_edge(parent_name, node_label)

    for child in node.children.values():
        build_nx_graph(child, graph, node_label)

#Vẽ cây FP-Tree
def draw_fp_tree_networkx(fp_tree_root):
    G = nx.DiGraph()
    build_nx_graph(fp_tree_root, G)

    pos = nx.spring_layout(G, k=1.5, iterations=100)  # Bạn có thể thay bằng hierarchy layout nếu cần
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=2000, font_size=10, font_weight="bold", arrows=True)
    plt.title("FP-Tree Visualization (networkx)")
    plt.show()


# --------------------------------------------
# Chạy chương trình
# --------------------------------------------
def pause(step_desc):
    user_input = input(f"\n➡️ {step_desc}\n   Nhấn Enter để tiếp tục, hoặc gõ 'q' để thoát: ")
    if user_input.lower() == 'q':
        print("⛔ Kết thúc chương trình theo yêu cầu.")
        exit()

def main():
    filename = "sample.csv"
    min_support_ratio = 0.5

    # Bước 1: Đọc dữ liệu
    pause("Bước 1: Đọc dữ liệu từ file")
    transactions = read_transactions(filename)
    transactions = [[item.strip() for item in tran] for tran in transactions]
    total_transactions = len(transactions)
    min_support_threshold = total_transactions * min_support_ratio  # không ép kiểu int nữa

    print(f"✅ Tổng số giao dịch: {total_transactions}")
    print(f"✅ Ngưỡng min_support: {min_support_threshold:.2f} ({min_support_ratio:.2f})")
    print(f"✉️ Một vài giao dịch đầu tiên:")
    for t in transactions[:5]:
        print(f"   {t}")

    # Bước 2: Đếm support
    pause("Bước 2: Đếm số lần xuất hiện (support) của từng item")
    item_supports = get_item_supports(transactions)
    print(f"📊 Top 10 item phổ biến nhất:")
    for item, count in sorted(item_supports.items(), key=lambda x: -x[1])[:10]:
        print(f"   {item}: {count}")

    # Bước 3: Lọc và sắp xếp giao dịch
    pause("Bước 3: Lọc các item không đủ support và sắp xếp lại từng giao dịch")
    filtered_transactions = filter_items(transactions, min_support_threshold, item_supports)
    print("📂 Giao dịch sau khi lọc và sắp xếp (top 5):")
    for t in filtered_transactions[:5]:
        print(f"   {t}")

    # Bước 4: Xây dựng FP-Tree
    pause("Bước 4: Xây dựng cây FP-Tree")
    fp_tree = build_fp_tree(filtered_transactions)
    print("🌲 FP-Tree đã được xây dựng.")

    # Bước 5: Vẽ FP-Tree bằng networkx
    pause("Bước 5: Vẽ cây FP-Tree (hiển thị bằng thư viện networkx)")
    draw_fp_tree_networkx(fp_tree.root)
    print("🖼️ Cây FP-Tree đã được vẽ.")

    # Bước 6: Áp dụng FP-Growth
    pause("Bước 6: Áp dụng thuật toán FP-Growth để khai thác tập mục phổ biến")
    freq_itemsets = {}
    fp_growth(fp_tree, [], min_support_threshold, freq_itemsets)
    print(f"✅ Tổng số tập mục phổ biến tìm được: {len(freq_itemsets)}")

    # Bước 7: In kết quả
    pause("Bước 7: Hiển thị các tập mục phổ biến")
    result_data = []
    for itemset, count in freq_itemsets.items():
        support_ratio = count / total_transactions
        result_data.append({
            'support': support_ratio, #round(support_ratio, 2)
            'itemsets': tuple(itemset)
        })

    df_result = pd.DataFrame(result_data)
    df_result.reset_index(drop=True, inplace=True)

    print("\n🎯 Các tập mục phổ biến (min_support = {:.2f}):\n".format(min_support_ratio))
    print(df_result.to_string(index=True))

if __name__ == "__main__":
    main()
