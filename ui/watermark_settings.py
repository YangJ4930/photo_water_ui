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
        select_image_button.clicked.connect(self.selectWatermarkImage)
        image_select_layout.addWidget(self.image_path_label)
        image_select_layout.addWidget(select_image_button)
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
        position_layout = QHBoxLayout()
        position_label = QLabel('位置：')
        self.position_combo = QComboBox()
        self.position_combo.addItems(['左上角', '右上角', '左下角', '右下角', '中心'])
        self.position_combo.setCurrentText('中心')
        self.position_combo.currentTextChanged.connect(self.onSettingChanged)
        position_layout.addWidget(position_label)
        position_layout.addWidget(self.position_combo)
        common_layout.addLayout(position_layout)
        
        # 旋转设置
        rotation_layout = QHBoxLayout()
        rotation_label = QLabel('旋转：')
        self.rotation_spin = QSpinBox()
        self.rotation_spin.setRange(0, 359)
        self.rotation_spin.setSuffix('°')
        self.rotation_spin.valueChanged.connect(self.onSettingChanged)
        rotation_layout.addWidget(rotation_label)
        rotation_layout.addWidget(self.rotation_spin)
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
        file_dialog.setNameFilter('Images (*.png)')
        
        if file_dialog.exec():
            image_path = file_dialog.selectedFiles()[0]
            self.current_settings['image_path'] = image_path
            self.image_path_label.setText(Path(image_path).name)
            self.settingsChanged.emit(self.current_settings)