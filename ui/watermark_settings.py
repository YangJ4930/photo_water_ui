from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QSpinBox, QPushButton,
                             QFontComboBox, QColorDialog, QFileDialog, QSlider,
                             QGroupBox, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from pathlib import Path

class WatermarkSettings(QWidget):
    # 设置变更信号
    settingsChanged = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_settings = {
            'type': '文本水印',
            'text': '',
            'font': {
                'family': 'Arial',
                'size': 40,
                'bold': False,
                'italic': False
            },
            'color': '#000000',
            'opacity': 100,
            'position': '中心',
            'position_custom': False,
            'rotation': 0
        }
    
    def initUI(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 水印类型选择
        type_group = QGroupBox('水印类型')
        type_layout = QHBoxLayout()
        self.type_group = QButtonGroup(self)
        
        text_radio = QRadioButton('文本水印')
        image_radio = QRadioButton('图片水印')
        text_radio.setChecked(True)
        
        self.type_group.addButton(text_radio, 0)
        self.type_group.addButton(image_radio, 1)
        self.type_group.buttonClicked.connect(self.onTypeChanged)
        
        type_layout.addWidget(text_radio)
        type_layout.addWidget(image_radio)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # 文本水印设置
        self.text_settings = QGroupBox('文本水印设置')
        text_layout = QVBoxLayout()
        
        # 文本输入
        text_input_layout = QHBoxLayout()
        text_label = QLabel('文本：')
        self.text_edit = QLineEdit()
        self.text_edit.setMaxLength(100)  # 限制最大输入长度
        self.text_edit.setToolTip('最大输入长度：100字符')
        self.text_edit.textChanged.connect(self.onTextChanged)
        text_input_layout.addWidget(text_label)
        text_input_layout.addWidget(self.text_edit)
        text_layout.addLayout(text_input_layout)
        
        # 字体设置
        font_layout = QHBoxLayout()
        font_label = QLabel('字体：')
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.onSettingChanged)
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_combo)
        text_layout.addLayout(font_layout)
        
        # 字号设置
        size_layout = QHBoxLayout()
        size_label = QLabel('字号：')
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 200)  # 最小字号改为1
        self.size_spin.setValue(40)
        self.size_spin.setToolTip('字体大小范围：1-200')
        self.size_spin.valueChanged.connect(self.onSettingChanged)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_spin)
        text_layout.addLayout(size_layout)
        
        # 颜色选择
        color_layout = QHBoxLayout()
        color_label = QLabel('颜色：')
        self.color_button = QPushButton()
        self.color_button.setStyleSheet('background-color: #000000;')
        self.color_button.setFixedSize(30, 30)
        self.color_button.clicked.connect(self.showColorDialog)
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        text_layout.addLayout(color_layout)
        
        self.text_settings.setLayout(text_layout)
        layout.addWidget(self.text_settings)
        
        # 图片水印设置
        self.image_settings = QGroupBox('图片水印设置')
        self.image_settings.setVisible(False)
        image_layout = QVBoxLayout()
        
        # 图片选择
        image_select_layout = QHBoxLayout()
        self.image_path_label = QLabel('未选择图片')
        select_image_button = QPushButton('选择图片')
        self.remove_image_button = QPushButton('删除图片')
        self.remove_image_button.setEnabled(False)  # 初始状态禁用
        select_image_button.clicked.connect(self.selectWatermarkImage)
        self.remove_image_button.clicked.connect(self.removeWatermarkImage)
        image_select_layout.addWidget(self.image_path_label)
        image_select_layout.addWidget(select_image_button)
        image_select_layout.addWidget(self.remove_image_button)
        image_layout.addLayout(image_select_layout)
        
        # 缩放设置
        scale_layout = QHBoxLayout()
        scale_label = QLabel('缩放：')
        self.scale_spin = QSpinBox()
        self.scale_spin.setRange(1, 200)
        self.scale_spin.setValue(100)
        self.scale_spin.setSuffix('%')
        self.scale_spin.valueChanged.connect(self.onSettingChanged)
        scale_layout.addWidget(scale_label)
        scale_layout.addWidget(self.scale_spin)
        image_layout.addLayout(scale_layout)
        
        self.image_settings.setLayout(image_layout)
        layout.addWidget(self.image_settings)
        
        # 通用设置
        common_group = QGroupBox('通用设置')
        common_layout = QVBoxLayout()
        
        # 透明度设置
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel('透明度：')
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_value = QLabel('100%')
        self.opacity_slider.valueChanged.connect(self.onOpacityChanged)
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_value)
        common_layout.addLayout(opacity_layout)
        
        # 位置设置
        position_layout = QVBoxLayout()
        position_label = QLabel('位置：')
        
        # 九宫格位置选择
        grid_layout = QHBoxLayout()
        self.position_combo = QComboBox()
        self.position_combo.addItems([
            '左上角', '上中', '右上角',
            '左中', '中心', '右中', 
            '左下角', '下中', '右下角'
        ])
        self.position_combo.setCurrentText('中心')
        self.position_combo.currentTextChanged.connect(self.onSettingChanged)
        
        # 添加九宫格快速选择按钮
        from PyQt6.QtWidgets import QGridLayout, QFrame
        grid_frame = QFrame()
        grid_frame.setFrameStyle(QFrame.Shape.Box)
        grid_frame.setMaximumSize(120, 90)
        
        self.grid_buttons_layout = QGridLayout(grid_frame)
        self.grid_buttons_layout.setSpacing(2)
        
        # 创建九宫格按钮
        positions = [
            ('左上角', 0, 0), ('上中', 0, 1), ('右上角', 0, 2),
            ('左中', 1, 0), ('中心', 1, 1), ('右中', 1, 2),
            ('左下角', 2, 0), ('下中', 2, 1), ('右下角', 2, 2)
        ]
        
        self.grid_buttons = {}
        for pos_name, row, col in positions:
            btn = QPushButton()
            btn.setFixedSize(35, 25)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:pressed {
                    background-color: #0078d4;
                }
            """)
            btn.clicked.connect(lambda checked, pos=pos_name: self.onGridPositionClicked(pos))
            self.grid_buttons_layout.addWidget(btn, row, col)
            self.grid_buttons[pos_name] = btn
        
        grid_layout.addWidget(self.position_combo)
        grid_layout.addWidget(grid_frame)
        
        position_layout.addWidget(position_label)
        position_layout.addLayout(grid_layout)
        common_layout.addLayout(position_layout)
        
        # 旋转设置
        rotation_layout = QVBoxLayout()
        rotation_label = QLabel('旋转：')
        
        # 旋转滑块
        rotation_slider_layout = QHBoxLayout()
        self.rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.rotation_slider.setRange(0, 359)
        self.rotation_slider.setValue(0)
        self.rotation_slider.valueChanged.connect(self.onRotationSliderChanged)
        
        # 旋转输入框
        self.rotation_spin = QSpinBox()
        self.rotation_spin.setRange(0, 359)
        self.rotation_spin.setSuffix('°')
        self.rotation_spin.valueChanged.connect(self.onRotationSpinChanged)
        
        rotation_slider_layout.addWidget(self.rotation_slider)
        rotation_slider_layout.addWidget(self.rotation_spin)
        
        rotation_layout.addWidget(rotation_label)
        rotation_layout.addLayout(rotation_slider_layout)
        common_layout.addLayout(rotation_layout)
        
        common_group.setLayout(common_layout)
        layout.addWidget(common_group)
        
        # 添加弹性空间
        layout.addStretch()
    
    def onTypeChanged(self, button):
        """处理水印类型变化"""
        is_text = button.text() == '文本水印'
        self.text_settings.setVisible(is_text)
        self.image_settings.setVisible(not is_text)
        self.current_settings['type'] = button.text()
        self.settingsChanged.emit(self.current_settings)
    
    def onTextChanged(self, text):
        """处理文本输入变化"""
        try:
            print(f"文本输入: {text}")
            self.current_settings['text'] = text
            # 只有当文本不为空时才发送信号，避免频繁更新
            if text.strip():
                self.settingsChanged.emit(self.current_settings)
        except Exception as e:
            print(f"处理文本输入时出错: {e}")
            # 发生错误时重置文本
            self.text_edit.setText(self.current_settings.get('text', ''))
    
    def onSettingChanged(self):
        """处理设置变化"""
        try:
            if self.current_settings['type'] == '文本水印':
                self.current_settings.update({
                    'font': {
                        'family': self.font_combo.currentFont().family(),
                        'size': self.size_spin.value(),
                        'bold': self.font_combo.currentFont().bold(),
                        'italic': self.font_combo.currentFont().italic()
                    }
                })
        except Exception as e:
            print(f"更新设置时出错: {e}")
            return
        else:
            self.current_settings['scale'] = self.scale_spin.value()
        
        self.current_settings.update({
            'position': self.position_combo.currentText(),
            'rotation': self.rotation_spin.value()
        })
        
        self.settingsChanged.emit(self.current_settings)
    
    def onOpacityChanged(self, value):
        """处理透明度变化"""
        self.opacity_value.setText(f'{value}%')
        self.current_settings['opacity'] = value
        self.settingsChanged.emit(self.current_settings)
    
    def onRotationSliderChanged(self, value):
        """处理旋转滑块变化"""
        # 同步更新输入框
        self.rotation_spin.blockSignals(True)
        self.rotation_spin.setValue(value)
        self.rotation_spin.blockSignals(False)
        
        # 更新设置
        self.current_settings['rotation'] = value
        self.settingsChanged.emit(self.current_settings)
    
    def onRotationSpinChanged(self, value):
        """处理旋转输入框变化"""
        # 同步更新滑块
        self.rotation_slider.blockSignals(True)
        self.rotation_slider.setValue(value)
        self.rotation_slider.blockSignals(False)
        
        # 更新设置
        self.current_settings['rotation'] = value
        self.settingsChanged.emit(self.current_settings)
    
    def onGridPositionClicked(self, position):
        """处理九宫格位置按钮点击"""
        # 更新下拉框选择
        self.position_combo.blockSignals(True)
        self.position_combo.setCurrentText(position)
        self.position_combo.blockSignals(False)
        
        # 更新按钮样式
        for pos_name, btn in self.grid_buttons.items():
            if pos_name == position:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0078d4;
                        border: 1px solid #005a9e;
                        border-radius: 3px;
                        color: white;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f0f0f0;
                        border: 1px solid #ccc;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                    QPushButton:pressed {
                        background-color: #0078d4;
                    }
                """)
        
        # 更新设置
        self.current_settings['position'] = position
        self.current_settings['position_custom'] = False
        self.settingsChanged.emit(self.current_settings)
     
    def showColorDialog(self):
        """显示颜色选择对话框"""
        color = QColorDialog.getColor(QColor(self.current_settings['color']))
        if color.isValid():
            self.current_settings['color'] = color.name()
            self.color_button.setStyleSheet(f'background-color: {color.name()};')
            self.settingsChanged.emit(self.current_settings)
    
    def selectWatermarkImage(self):
        """选择水印图片"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter('Images (*.png *.jpg *.jpeg *.bmp *.gif)')
        
        if file_dialog.exec():
            image_path = file_dialog.selectedFiles()[0]
            self.current_settings['image_path'] = image_path
            self.image_path_label.setText(Path(image_path).name)
            self.remove_image_button.setEnabled(True)  # 启用删除按钮
            self.settingsChanged.emit(self.current_settings)
            
    def removeWatermarkImage(self):
        """删除水印图片"""
        self.current_settings['image_path'] = ''
        self.image_path_label.setText('未选择图片')
        self.remove_image_button.setEnabled(False)  # 禁用删除按钮
        self.settingsChanged.emit(self.current_settings)
            
    def load_settings(self, settings):
        """从模板加载设置"""
        try:
            # 更新当前设置
            self.current_settings.update(settings)
            
            # 更新UI控件
            if 'watermark_type' in settings:
                if settings['watermark_type'] == 'text':
                    self.type_group.button(0).setChecked(True)
                    self.onTypeChanged(self.type_group.button(0))
                else:
                    self.type_group.button(1).setChecked(True)
                    self.onTypeChanged(self.type_group.button(1))
                    
            # 文本设置
            if 'text' in settings:
                self.text_edit.setText(settings['text'])
                
            if 'font_family' in settings:
                self.font_combo.setCurrentFont(QFont(settings['font_family']))
                
            if 'font_size' in settings:
                self.size_spin.setValue(settings['font_size'])
                
            if 'color' in settings:
                self.color_button.setStyleSheet(f'background-color: {settings["color"]};')
                
            if 'position' in settings:
                position_map = {
                    'top_left': '左上角',
                    'top_center': '顶部居中', 
                    'top_right': '右上角',
                    'center_left': '左侧居中',
                    'center': '中心',
                    'center_right': '右侧居中',
                    'bottom_left': '左下角',
                    'bottom_center': '底部居中',
                    'bottom_right': '右下角'
                }
                position_text = position_map.get(settings['position'], '中心')
                index = self.position_combo.findText(position_text)
                if index >= 0:
                    self.position_combo.setCurrentIndex(index)
                    
            # 图片水印设置
            if 'image_path' in settings and settings['image_path']:
                self.image_path_label.setText(Path(settings['image_path']).name)
                self.remove_image_button.setEnabled(True)
            else:
                self.image_path_label.setText('未选择图片')
                self.remove_image_button.setEnabled(False)
                
            # 发送设置变更信号
            self.settingsChanged.emit(self.current_settings)
            
        except Exception as e:
            print(f"加载设置失败: {e}")