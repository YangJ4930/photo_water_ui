import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class ConfigManager:
    """配置管理器，负责水印模板的保存、加载和管理"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser("~"), ".photo_watermark")
        self.templates_dir = os.path.join(self.config_dir, "templates")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.last_settings_file = os.path.join(self.config_dir, "last_settings.json")
        
        # 确保配置目录存在
        self._ensure_directories()
        
    def _ensure_directories(self):
        """确保配置目录存在"""
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        
    def save_template(self, name: str, settings: Dict[str, Any]) -> bool:
        """保存水印模板
        
        Args:
            name: 模板名称
            settings: 水印设置字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            template_data = {
                'name': name,
                'created_at': datetime.now().isoformat(),
                'settings': settings
            }
            
            # 生成安全的文件名
            safe_name = self._sanitize_filename(name)
            template_file = os.path.join(self.templates_dir, f"{safe_name}.json")
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            print(f"保存模板失败: {e}")
            return False
            
    def load_template(self, name: str) -> Optional[Dict[str, Any]]:
        """加载水印模板
        
        Args:
            name: 模板名称
            
        Returns:
            Dict: 模板设置，如果加载失败返回None
        """
        try:
            safe_name = self._sanitize_filename(name)
            template_file = os.path.join(self.templates_dir, f"{safe_name}.json")
            
            if not os.path.exists(template_file):
                return None
                
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
                
            return template_data.get('settings')
            
        except Exception as e:
            print(f"加载模板失败: {e}")
            return None
            
    def get_template_list(self) -> List[Dict[str, str]]:
        """获取所有模板列表
        
        Returns:
            List: 模板信息列表，包含名称和创建时间
        """
        templates = []
        
        try:
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.json'):
                    template_file = os.path.join(self.templates_dir, filename)
                    
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        
                    templates.append({
                        'name': template_data.get('name', filename[:-5]),
                        'created_at': template_data.get('created_at', ''),
                        'filename': filename
                    })
                    
        except Exception as e:
            print(f"获取模板列表失败: {e}")
            
        # 按创建时间排序
        templates.sort(key=lambda x: x['created_at'], reverse=True)
        return templates
        
    def delete_template(self, name: str) -> bool:
        """删除水印模板
        
        Args:
            name: 模板名称
            
        Returns:
            bool: 删除是否成功
        """
        try:
            safe_name = self._sanitize_filename(name)
            template_file = os.path.join(self.templates_dir, f"{safe_name}.json")
            
            if os.path.exists(template_file):
                os.remove(template_file)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"删除模板失败: {e}")
            return False
            
    def rename_template(self, old_name: str, new_name: str) -> bool:
        """重命名模板
        
        Args:
            old_name: 原模板名称
            new_name: 新模板名称
            
        Returns:
            bool: 重命名是否成功
        """
        try:
            # 加载原模板
            settings = self.load_template(old_name)
            if settings is None:
                return False
                
            # 保存为新名称
            if self.save_template(new_name, settings):
                # 删除原模板
                return self.delete_template(old_name)
            else:
                return False
                
        except Exception as e:
            print(f"重命名模板失败: {e}")
            return False
            
    def save_last_settings(self, settings: Dict[str, Any]) -> bool:
        """保存最后使用的设置
        
        Args:
            settings: 水印设置字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            with open(self.last_settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
            
        except Exception as e:
            print(f"保存最后设置失败: {e}")
            return False
            
    def load_last_settings(self) -> Optional[Dict[str, Any]]:
        """加载最后使用的设置
        
        Returns:
            Dict: 最后的设置，如果不存在返回None
        """
        try:
            if os.path.exists(self.last_settings_file):
                with open(self.last_settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
            
        except Exception as e:
            print(f"加载最后设置失败: {e}")
            return None
            
    def get_default_template(self) -> Dict[str, Any]:
        """获取默认模板设置
        
        Returns:
            Dict: 默认水印设置
        """
        return {
            'text': '水印文字',
            'font_family': 'Arial',
            'font_size': 36,
            'font_bold': False,
            'font_italic': False,
            'color': '#FFFFFF',
            'opacity': 80,
            'position': 'bottom_right',
            'position_custom': False,
            'custom_x': 0,
            'custom_y': 0,
            'rotation': 0,
            'image_path': '',
            'image_size': 100,
            'watermark_type': 'text'  # 'text' 或 'image'
        }
        
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除不安全字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 安全的文件名
        """
        # 移除或替换不安全的字符
        unsafe_chars = '<>:"/\\|?*'
        safe_name = filename
        
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')
            
        # 限制长度
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
            
        return safe_name