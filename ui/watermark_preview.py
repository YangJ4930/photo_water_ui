from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor, QImage, QCursor, QPen
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
        self.updating_preview = False  # 防止重复更新的标志
        self.watermark_bounds = QRect()  # 水印边界
        self.hover_watermark = False  # 鼠标是否悬停在水印上
        self.drag_offset = QPoint()  # 拖拽偏移量
        
        # 启用鼠标跟踪
        self.setMouseTracking(True)
    
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
        
        # 如果已有水印设置，重新计算位置
        if self.watermark_settings:
            if not self.watermark_settings.get('position_custom'):
                self.watermark_pos = self.getPresetPosition(self.watermark_settings.get('position', '中心'))
            elif self.watermark_pos == QPoint():
                self.watermark_pos = self.getPresetPosition('中心')

        
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
        else:
            # 如果是自定义位置但watermark_pos还是默认值，设置为中心
            if self.watermark_pos == QPoint():
                self.watermark_pos = self.getPresetPosition('中心')
        self.updatePreview()
    
    def updatePreview(self):
        """更新预览显示"""
        if not self.original_image or not self.watermark_settings or self.updating_preview:
            return
        
        # 设置更新标志，防止重复调用
        self.updating_preview = True
        
        try:
            # 获取当前显示的缩放图片尺寸
            current_size = self.size()
            
            # 重新缩放原始图片
            scaled_image = self.original_image.scaled(
                current_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # 更新缩放比例
            self.scale_factor = scaled_image.width() / self.original_image.width()
            
            # 创建工作画布，使用缩放后的图片尺寸
            preview = QPixmap(scaled_image.size())
            preview.fill(Qt.GlobalColor.transparent)
            
            # 绘制原图
            painter = QPainter(preview)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.drawPixmap(0, 0, scaled_image)
            
            # 绘制水印
            if self.watermark_settings.get('type') == '文本水印':
                self.drawTextWatermark(painter)
            else:
                self.drawImageWatermark(painter)
            
            # 如果正在拖拽或悬停，绘制水印边界
            if self.dragging or self.hover_watermark:
                self.drawWatermarkBounds(painter)
            
            painter.end()
            self.setPixmap(preview)
            
            # 计算水印边界
            self.calculateWatermarkBounds()
        finally:
            # 重置更新标志
            self.updating_preview = False
    
    def updateDragPreview(self):
        """拖动时的轻量级预览更新"""
        if not self.original_image or not self.watermark_settings:
            return
        
        # 获取当前显示的缩放图片尺寸
        current_size = self.size()
        
        # 重新缩放原始图片
        scaled_image = self.original_image.scaled(
            current_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # 更新缩放比例
        self.scale_factor = scaled_image.width() / self.original_image.width()
        
        # 创建透明画布
        preview = QPixmap(scaled_image.size())
        preview.fill(Qt.GlobalColor.transparent)
        
        # 绘制原图
        painter = QPainter(preview)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(0, 0, scaled_image)
        
        # 绘制当前位置的水印
        if self.watermark_settings.get('type') == '文本水印':
            self.drawTextWatermark(painter)
        else:
            self.drawImageWatermark(painter)
        
        # 绘制拖动边界
        self.drawWatermarkBounds(painter)
        
        painter.end()
        
        # 更新显示
        self.setPixmap(preview)
        
        # 更新水印边界
        self.calculateWatermarkBounds()
    
    def paintEvent(self, event):
        """重写paintEvent以处理拖拽时的实时绘制"""
        # 始终使用默认的paintEvent，避免无限循环
        super().paintEvent(event)
    
    def calculateWatermarkBounds(self):
        """计算水印边界"""
        if not self.watermark_settings:
            return
        

        
        if self.watermark_settings.get('type') == '文本水印':
            text = self.watermark_settings.get('text', '')
            if not text:
                return
            
            # 创建临时画笔计算文本尺寸
            temp_pixmap = QPixmap(1, 1)
            temp_painter = QPainter(temp_pixmap)
            
            # 设置字体
            font = QFont()
            font_settings = self.watermark_settings.get('font', {})
            font_size = max(1, int(font_settings.get('size', 40) * self.scale_factor))
            font.setPointSize(font_size)
            temp_painter.setFont(font)
            
            # 计算文本尺寸
            fm = temp_painter.fontMetrics()
            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()
            
            temp_painter.end()
            
            # 设置边界（考虑旋转）
            padding = 10
            self.watermark_bounds = QRect(
                self.watermark_pos.x() - text_width//2 - padding,
                self.watermark_pos.y() - text_height//2 - padding,
                text_width + 2*padding,
                text_height + 2*padding
            )

        else:
            # 图片水印边界计算
            image_path = self.watermark_settings.get('image_path')
            if image_path and os.path.exists(image_path):
                watermark = QPixmap(image_path)
                scale = self.watermark_settings.get('scale', 100) / 100 * self.scale_factor
                scaled_width = int(watermark.width() * scale)
                scaled_height = int(watermark.height() * scale)
                
                padding = 10
                self.watermark_bounds = QRect(
                    self.watermark_pos.x() - scaled_width//2 - padding,
                    self.watermark_pos.y() - scaled_height//2 - padding,
                    scaled_width + 2*padding,
                    scaled_height + 2*padding
                )

    
    def drawWatermarkBounds(self, painter):
        """绘制水印边界框"""
        if self.watermark_bounds.isEmpty():
            return
        
        # 保存当前状态
        painter.save()
        
        # 设置边界框样式
        pen = QPen(QColor(0, 120, 255), 2)  # 蓝色边框
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # 绘制边界框
        painter.drawRect(self.watermark_bounds)
        
        # 绘制控制点（四个角）
        control_size = 8
        painter.setBrush(QColor(0, 120, 255))
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        
        # 四个角的控制点
        corners = [
            self.watermark_bounds.topLeft(),
            self.watermark_bounds.topRight(),
            self.watermark_bounds.bottomLeft(),
            self.watermark_bounds.bottomRight()
        ]
        
        for corner in corners:
            painter.drawRect(
                corner.x() - control_size//2,
                corner.y() - control_size//2,
                control_size,
                control_size
            )
        
        # 恢复状态
        painter.restore()
     
    def drawTextWatermark(self, painter):
        """绘制文本水印
        
        Args:
            painter: QPainter对象
        """
        try:
            text = self.watermark_settings.get('text', '')
            if not text:
                return
        except Exception as e:
            return
        
        try:
            # 设置字体
            font = QFont()
            font_settings = self.watermark_settings.get('font', {})
            font_family = font_settings.get('family', 'Arial')
            
            # 检查字体是否存在
            font_path = os.path.join(os.environ['WINDIR'], 'Fonts', f'{font_family}.ttf')
            if not os.path.exists(font_path):
                font_path = os.path.join(os.environ['WINDIR'], 'Fonts', f'{font_family}.TTF')
            
            if not os.path.exists(font_path):
                # 如果找不到指定字体，使用微软雅黑
                font.setFamily('Microsoft YaHei')
            else:
                font.setFamily(font_family)
            
            # 设置字体大小
            font_size = max(1, int(font_settings.get('size', 40) * self.scale_factor))
            font.setPointSize(font_size)
            
            # 设置字体样式
            font.setBold(font_settings.get('bold', False))
            font.setItalic(font_settings.get('italic', False))
            painter.setFont(font)
        except Exception as e:
            # 使用安全的默认值
            default_font = QFont('Microsoft YaHei', 40)
            painter.setFont(default_font)
        
        try:
            # 设置颜色和透明度
            color = self.watermark_settings.get('color', '#000000')
            opacity = self.watermark_settings.get('opacity', 100)
            
            if isinstance(color, str):
                color = QColor(color)
            color.setAlpha(int(255 * opacity / 100))
            painter.setPen(color)
            
            # 计算文本尺寸
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()
            
            # 保存当前状态
            painter.save()
            
            # 移动到绘制位置并旋转
            painter.translate(self.watermark_pos)
            rotation = self.watermark_settings.get('rotation', 0)
            if rotation:
                painter.rotate(rotation)
            
            # 绘制文本（考虑中心点偏移）
            draw_x = int(-text_width/2)
            draw_y = int(text_height/2)
            painter.drawText(draw_x, draw_y, text)
            
            # 恢复状态
            painter.restore()
            
        except Exception as e:
            # 恢复画笔状态
            painter.restore()
            # 使用最基本的绘制方式
            painter.setPen(QColor('#000000'))
            painter.drawText(int(self.watermark_pos.x()), int(self.watermark_pos.y()), text)
    
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
        painter.drawPixmap(int(-watermark.width()/2), int(-watermark.height()/2), watermark)
        
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
            '上中': QPoint(width // 2, padding),
            '右上角': QPoint(width - padding, padding),
            '左中': QPoint(padding, height // 2),
            '中心': QPoint(width // 2, height // 2),
            '右中': QPoint(width - padding, height // 2),
            '左下角': QPoint(padding, height - padding),
            '下中': QPoint(width // 2, height - padding),
            '右下角': QPoint(width - padding, height - padding)
        }
        
        return positions.get(position, QPoint(width // 2, height // 2))
    
    def isValidWatermarkPosition(self, pos):
        """检查水印位置是否有效（在图片边界内）
        
        Args:
            pos: QPoint 水印位置
            
        Returns:
            bool: 位置是否有效
        """
        if not self.pixmap():
            return False
        
        pixmap_rect = self.pixmap().rect()

        
        # 检查位置是否在图片范围内
        if pixmap_rect.contains(pos):
            return True
        else:
            return False
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 如果有水印设置，允许在图片任意位置开始拖拽
            if self.watermark_settings and self.pixmap():
                self.dragging = True
                self.drag_start = event.pos()
                # 计算从点击位置到水印中心的偏移
                self.drag_offset = self.watermark_pos - event.pos()
                self.watermark_settings['position_custom'] = True
                self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.dragging:
            # 使用拖拽偏移计算新的水印位置
            new_pos = event.pos() + self.drag_offset
            
            # 检查边界限制
            if self.isValidWatermarkPosition(new_pos):
                self.watermark_pos = new_pos
                # 使用轻量级拖动预览
                self.updateDragPreview()
        else:
            # 检查鼠标是否悬停在水印上
            old_hover = self.hover_watermark
            self.hover_watermark = self.watermark_bounds.contains(event.pos())
            
            # 更新鼠标样式
            if self.hover_watermark:
                self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            
            # 如果悬停状态改变，更新预览
            if old_hover != self.hover_watermark:
                self.updatePreview()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.dragging = False
            # 恢复鼠标样式
            if self.hover_watermark:
                self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            # 最终更新预览
            self.updatePreview()