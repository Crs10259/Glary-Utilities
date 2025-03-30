import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QCoreApplication, Qt
from utils.settings_manager import Settings
from main_window import MainWindow
from components.icons import Icon

def main():
    
    # 解析命令行参数
    check_translations = '--check-translations' in sys.argv
    debug_mode = '--debug' in sys.argv
    
    # 启用高DPI缩放
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("Glary Utilities")
    app.setOrganizationName("Glarysoft")
    
    # 设置应用程序图标
    if Icon.Icon.Exist:
        app.setWindowIcon(QIcon(Icon.Icon.Path))
    
    # 初始化设置
    settings = Settings()
    
    # 开启调试模式
    if debug_mode:
        settings.set_setting("debug_mode", True)
        print("调试模式已启用")
    
    try:
        # 创建主窗口
        window = MainWindow(settings)
        
        # 检查缺失的翻译
        if check_translations:
            print("正在检查缺失的翻译...")
            window.check_all_translations()
            print("翻译检查完成")
            
            # 如果只检查翻译，则退出
            if '--exit-after-check' in sys.argv:
                print("检查后退出")
                return 0
        
        # 显示窗口并启动应用程序
        window.show()
        return app.exec_()
        
    except KeyError as e:

        print(f"错误: {e}")
        
        # 仅在非检查模式下显示对话框
        if not check_translations:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle("翻译错误")
            error_dialog.setText(f"缺失翻译: {e}")
            error_dialog.setInformativeText("请检查翻译文件，确保所有必需的键都存在。")
            error_dialog.exec_()
        
        return 1
    # except Exception as e:
    #     print(f"错误: {e}")
        
        # # 仅在非检查模式下显示对话框
        # if not check_translations:
        #     error_dialog = QMessageBox()
        #     error_dialog.setIcon(QMessageBox.Critical)
        #     error_dialog.setWindowTitle("错误")
        #     error_dialog.setText(f"发生错误: {e}")
        #     error_dialog.exec_()
        
        # return 1

if __name__ == "__main__":
    sys.exit(main()) 