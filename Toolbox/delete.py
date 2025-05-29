import csv
# 输入和输出文件路径
input_file = "../RepositoryList.csv"
output_file = "RepositoryList1.csv"

# 删除空白行
with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
        open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        # 检查是否是空白行
        if any(field.strip() for field in row):
            writer.writerow(row)

print(f"空白行已删除，结果保存到 {output_file}")
