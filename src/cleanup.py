import os
import shutil

def cleanup():
    # 需要删除的assets目录
    assets_dir = "assets"
    
    if os.path.exists(assets_dir):
        print(f"正在删除 {assets_dir} 目录...")
        try:
            shutil.rmtree(assets_dir)
            print(f"{assets_dir} 目录已成功删除")
        except Exception as e:
            print(f"删除目录时出错: {e}")
    else:
        print(f"{assets_dir} 目录不存在")

if __name__ == "__main__":
    cleanup() 