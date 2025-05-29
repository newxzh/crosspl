import os
import shutil
import stat

# 设置大文件夹路径
source_folder = 'D:\CAE\Repository'
# 设置目标文件夹路径
target_folder = 'D:\CAE\Splited_Repository'

# 获取文件夹中所有文件
files = [f for f in os.listdir(source_folder) if os.path.isdir(os.path.join(source_folder, f))]

# 每个子文件夹包含2000个文件
batch_size = 2000

# 计算需要创建多少个文件夹
num_batches = len(files) // batch_size + (1 if len(files) % batch_size > 0 else 0)

# 遍历每个批次
for i in range(num_batches):
    # 创建目标子文件夹
    batch_folder = os.path.join(target_folder, f'{i + 1}')
    os.makedirs(batch_folder, exist_ok=True)

    # 选择当前批次的文件
    start_index = i * batch_size
    end_index = min(start_index + batch_size, len(files))
    batch_files = files[start_index:end_index]

    # 移动文件到目标子文件夹
    for file_name in batch_files:
        source_file = os.path.join(source_folder, file_name)
        target_file = os.path.join(batch_folder, file_name)

        # 如果文件是只读的，去除只读属性
        if os.path.isfile(source_file):
            file_attributes = os.stat(source_file).st_mode
            if file_attributes & stat.S_IREAD:  # 判断是否是只读文件
                os.chmod(source_file, stat.S_IWRITE)  # 取消只读属性

        # 移动文件
        try:
            shutil.move(source_file, target_file)
        except Exception as e:
            print(f"移动文件 {file_name} 时出错: {e}")

print("文件已按每2000个一组划分完成。")