from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QDropEvent, QDragEnterEvent, QPixmap, QIcon
from pathlib import Path
from utils.image_processor import ImageProcessor

class ImageListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)  # 启用拖放
        self.setIconSize(QSize(100, 100))  # 设置缩略图大小
        self.setViewMode(QListWidget.ViewMode.IconMode)  # 使用图标模式显示
        self.setSpacing(10)  # 设置项目间距
        self.setMovement(QListWidget.Movement.Static)  # 禁止项目移动
        
        self.image_processor = ImageProcessor()
        self.image_paths = []  # 存储图片路径
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否包含图片文件
            for url in event.mimeData().urls():
                if self._is_valid_image(url.toLocalFile()):
                    event.acceptProposedAction()
                    return
    
    def dropEvent(self, event: QDropEvent):
        """处理拖放事件"""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if self._is_valid_image(file_path):
                self.add_image(file_path)
    
    def add_image(self, image_path: str):
        """添加图片到列表"""
        if not self._is_valid_image(image_path):
            return
        
        # 生成缩略图
        thumbnail = self.image_processor.create_thumbnail(image_path)
        if thumbnail:
            # 创建列表项
            item = QListWidgetItem()
            item.setIcon(QIcon(QPixmap.fromImage(thumbnail)))
            item.setText(Path(image_path).name)
            item.setData(Qt.ItemDataRole.UserRole, image_path)  # 存储完整路径
            
            self.addItem(item)
            self.image_paths.append(image_path)
    
    def _is_valid_image(self, file_path: str) -> bool:
        """检查文件是否为有效的图片格式"""
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
        return Path(file_path).suffix.lower() in valid_extensions
    
    def has_images(self) -> bool:
        """检查是否有图片在列表中"""
        return len(self.image_paths) > 0
    
    def get_images(self) -> list:
        """获取所有图片路径"""
        return self.image_paths.copy()