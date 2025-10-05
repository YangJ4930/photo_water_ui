from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMessageBox, QInputDialog, QWidget, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from utils.config_manager import ConfigManager
from typing import Dict, Any, Optional

class TemplateManagerDialog(QDialog):
    """模板管理对话框"""
    
    # 信号：模板被选择加载
    template_selected = pyqtSignal(dict)  # 发送模板设置
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self.current_template = None
        
        self.setWindowTitle("水印模板管理")
        self.setModal(True)
        self.resize(600, 400)
        
        self.setup_ui()
        self.load_templates()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("水印模板管理")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 主要内容区域
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧：模板列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        list_label = QLabel("已保存的模板:")
        list_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(list_label)
        
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self.on_template_selected)
        self.template_list.itemDoubleClicked.connect(self.on_template_double_clicked)
        left_layout.addWidget(self.template_list)
        
        splitter.addWidget(left_widget)
        
        # 右侧：模板详情和操作按钮
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 模板详情
        details_label = QLabel("模板详情:")
        details_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_layout.addWidget(details_label)
        
        self.details_label = QLabel("请选择一个模板查看详情")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                min-height: 100px;
            }
        """)
        right_layout.addWidget(self.details_label)
        
        # 操作按钮
        button_layout = QVBoxLayout()
        
        self.load_button = QPushButton("加载模板")
        self.load_button.setEnabled(False)
        self.load_button.clicked.connect(self.load_selected_template)
        button_layout.addWidget(self.load_button)
        
        self.rename_button = QPushButton("重命名")
        self.rename_button.setEnabled(False)
        self.rename_button.clicked.connect(self.rename_selected_template)
        button_layout.addWidget(self.rename_button)
        
        self.delete_button = QPushButton("删除")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_selected_template)
        self.delete_button.setStyleSheet("QPushButton { color: #d32f2f; }")
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        right_layout.addLayout(button_layout)
        
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setSizes([300, 300])
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        
        refresh_button = QPushButton("刷新列表")
        refresh_button.clicked.connect(self.load_templates)
        bottom_layout.addWidget(refresh_button)
        
        bottom_layout.addStretch()
        
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        bottom_layout.addWidget(close_button)
        
        layout.addLayout(bottom_layout)
        
    def load_templates(self):
        """加载模板列表"""
        self.template_list.clear()
        templates = self.config_manager.get_template_list()
        
        if not templates:
            item = QListWidgetItem("暂无保存的模板")
            item.setFlags(Qt.ItemFlag.NoItemFlags)  # 不可选择
            self.template_list.addItem(item)
            return
            
        for template in templates:
            item = QListWidgetItem()
            item.setText(template['name'])
            item.setData(Qt.ItemDataRole.UserRole, template)
            self.template_list.addItem(item)
            
    def on_template_selected(self, item: QListWidgetItem):
        """模板被选中时的处理"""
        template_info = item.data(Qt.ItemDataRole.UserRole)
        if not template_info:
            return
            
        self.current_template = template_info
        
        # 加载模板设置
        settings = self.config_manager.load_template(template_info['name'])
        if settings:
            self.show_template_details(template_info, settings)
            
        # 启用操作按钮
        self.load_button.setEnabled(True)
        self.rename_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        
    def on_template_double_clicked(self, item: QListWidgetItem):
        """双击模板时直接加载"""
        self.on_template_selected(item)
        self.load_selected_template()
        
    def show_template_details(self, template_info: Dict, settings: Dict[str, Any]):
        """显示模板详情"""
        details = f"""<b>模板名称:</b> {template_info['name']}<br>
<b>创建时间:</b> {template_info['created_at'][:19].replace('T', ' ')}<br><br>

<b>水印设置:</b><br>"""
        
        if settings.get('watermark_type') == 'text':
            details += f"""• 类型: 文字水印<br>
• 文字内容: {settings.get('text', '')}<br>
• 字体: {settings.get('font_family', 'Arial')}<br>
• 字体大小: {settings.get('font_size', 36)}px<br>
• 颜色: {settings.get('color', '#FFFFFF')}<br>
• 透明度: {settings.get('opacity', 80)}%<br>"""
        else:
            details += f"""• 类型: 图片水印<br>
• 图片路径: {settings.get('image_path', '')}<br>
• 图片大小: {settings.get('image_size', 100)}%<br>
• 透明度: {settings.get('opacity', 80)}%<br>"""
            
        details += f"""• 位置: {self.get_position_text(settings)}<br>
• 旋转角度: {settings.get('rotation', 0)}°<br>"""
        
        self.details_label.setText(details)
        
    def get_position_text(self, settings: Dict[str, Any]) -> str:
        """获取位置描述文本"""
        if settings.get('position_custom', False):
            return f"自定义 ({settings.get('custom_x', 0)}, {settings.get('custom_y', 0)})"
        else:
            position_map = {
                'top_left': '左上角',
                'top_center': '顶部居中',
                'top_right': '右上角',
                'center_left': '左侧居中',
                'center': '居中',
                'center_right': '右侧居中',
                'bottom_left': '左下角',
                'bottom_center': '底部居中',
                'bottom_right': '右下角'
            }
            return position_map.get(settings.get('position', 'bottom_right'), '未知位置')
            
    def load_selected_template(self):
        """加载选中的模板"""
        if not self.current_template:
            return
            
        settings = self.config_manager.load_template(self.current_template['name'])
        if settings:
            self.template_selected.emit(settings)
            QMessageBox.information(self, "成功", f"模板 '{self.current_template['name']}' 已加载")
            self.close()
        else:
            QMessageBox.warning(self, "错误", "加载模板失败")
            
    def rename_selected_template(self):
        """重命名选中的模板"""
        if not self.current_template:
            return
            
        old_name = self.current_template['name']
        new_name, ok = QInputDialog.getText(
            self, "重命名模板", "请输入新的模板名称:", text=old_name
        )
        
        if ok and new_name.strip():
            new_name = new_name.strip()
            if new_name != old_name:
                if self.config_manager.rename_template(old_name, new_name):
                    QMessageBox.information(self, "成功", f"模板已重命名为 '{new_name}'")
                    self.load_templates()
                else:
                    QMessageBox.warning(self, "错误", "重命名模板失败")
                    
    def delete_selected_template(self):
        """删除选中的模板"""
        if not self.current_template:
            return
            
        name = self.current_template['name']
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除模板 '{name}' 吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.config_manager.delete_template(name):
                QMessageBox.information(self, "成功", f"模板 '{name}' 已删除")
                self.load_templates()
                self.current_template = None
                self.details_label.setText("请选择一个模板查看详情")
                
                # 禁用操作按钮
                self.load_button.setEnabled(False)
                self.rename_button.setEnabled(False)
                self.delete_button.setEnabled(False)
            else:
                QMessageBox.warning(self, "错误", "删除模板失败")