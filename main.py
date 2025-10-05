import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序事件循环
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
