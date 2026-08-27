#!/usr/bin/env python3
# WiFi QR Reader - Leitor de QR Code de WiFi
# Autor: @marbleceo
# GitHub: https://github.com/MarbleCeo/wifi-qr-reader

import os
import re
import subprocess
import sys
import time
from pathlib import Path

import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from pyzbar.pyzbar import decode

ICON_PATH = Path(__file__).resolve().parent.parent / "packaging" / "icon.svg"

STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1e1f26;
    color: #e8e8ec;
    font-family: 'Segoe UI', sans-serif;
}
QLabel#title {
    color: #7dd3fc;
}
QLabel#status {
    padding: 6px 12px;
    border-radius: 10px;
    font-weight: 600;
}
QLabel#status[state="idle"] { background-color: #33344a; color: #b8bacf; }
QLabel#status[state="scanning"] { background-color: #1e3a4a; color: #7dd3fc; }
QLabel#status[state="connecting"] { background-color: #4a3a1e; color: #fbbf24; }
QLabel#status[state="connected"] { background-color: #1e4a2c; color: #4ade80; }
QLabel#status[state="error"] { background-color: #4a1e1e; color: #f87171; }
QPushButton {
    background-color: #2c2e3d;
    border: 1px solid #43465c;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 13px;
}
QPushButton:hover { background-color: #383b4f; }
QPushButton:pressed { background-color: #23253080; }
QTextEdit {
    background-color: #14151b;
    border: 1px solid #2c2e3d;
    border-radius: 8px;
    padding: 8px;
    font-family: 'Cascadia Code', 'Consolas', monospace;
}
"""

# Minimum time between processing two WiFi QR detections, so a code held in
# front of the camera doesn't retrigger the connect dialog every frame.
SCAN_COOLDOWN_SECONDS = 2.0


def host_command(*args):
    """Prefix a command with flatpak-spawn --host when sandboxed.

    Inside the Flatpak sandbox, nmcli/systemctl aren't available directly —
    flatpak-spawn --host runs them on the real system instead (requires the
    --talk-name=org.freedesktop.Flatpak permission, granted in the manifest).
    Outside a sandbox (pip install, AUR, etc.) this is a no-op.
    """
    if os.environ.get("FLATPAK_ID"):
        return ["flatpak-spawn", "--host", *args]
    return list(args)


class WiFiQRReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WiFi QR Reader")
        self.setGeometry(100, 100, 850, 720)
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

        self.camera_active = False
        self.cap = None
        self.current_camera = 0
        self._last_scan_time = 0.0

        self.initUI()
        self.connectCamera(self.current_camera)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        central_widget.setLayout(layout)

        header = QHBoxLayout()
        title = QLabel("📷 WiFi QR Reader")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        self.status_label = QLabel("Ocioso")
        self.status_label.setObjectName("status")
        self.setStatus("idle", "Ocioso")
        header.addWidget(self.status_label)
        layout.addLayout(header)

        self.camera_label = QLabel("Inicializando câmera...")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet(
            "border: 2px solid #2c2e3d; border-radius: 10px; "
            "background-color: #000; color: #888;"
        )
        layout.addWidget(self.camera_label)

        self.log_output = QTextEdit()
        self.log_output.setMaximumHeight(150)
        self.log_output.setReadOnly(True)
        self.log_output.append("Aguardando QR Code de WiFi...")
        layout.addWidget(self.log_output)

        button_layout = QHBoxLayout()

        self.switch_btn = QPushButton("📷 Alternar Câmera")
        self.switch_btn.clicked.connect(self.switchCamera)
        button_layout.addWidget(self.switch_btn)

        self.clear_btn = QPushButton("🗑️ Limpar Log")
        self.clear_btn.clicked.connect(self.clearLog)
        button_layout.addWidget(self.clear_btn)

        self.exit_btn = QPushButton("❌ Sair")
        self.exit_btn.clicked.connect(self.close)
        button_layout.addWidget(self.exit_btn)

        layout.addLayout(button_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(30)

    def setStatus(self, state, text):
        self.status_label.setText(text)
        self.status_label.setProperty("state", state)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def connectCamera(self, camera_index):
        if self.cap is not None:
            self.cap.release()

        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            self.camera_label.setText(f"Erro ao abrir câmera {camera_index}")
            self.log(f"❌ Erro ao abrir câmera {camera_index}")
            self.setStatus("error", "Câmera indisponível")
            self.camera_active = False
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera_active = True
        self.setStatus("scanning", "Procurando QR code")
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

        now = time.monotonic()
        if now - self._last_scan_time >= SCAN_COOLDOWN_SECONDS:
            for qr in decode(frame):
                x, y, w, h = qr.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

                qr_data = qr.data.decode("utf-8")
                if qr_data.startswith("WIFI:"):
                    self._last_scan_time = now
                    self.log("📱 QR Code detectado!")
                    self.log(f"📄 Dados: {qr_data}")
                    self.processWiFiQR(qr_data)
                    break

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        self.camera_label.setPixmap(
            pixmap.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def processWiFiQR(self, qr_data):
        ssid = ""
        password = ""
        encryption = ""

        try:
            ssid_match = re.search(r"S:([^;]+)", qr_data)
            type_match = re.search(r"T:([^;]+)", qr_data)
            pass_match = re.search(r"P:([^;]*)", qr_data)

            if ssid_match:
                ssid = ssid_match.group(1)
            if type_match:
                encryption = type_match.group(1)
            if pass_match:
                password = pass_match.group(1)

        except Exception as e:
            self.log(f"❌ Erro ao ler QR: {str(e)}")
            self.setStatus("error", "Erro ao ler QR")
            QMessageBox.critical(self, "Erro", f"Erro ao ler QR: {str(e)}")
            return

        if not ssid:
            self.log("❌ QR não contém SSID válido")
            self.setStatus("error", "QR inválido")
            QMessageBox.warning(self, "Aviso", "QR não contém SSID válido")
            return

        self.log("📡 Rede detectada:")
        self.log(f"   SSID: {ssid}")
        self.log(f"   Criptografia: {encryption}")
        self.log(f"   Senha: {'***' if password else '(aberta)'}")

        msg = "Rede WiFi detectada:\n\n"
        msg += f"SSID: {ssid}\n"
        msg += f"Criptografia: {encryption}\n"
        msg += ("Senha: ****\n\n" if password else "Senha: (aberta)\n\n")
        msg += "Deseja conectar?"

        reply = QMessageBox.question(
            self, "Conectar WiFi?", msg, QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.connectToWiFi(ssid, password, encryption)
        else:
            self.setStatus("scanning", "Procurando QR code")

    def connectToWiFi(self, ssid, password, encryption):
        self.log("🔄 Tentando conectar...")
        self.setStatus("connecting", f"Conectando a {ssid}")

        try:
            check_nm = subprocess.run(
                host_command("systemctl", "is-active", "NetworkManager"),
                capture_output=True,
                text=True,
            )
            if check_nm.returncode != 0:
                self.log("⚠️ NetworkManager não está ativo!")
                self.setStatus("error", "NetworkManager inativo")
                QMessageBox.warning(self, "Aviso", "NetworkManager não está rodando!")
                return

            if encryption == "nopass" or not password:
                self.log(f"📶 Conectando sem senha a '{ssid}'...")
                result = subprocess.run(
                    host_command("nmcli", "device", "wifi", "connect", ssid),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            else:
                self.log(f"🔐 Conectando com senha a '{ssid}'...")
                cmd = host_command("nmcli", "device", "wifi", "connect", ssid, "password", password)
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            self.log(f"📤 Retorno: {result.returncode}")
            if result.stdout:
                self.log(f"📝 stdout: {result.stdout}")
            if result.stderr:
                self.log(f"⚠️ stderr: {result.stderr}")

            if result.returncode == 0:
                self.log("✅ Conectado com sucesso!")
                self.setStatus("connected", f"Conectado a {ssid}")
                QMessageBox.information(self, "Sucesso", f"Conectado à rede {ssid}!")
                return

            self.log(f"❌ Erro ao conectar (código {result.returncode})")
            self.log("🔄 Tentando método alternativo...")

            if encryption in ("WPA", "WPA2"):
                conn_name = ssid.replace(" ", "_")
                subprocess.run(
                    host_command(
                        "nmcli", "connection", "add", "type", "wifi",
                        "con-name", conn_name, "ssid", ssid,
                    ),
                    capture_output=True,
                    text=True,
                )
                subprocess.run(
                    host_command(
                        "nmcli", "connection", "modify", conn_name,
                        "wifi-sec.key-mgmt", "wpa-psk",
                        "wifi-sec.psk", password,
                    ),
                    capture_output=True,
                    text=True,
                )
                result_alt = subprocess.run(
                    host_command("nmcli", "connection", "up", conn_name),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result_alt.returncode == 0:
                    self.log("✅ Conectado com método alternativo!")
                    self.setStatus("connected", f"Conectado a {ssid}")
                    QMessageBox.information(self, "Sucesso", f"Conectado à rede {ssid}!")
                    return

            error_msg = result.stderr or result.stdout or f"Código de erro: {result.returncode}"
            self.setStatus("error", "Falha ao conectar")
            QMessageBox.critical(self, "Erro", f"Falha ao conectar:\n{error_msg}")

        except subprocess.TimeoutExpired:
            self.log("❌ Timeout ao conectar (30s)")
            self.setStatus("error", "Timeout ao conectar")
            QMessageBox.critical(self, "Erro", "Timeout ao conectar (30 segundos)")
        except Exception as e:
            self.log(f"❌ Exceção: {str(e)}")
            self.setStatus("error", "Erro ao conectar")
            QMessageBox.critical(self, "Erro", f"Erro ao conectar:\n{str(e)}")

    def closeEvent(self, event):
        if self.cap is not None:
            self.cap.release()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = WiFiQRReader()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
