# WiFi QR Reader

Leitor de QR Code de WiFi com visualização da câmera em tempo real.

![License](https://img.shields.io/badge/license-noncommercial-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)

## 📷 Funcionalidades

- Visualização da câmera em tempo real
- Detecção automática de QR Codes de WiFi
- Conexão automática via NetworkManager
- Suporte a múltiplas câmeras
- Log detalhado de conexões
- Interface gráfica amigável

## 🚀 Instalação

### Snap Store (Recomendado)
```bash
sudo snap install wifi-qr-reader
```

### GitHub Releases
Baixe o AppImage da [última release](https://github.com/MarbleCeo/wifi-qr-reader/releases)

### Manual
```bash
# Instalar dependências
sudo apt install python3-pip python3-opencv python3-pyqt5
pip3 install pyzbar

# Baixar e executar
wget https://github.com/MarbleCeo/wifi-qr-reader/releases/latest/download/wifi-qr-reader.py
python3 wifi-qr-reader.py
```

## 💻 Como Usar

1. Abra o aplicativo
2. Posicione o QR Code do WiFi na frente da câmera
3. Confirme a conexão quando solicitado

## 🔧 Dependências

- Python 3.8+
- OpenCV
- PyQt5
- pyzbar
- NetworkManager

## 📦 Empacotamento

### Snap
```bash
cd snap
snapcraft
```

### AppImage
```bash
pipx install pyinstaller
pyinstaller --onefile --windowed wifi-qr-reader-gui.py
```

## 🤝 Contribuindo

Pull requests são bem-vindos! Sinta-se à vontade para abrir issues para bugs ou sugestões.

## 📄 Licença

Uso pessoal e não-comercial é livre. Uso comercial (venda, sublicenciamento,
inclusão em produto/serviço pago) requer acordo por escrito e pagamento de
royalty ao autor — veja [LICENSE](LICENSE) para detalhes.

## 🔗 Links

- [Snap Store](https://snapcraft.io/wifi-qr-reader)
- [Issues](https://github.com/MarbleCeo/wifi-qr-reader/issues)
- [Discussions](https://github.com/MarbleCeo/wifi-qr-reader/discussions)

## 👤 Autor

**Seu Nome** - [@seu-usuario](https://github.com/MarbleCeo)
