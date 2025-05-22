import os
import shutil
import sys

def copy_folder_contents(src_dir, dest_dir):
    if not os.path.exists(src_dir):
        print(f"源目录不存在: {src_dir}")
        return

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)  # 创建目标目录及其父目录
        print(f"已创建目标目录: {dest_dir}")

    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(dest_dir, item)

        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)  # 复制目录
        else:
            shutil.copy2(s, d)  # 复制文件，保留元数据

    print(f"已将所有内容从 {src_dir} 拷贝到 {dest_dir}")

# 示例用法：传入两个路径作为参数
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python script.py <源目录> <目标目录>")
        sys.exit(1)

    source_path = sys.argv[1]
    target_path = sys.argv[2]

    copy_folder_contents(source_path, target_path)
