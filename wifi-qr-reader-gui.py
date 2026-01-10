#!/usr/bin/env python3
# WiFi QR Reader - Leitor de QR Code de WiFi
# Autor: @marbleceo
# GitHub: https://github.com/MarbleCeo/wifi-qr-reader

import sys
import cv2
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QHBoxLayout, QWidget, QPushButton, QMessageBox,
                             QTextEdit)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from pyzbar.pyzbar import decode
import re

class WiFiQRReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WiFi QR Reader - by @marbleceo")
        self.setGeometry(100, 100, 850, 700)
        self.camera_active = False
        self.cap = None
        
        self.initUI()
        self.setupCamera()
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        title = QLabel("📷 WiFi QR Reader")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)
        
        self.camera_label = QLabel("Inicializando câmera...")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet("border: 2px solid #333; background-color: #000; color: #fff;")
        layout.addWidget(self.camera_label)
        
        self.log_output = QTextEdit()
        self.log_output.setMaximumHeight(150)
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #f5f5f5; padding: 5px; font-family: monospace;")
        self.log_output.append("Aguardando QR Code de WiFi...")
        layout.addWidget(self.log_output)
        
        button_layout = QHBoxLayout()
        
        self.switch_btn = QPushButton("📷 Alternar Câmera")
        self.switch_btn.clicked.connect(self.switchCamera)
        self.switch_btn.setStyleSheet("padding: 10px; font-size: 14px;")
        button_layout.addWidget(self.switch_btn)
        
        self.clear_btn = QPushButton("🗑️ Limpar Log")
        self.clear_btn.clicked.connect(self.clearLog)
        self.clear_btn.setStyleSheet("padding: 10px; font-size: 14px;")
        button_layout.addWidget(self.clear_btn)
        
        self.exit_btn = QPushButton("❌ Sair")
        self.exit_btn.clicked.connect(self.close)
        self.exit_btn.setStyleSheet("padding: 10px; font-size: 14px;")
        button_layout.addWidget(self.exit_btn)
        
        layout.addLayout(button_layout)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(30)
        
    def setupCamera(self):
        self.current_camera = 0
        self.connectCamera(self.current_camera)
        
    def connectCamera(self, camera_index):
        if self.cap is not None:
            self.cap.release()
        
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            self.camera_label.setText(f"Erro ao abrir câmera {camera_index}")
            self.log(f"❌ Erro ao abrir câmera {camera_index}")
            self.camera_active = False
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera_active = True
        self.log(f"✅ Câmera {camera_index} iniciada")
        return True
        
    def switchCamera(self):
        cameras = [0, 1, 2, 3]
        current_idx = cameras.index(self.current_camera) if self.current_camera in cameras else -1
        next_idx = (current_idx + 1) % len(cameras)
        self.current_camera = cameras[next_idx]
        self.connectCamera(self.current_camera)
        
    def clearLog(self):
        self.log_output.clear()
        
    def log(self, message):
        self.log_output.append(message)
        
    def updateFrame(self):
        if not self.camera_active or self.cap is None:
            return
            
        ret, frame = self.cap.read()
        if not ret:
            return
            
        qrs = decode(frame)
        
        for qr in qrs:
            x, y, w, h = qr.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            
            qr_data = qr.data.decode('utf-8')
            
            if qr_data.startswith('WIFI:'):
                self.log(f"📱 QR Code detectado!")
                self.log(f"📄 Dados: {qr_data}")
                self.timer.stop()
                self.processWiFiQR(qr_data)
                self.timer.start(30)
                
                cv2.waitKey(2000)
                break
        
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        self.camera_label.setPixmap(pixmap.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
    def processWiFiQR(self, qr_data):
        ssid = ""
        password = ""
        encryption = ""
        
        try:
            ssid_match = re.search(r'S:([^;]+)', qr_data)
            type_match = re.search(r'T:([^;]+)', qr_data)
            pass_match = re.search(r'P:([^;]*)', qr_data)
            
            if ssid_match:
                ssid = ssid_match.group(1)
            if type_match:
                encryption = type_match.group(1)
            if pass_match:
                password = pass_match.group(1)
                
        except Exception as e:
            self.log(f"❌ Erro ao ler QR: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao ler QR: {str(e)}")
            return
            
        if not ssid:
            self.log("❌ QR não contém SSID válido")
            QMessageBox.warning(self, "Aviso", "QR não contém SSID válido")
            return
            
        self.log(f"📡 Rede detectada:")
        self.log(f"   SSID: {ssid}")
        self.log(f"   Criptografia: {encryption}")
        self.log(f"   Senha: {'***' if password else '(aberta)'}")
        
        msg = f"Rede WiFi detectada:\n\n"
        msg += f"SSID: {ssid}\n"
        msg += f"Criptografia: {encryption}\n"
        if password:
            msg += f"Senha: ****\n\n"
        else:
            msg += "Senha: (aberta)\n\n"
        msg += "Deseja conectar?"
        
        reply = QMessageBox.question(self, "Conectar WiFi?", msg, 
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.connectToWiFi(ssid, password, encryption)
            
    def connectToWiFi(self, ssid, password, encryption):
        self.log("🔄 Tentando conectar...")
        
        try:
            # Primeiro, verificar se o NetworkManager está ativo
            check_nm = subprocess.run(['systemctl', 'is-active', 'NetworkManager'], 
                                     capture_output=True, text=True)
            if check_nm.returncode != 0:
                self.log("⚠️ NetworkManager não está ativo!")
                QMessageBox.warning(self, "Aviso", "NetworkManager não está rodando!")
                return
            
            # Tentar conectar
            if encryption == 'nopass' or not password:
                self.log(f"📶 Conectando sem senha a '{ssid}'...")
                result = subprocess.run(['nmcli', 'device', 'wifi', 'connect', ssid], 
                                      capture_output=True, text=True, timeout=30)
            else:
                self.log(f"🔐 Conectando com senha a '{ssid}'...")
                # Usar aspas para lidar com senhas com espaços
                cmd = ['nmcli', 'device', 'wifi', 'connect', ssid, 'password', password]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
            self.log(f"📤 Retorno: {result.returncode}")
            
            if result.stdout:
                self.log(f"📝 stdout: {result.stdout}")
            if result.stderr:
                self.log(f"⚠️ stderr: {result.stderr}")
                
            if result.returncode == 0:
                self.log("✅ Conectado com sucesso!")
                QMessageBox.information(self, "Sucesso", f"Conectado à rede {ssid}!")
            else:
                self.log(f"❌ Erro ao conectar (código {result.returncode})")
                
                # Tentar método alternativo usando nmcli connection
                self.log("🔄 Tentando método alternativo...")
                if encryption == 'WPA' or encryption == 'WPA2':
                    conn_name = ssid.replace(' ', '_')
                    cmd_alt = ['nmcli', 'connection', 'add', 'type', 'wifi', 
                              'con-name', conn_name, 'ssid', ssid]
                    subprocess.run(cmd_alt, capture_output=True, text=True)
                    
                    cmd_wifi_sec = ['nmcli', 'connection', 'modify', conn_name,
                                  'wifi-sec.key-mgmt', 'wpa-psk',
                                  'wifi-sec.psk', password]
                    subprocess.run(cmd_wifi_sec, capture_output=True, text=True)
                    
                    result_alt = subprocess.run(['nmcli', 'connection', 'up', conn_name],
                                              capture_output=True, text=True, timeout=30)
                    
                    if result_alt.returncode == 0:
                        self.log("✅ Conectado com método alternativo!")
                        QMessageBox.information(self, "Sucesso", f"Conectado à rede {ssid}!")
                    else:
                        error_msg = result.stderr if result.stderr else result.stdout
                        if not error_msg:
                            error_msg = f"Código de erro: {result.returncode}"
                        QMessageBox.critical(self, "Erro", f"Falha ao conectar:\n{error_msg}")
                else:
                    error_msg = result.stderr if result.stderr else result.stdout
                    if not error_msg:
                        error_msg = f"Código de erro: {result.returncode}"
                    QMessageBox.critical(self, "Erro", f"Falha ao conectar:\n{error_msg}")
                
        except subprocess.TimeoutExpired:
            self.log("❌ Timeout ao conectar (30s)")
            QMessageBox.critical(self, "Erro", "Timeout ao conectar (30 segundos)")
        except Exception as e:
            self.log(f"❌ Exceção: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao conectar:\n{str(e)}")
            
    def closeEvent(self, event):
        if self.cap is not None:
            self.cap.release()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WiFiQRReader()
    window.show()
    sys.exit(app.exec_())
