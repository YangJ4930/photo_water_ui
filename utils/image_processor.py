from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from PyQt6.QtGui import QImage
import os

class ImageProcessor:
    def __init__(self):
        # 支持的图片格式
        self.supported_formats = {
            'JPEG': ('.jpg', '.jpeg'),
            'PNG': ('.png'),
            'BMP': ('.bmp'),
            'TIFF': ('.tiff', '.tif')
        }
    
    def create_thumbnail(self, image_path: str, size: tuple = (100, 100)) -> QImage:
        """创建图片缩略图
        
        Args:
            image_path: 图片路径
            size: 缩略图大小，默认100x100
            
        Returns:
            QImage对象，如果失败返回None
        """
        try:
            with Image.open(image_path) as img:
                # 生成缩略图
                img.thumbnail(size)
                # 转换为RGB模式（如果是RGBA，保留透明通道）
                if img.mode == 'RGBA':
                    data = img.tobytes('raw', 'RGBA')
                    return QImage(data, img.size[0], img.size[1], QImage.Format.Format_RGBA8888)
                else:
                    img = img.convert('RGB')
                    data = img.tobytes('raw', 'RGB')
                    return QImage(data, img.size[0], img.size[1], QImage.Format.Format_RGB888)
        except Exception as e:
            print(f"创建缩略图失败: {e}")
            return None
    
    def apply_watermark(self, image: Image.Image, watermark_settings: dict) -> Image.Image:
        """应用水印到图片
        
        Args:
            image: PIL Image对象
            watermark_settings: 水印设置
            
        Returns:
            处理后的PIL Image对象
        """
        # 创建一个透明图层用于绘制水印
        watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 获取水印位置
        position = watermark_settings.get('position', '中心')
        x, y = self._calculate_position(position, image.size)
        
        # 根据水印类型处理
        if watermark_settings.get('type') == '文本水印':
            # 处理文本水印
            text = watermark_settings.get('text', '')
            if text:
                try:
                    # 获取字体设置
                    font_family = watermark_settings.get('font', {}).get('family', 'Arial')
                    print(f"正在处理文本水印，字体: {font_family}")
                    
                    # 确保字体大小有效
                    font_size = max(1, watermark_settings.get('font', {}).get('size', 40))
                    print(f"字体大小: {font_size}")
                    
                    # Windows系统字体目录
                    font_path = os.path.join(os.environ['WINDIR'], 'Fonts', f'{font_family}.ttf')
                    if not os.path.exists(font_path):
                        # 尝试 .TTF 扩展名
                        font_path = os.path.join(os.environ['WINDIR'], 'Fonts', f'{font_family}.TTF')
                    
                    if os.path.exists(font_path):
                        print(f"使用字体文件: {font_path}")
                        font = ImageFont.truetype(font_path, font_size)
                    else:
                        # 如果找不到指定字体，使用微软雅黑
                        print(f"找不到字体 {font_family}，使用微软雅黑替代")
                        fallback_font = os.path.join(os.environ['WINDIR'], 'Fonts', 'msyh.ttc')
                        font = ImageFont.truetype(fallback_font, font_size)
                    
                    # 获取颜色设置
                    color = watermark_settings.get('color', (0, 0, 0))
                    if isinstance(color, str):
                        color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    opacity = int(255 * watermark_settings.get('opacity', 100) / 100)
                    print(f"颜色: {color}, 透明度: {opacity}")
                    
                    # 绘制文本
                    print(f"绘制文本位置: ({x}, {y})")
                    draw.text((x, y), text, font=font, fill=color + (opacity,))
                    print("文本水印绘制完成")
                    
                except Exception as e:
                    print(f"应用文本水印时出错: {e}")
                    # 使用最基本的设置
                    font = ImageFont.load_default()
                    draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))
        else:
            # 处理图片水印
            image_path = watermark_settings.get('image_path')
            if image_path and Path(image_path).exists():
                with Image.open(image_path) as watermark_img:
                    # 调整大小
                    scale = watermark_settings.get('scale', 100) / 100
                    new_size = tuple(int(dim * scale) for dim in watermark_img.size)
                    watermark_img = watermark_img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # 调整位置（考虑图片大小的偏移）
                    x -= watermark_img.width // 2
                    y -= watermark_img.height // 2
                    
                    # 粘贴水印图片
                    watermark_layer.paste(watermark_img, (x, y), watermark_img)
        
        # 应用旋转
        rotation = watermark_settings.get('rotation', 0)
        if rotation:
            watermark_layer = watermark_layer.rotate(rotation, expand=True)
        
        # 合并水印层和原图
        return Image.alpha_composite(image.convert('RGBA'), watermark_layer)
    
    def export_images(self, image_paths: list, export_dir: str, settings: dict):
        """导出图片
        
        Args:
            image_paths: 图片路径列表
            export_dir: 导出目录
            settings: 导出设置，包含：
                - format: 输出格式 ('JPEG' 或 'PNG')
                - quality: JPEG质量 (0-100)
                - prefix: 文件名前缀
                - suffix: 文件名后缀
                - watermark: 水印设置
        """
        os.makedirs(export_dir, exist_ok=True)
        
        for image_path in image_paths:
            try:
                # 打开原图
                with Image.open(image_path) as img:
                    # 应用水印
                    if settings.get('watermark'):
                        img = self.apply_watermark(img, settings['watermark'])
                    
                    # 处理文件名
                    original_name = Path(image_path).stem
                    new_name = f"{settings['prefix']}{original_name}{settings['suffix']}"
                    
                    # 设置输出格式和扩展名
                    output_format = settings['format']
                    ext = '.jpg' if output_format == 'JPEG' else '.png'
                    output_path = str(Path(export_dir) / f"{new_name}{ext}")
                    
                    # 如果输出格式是JPEG，转换为RGB模式
                    if output_format == 'JPEG':
                        img = img.convert('RGB')
                    
                    # 保存图片
                    save_params = {}
                    if output_format == 'JPEG':
                        save_params['quality'] = settings['quality']
                    
                    img.save(output_path, output_format, **save_params)
                    
            except Exception as e:
                print(f"导出图片失败 {image_path}: {e}")
    
    def _calculate_position(self, position: str, image_size: tuple) -> tuple:
        """计算水印位置
        
        Args:
            position: 位置名称
            image_size: 图片尺寸
            
        Returns:
            (x, y) 坐标元组
        """
        width, height = image_size
        padding = 50  # 边距
        
        positions = {
            '左上角': (padding, padding),
            '右上角': (width - padding, padding),
            '左下角': (padding, height - padding),
            '右下角': (width - padding, height - padding),
            '中心': (width // 2, height // 2)
        }
        
        return positions.get(position, (width // 2, height // 2))
    
    def is_supported_format(self, file_path: str) -> bool:
        """检查文件是否为支持的图片格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否支持
        """
        ext = Path(file_path).suffix.lower()
        return any(ext in exts for exts in self.supported_formats.values())