
"""
跨平台打包脚本
使用方法: python build.py
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def build_executable():
    """构建可执行文件"""
    print(f"正在为 {platform.system()} 构建可执行文件...")
    
    # 基本的 PyInstaller 参数
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "notify-change",
        "--clean",
        # 如果有 GUI，去掉 --console
        "--console",
    ]
    
    # 添加数据文件
    data_dirs = ["templates", "static", "config"]
    for data_dir in data_dirs:
        if Path(data_dir).exists():
            if platform.system() == "Windows":
                cmd.extend(["--add-data", f"{data_dir};{data_dir}"])
            else:
                cmd.extend(["--add-data", f"{data_dir}:{data_dir}"])
    
    # 主入口文件改为 app.py (Flask Web应用)
    cmd.append("app.py")
    
    try:
        subprocess.run(cmd, check=True)
        
        # 显示构建结果
        dist_dir = Path("dist")
        if dist_dir.exists():
            files = list(dist_dir.iterdir())
            print(f"\n✅ 构建成功! 文件位置:")
            for file in files:
                print(f"   📦 {file}")
                print(f"   📏 大小: {file.stat().st_size / 1024 / 1024:.1f} MB")
            
            # # 复制用户说明文件到 dist 目录
            # readme_user = Path("README_USER.md")
            # if readme_user.exists():
            #     import shutil
            #     shutil.copy2(readme_user, dist_dir / "使用说明.md")
            #     print(f"   📋 使用说明已复制到 dist 目录")
                
            # print(f"\n🎉 打包完成!")
            # print(f"💡 运行 {dist_dir}/notify-change-web.exe 启动程序")
            # print(f"📖 查看 {dist_dir}/使用说明.md 了解详细使用方法")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()
