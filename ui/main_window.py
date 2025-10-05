from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QSpinBox, QLineEdit, QPushButton, QFileDialog, QSplitter, QMenuBar,
    QMenu, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from ui.image_list_widget import ImageListWidget
from ui.watermark_settings import WatermarkSettings
from ui.watermark_preview import WatermarkPreview
from ui.template_manager import TemplateManagerDialog
from utils.image_processor import ImageProcessor
from utils.config_manager import ConfigManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('智能水印文件管理系统')
        self.setMinimumSize(1200, 800)
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建主部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # 创建左侧面板（图片列表和控制面板）
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 创建图片列表
        self.image_list = ImageListWidget()
        self.image_list.itemSelectionChanged.connect(self.on_image_selected)
        left_layout.addWidget(self.image_list)
        
        # 创建控制面板
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        
        # 输出格式选择
        format_layout = QHBoxLayout()
        format_label = QLabel('输出格式：')
        self.format_combo = QComboBox()
        self.format_combo.addItems(['JPEG', 'PNG'])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        control_layout.addLayout(format_layout)
        
        # JPEG质量设置
        quality_layout = QHBoxLayout()
        quality_label = QLabel('JPEG质量：')
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(85)
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_spin)
        control_layout.addLayout(quality_layout)
        
        # 文件命名规则
        naming_layout = QVBoxLayout()
        prefix_layout = QHBoxLayout()
        prefix_label = QLabel('文件名前缀：')
        self.prefix_edit = QLineEdit()
        prefix_layout.addWidget(prefix_label)
        prefix_layout.addWidget(self.prefix_edit)
        naming_layout.addLayout(prefix_layout)
        
        suffix_layout = QHBoxLayout()
        suffix_label = QLabel('文件名后缀：')
        self.suffix_edit = QLineEdit()
        suffix_layout.addWidget(suffix_label)
        suffix_layout.addWidget(self.suffix_edit)
        naming_layout.addLayout(suffix_layout)
        control_layout.addLayout(naming_layout)
        
        # 导入导出按钮
        button_layout = QVBoxLayout()
        
        # 第一行：导入导出按钮
        io_layout = QHBoxLayout()
        self.import_button = QPushButton('导入图片')
        self.export_button = QPushButton('导出图片')
        self.import_button.clicked.connect(self.import_images)
        self.export_button.clicked.connect(self.export_images)
        io_layout.addWidget(self.import_button)
        io_layout.addWidget(self.export_button)
        button_layout.addLayout(io_layout)
        
        # 第二行：模板功能按钮
        template_layout = QHBoxLayout()
        self.save_template_button = QPushButton('保存模板')
        self.load_template_button = QPushButton('加载模板')
        self.manage_template_button = QPushButton('管理模板')
        
        self.save_template_button.clicked.connect(self.save_current_template)
        self.load_template_button.clicked.connect(self.show_template_manager)
        self.manage_template_button.clicked.connect(self.show_template_manager)
        
        template_layout.addWidget(self.save_template_button)
        template_layout.addWidget(self.load_template_button)
        template_layout.addWidget(self.manage_template_button)
        button_layout.addLayout(template_layout)
        
        control_layout.addLayout(button_layout)
        
        left_layout.addWidget(control_panel)
        
        # 创建右侧面板（预览和水印设置）
        right_panel = QSplitter(Qt.Orientation.Vertical)
        
        # 创建预览区域
        self.preview = WatermarkPreview()
        right_panel.addWidget(self.preview)
        
        # 创建水印设置面板
        self.watermark_settings = WatermarkSettings()
        self.watermark_settings.settingsChanged.connect(self.preview.setWatermarkSettings)
        right_panel.addWidget(self.watermark_settings)
        
        # 设置分割器比例
        right_panel.setStretchFactor(0, 2)  # 预览区域占2
        right_panel.setStretchFactor(1, 1)  # 水印设置占1
        
        # 添加左右面板到主布局
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 1)  # 左侧面板占1
        main_splitter.setStretchFactor(1, 2)  # 右侧面板占2
        main_layout.addWidget(main_splitter)
        
        # 初始化图片处理器
        self.image_processor = ImageProcessor()
        
        # 加载上次的设置
        self.load_last_settings()
    
    def import_images(self):
        """导入图片"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter('Images (*.jpg *.jpeg *.png *.bmp *.tiff *.tif)')
        
        if file_dialog.exec():
            filenames = file_dialog.selectedFiles()
            for filename in filenames:
                if self.image_processor.is_supported_format(filename):
                    self.image_list.add_image(filename)
    
    def export_images(self):
        """导出图片"""
        if not self.image_list.count():
            return
        
        # 选择导出目录
        export_dir = QFileDialog.getExistingDirectory(self, '选择导出目录')
        if not export_dir:
            return
        
        # 收集所有图片路径
        image_paths = []
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            image_paths.append(item.data(Qt.ItemDataRole.UserRole))
        
        # 导出设置
        settings = {
            'format': self.format_combo.currentText(),
            'quality': self.quality_spin.value(),
            'prefix': self.prefix_edit.text(),
            'suffix': self.suffix_edit.text(),
            'watermark': self.watermark_settings.current_settings
        }
        
        # 执行导出
        self.image_processor.export_images(image_paths, export_dir, settings)
    
    def on_image_selected(self):
        """处理图片选择变化"""
        selected_items = self.image_list.selectedItems()
        if selected_items:
            image_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.preview.setImage(image_path)
            
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        import_action = QAction('导入图片', self)
        import_action.triggered.connect(self.import_images)
        file_menu.addAction(import_action)
        
        export_action = QAction('导出图片', self)
        export_action.triggered.connect(self.export_images)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 模板菜单
        template_menu = menubar.addMenu('模板')
        
        save_template_action = QAction('保存当前模板', self)
        save_template_action.triggered.connect(self.save_current_template)
        template_menu.addAction(save_template_action)
        
        load_template_action = QAction('加载模板', self)
        load_template_action.triggered.connect(self.show_template_manager)
        template_menu.addAction(load_template_action)
        
        manage_template_action = QAction('管理模板', self)
        manage_template_action.triggered.connect(self.show_template_manager)
        template_menu.addAction(manage_template_action)
        
        template_menu.addSeparator()
        
        reset_action = QAction('重置为默认设置', self)
        reset_action.triggered.connect(self.reset_to_default)
        template_menu.addAction(reset_action)
        
    def save_current_template(self):
        """保存当前水印设置为模板"""
        # 获取模板名称
        name, ok = QInputDialog.getText(
            self, '保存模板', '请输入模板名称:'
        )
        
        if ok and name.strip():
            name = name.strip()
            settings = self.watermark_settings.current_settings
            
            if self.config_manager.save_template(name, settings):
                QMessageBox.information(self, '成功', f'模板 "{name}" 已保存')
            else:
                QMessageBox.warning(self, '错误', '保存模板失败')
                
    def show_template_manager(self):
        """显示模板管理对话框"""
        dialog = TemplateManagerDialog(self)
        dialog.template_selected.connect(self.load_template_settings)
        dialog.exec()
        
    def load_template_settings(self, settings):
        """加载模板设置"""
        self.watermark_settings.load_settings(settings)
        
    def reset_to_default(self):
        """重置为默认设置"""
        reply = QMessageBox.question(
            self, '确认重置', 
            '确定要重置为默认设置吗？当前设置将丢失。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            default_settings = self.config_manager.get_default_template()
            self.watermark_settings.load_settings(default_settings)
            
    def load_last_settings(self):
        """加载上次的设置"""
        settings = self.config_manager.load_last_settings()
        if settings:
            self.watermark_settings.load_settings(settings)
        else:
            # 如果没有上次设置，加载默认设置
            default_settings = self.config_manager.get_default_template()
            self.watermark_settings.load_settings(default_settings)
            
    def closeEvent(self, event):
        """程序关闭时保存当前设置"""
        settings = self.watermark_settings.current_settings
        self.config_manager.save_last_settings(settings)
        event.accept()