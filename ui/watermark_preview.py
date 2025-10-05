from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor, QImage
from PIL import Image, ImageQt
import os

class WatermarkPreview(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setStyleSheet('background-color: #f0f0f0; border: 1px solid #d0d0d0;')
        
        # 初始化变量
        self.image_path = None
        self.original_image = None
        self.watermark_settings = None
        self.dragging = False
        self.drag_start = QPoint()
        self.watermark_pos = QPoint()
        self.scale_factor = 1.0
    
    def setImage(self, image_path):
        """设置预览图片
        
        Args:
            image_path: 图片路径
        """
        if not os.path.exists(image_path):
            return
        
        self.image_path = image_path
        self.original_image = QPixmap(image_path)
        
        # 计算缩放比例以适应预览区域
        preview_size = self.size()
        scaled_size = self.original_image.size()
        
        if scaled_size.width() > preview_size.width() or scaled_size.height() > preview_size.height():
            scaled_pixmap = self.original_image.scaled(
                preview_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.scale_factor = scaled_pixmap.width() / self.original_image.width()
        else:
            scaled_pixmap = self.original_image
            self.scale_factor = 1.0
        
        self.setPixmap(scaled_pixmap)
        self.updatePreview()
    
    def setWatermarkSettings(self, settings):
        """更新水印设置
        
        Args:
            settings: 水印设置字典
        """
        self.watermark_settings = settings
        if not settings.get('position_custom'):
            # 如果不是自定义位置，使用预设位置
            self.watermark_pos = self.getPresetPosition(settings.get('position', '中心'))
        self.updatePreview()
    
    def updatePreview(self):
        """更新预览显示"""
        if not self.original_image or not self.watermark_settings:
            return
        
        # 创建工作画布
        preview = QPixmap(self.pixmap().size())
        preview.fill(Qt.GlobalColor.transparent)
        
        # 绘制原图
        painter = QPainter(preview)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(0, 0, self.pixmap())
        
        # 绘制水印
        if self.watermark_settings.get('type') == '文本水印':
            self.drawTextWatermark(painter)
        else:
            self.drawImageWatermark(painter)
        
        painter.end()
        self.setPixmap(preview)
    
    def drawTextWatermark(self, painter):
        """绘制文本水印
        
        Args:
            painter: QPainter对象
        """
        try:
            text = self.watermark_settings.get('text', '')
            if not text:
                return
            
            print(f"正在绘制文本水印: {text}")
        except Exception as e:
            print(f"获取水印文本时出错: {e}")
            return
        
        try:
            # 设置字体
            font = QFont()
            font_settings = self.watermark_settings.get('font', {})
            font_family = font_settings.get('family', 'Arial')
            print(f"正在设置字体: {font_family}")
            
            # 检查字体是否存在
            font_path = os.path.join(os.environ['WINDIR'], 'Fonts', f'{font_family}.ttf')
            if not os.path.exists(font_path):
                font_path = os.path.join(os.environ['WINDIR'], 'Fonts', f'{font_family}.TTF')
            
            if not os.path.exists(font_path):
                # 如果找不到指定字体，使用微软雅黑
                print(f"找不到字体 {font_family}，使用微软雅黑替代")
                font.setFamily('Microsoft YaHei')
            else:
                font.setFamily(font_family)
            
            # 设置字体大小
            font_size = max(1, int(font_settings.get('size', 40) * self.scale_factor))
            print(f"字体大小: {font_size}")
            font.setPointSize(font_size)
            
            # 设置字体样式
            font.setBold(font_settings.get('bold', False))
            font.setItalic(font_settings.get('italic', False))
            painter.setFont(font)
        except Exception as e:
            print(f"设置字体时出错: {e}")
            # 使用安全的默认值
            default_font = QFont('Microsoft YaHei', 40)
            painter.setFont(default_font)
        
        try:
            # 设置颜色和透明度
            color = self.watermark_settings.get('color', '#000000')
            opacity = self.watermark_settings.get('opacity', 100)
            print(f"设置颜色: {color}, 透明度: {opacity}%")
            
            if isinstance(color, str):
                color = QColor(color)
            color.setAlpha(int(255 * opacity / 100))
            painter.setPen(color)
            
            # 计算文本尺寸
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()
            print(f"文本尺寸: {text_width}x{text_height}")
            
            # 保存当前状态
            painter.save()
            
            # 移动到绘制位置并旋转
            painter.translate(self.watermark_pos)
            rotation = self.watermark_settings.get('rotation', 0)
            if rotation:
                print(f"旋转角度: {rotation}°")
                painter.rotate(rotation)
            
            # 绘制文本（考虑中心点偏移）
            draw_x = -text_width/2
            draw_y = text_height/2
            print(f"绘制位置: ({draw_x}, {draw_y})")
            painter.drawText(draw_x, draw_y, text)
            
            # 恢复状态
            painter.restore()
            
        except Exception as e:
            print(f"绘制文本水印时出错: {e}")
            # 恢复画笔状态
            painter.restore()
            # 使用最基本的绘制方式
            painter.setPen(QColor('#000000'))
            painter.drawText(self.watermark_pos, text)
    
    def drawImageWatermark(self, painter):
        """绘制图片水印
        
        Args:
            painter: QPainter对象
        """
        image_path = self.watermark_settings.get('image_path')
        if not image_path or not os.path.exists(image_path):
            return
        
        # 加载水印图片
        watermark = QPixmap(image_path)
        
        # 调整大小
        scale = self.watermark_settings.get('scale', 100) / 100 * self.scale_factor
        watermark = watermark.scaled(
            int(watermark.width() * scale),
            int(watermark.height() * scale),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # 设置透明度
        opacity = self.watermark_settings.get('opacity', 100)
        painter.setOpacity(opacity / 100)
        
        # 保存当前状态
        painter.save()
        
        # 移动到绘制位置并旋转
        painter.translate(self.watermark_pos)
        rotation = self.watermark_settings.get('rotation', 0)
        if rotation:
            painter.rotate(rotation)
        
        # 绘制图片（考虑中心点偏移）
        painter.drawPixmap(-watermark.width()/2, -watermark.height()/2, watermark)
        
        # 恢复状态
        painter.restore()
    
    def getPresetPosition(self, position):
        """获取预设位置坐标
        
        Args:
            position: 位置名称
            
        Returns:
            QPoint: 位置坐标
        """
        if not self.pixmap():
            return QPoint()
        
        width = self.pixmap().width()
        height = self.pixmap().height()
        padding = int(50 * self.scale_factor)  # 边距，转换为整数
        
        positions = {
            '左上角': QPoint(padding, padding),
            '右上角': QPoint(width - padding, padding),
            '左下角': QPoint(padding, height - padding),
            '右下角': QPoint(width - padding, height - padding),
            '中心': QPoint(width // 2, height // 2)
        }
        
        return positions.get(position, QPoint(width // 2, height // 2))
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start = event.pos()
            self.watermark_settings['position_custom'] = True
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.dragging:
            delta = event.pos() - self.drag_start
            self.watermark_pos += delta
            self.drag_start = event.pos()
            self.updatePreview()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False