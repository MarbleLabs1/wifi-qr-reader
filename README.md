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

### Via pip
```bash
git clone https://github.com/MarbleLabs1/wifi-qr-reader.git
cd wifi-qr-reader
pip install .
wifi-qr-reader
```

### Arch Linux (AUR)
Pacote `wifi-qr-reader` — veja [`packaging/PKGBUILD`](packaging/PKGBUILD).

### Flatpak
Manifest em [`packaging/io.github.marbleceo.WifiQrReader.json`](packaging/io.github.marbleceo.WifiQrReader.json)
— ainda não publicado no Flathub, veja [`packaging/README.md`](packaging/README.md)
para o que falta.

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

Ver [`packaging/`](packaging/) — inclui `PKGBUILD` (AUR), manifest Flatpak,
`.desktop` e ícone.

## 🤝 Contribuindo

Pull requests são bem-vindos! Sinta-se à vontade para abrir issues para bugs ou sugestões.

## 📄 Licença

Uso pessoal e não-comercial é livre. Uso comercial (venda, sublicenciamento,
inclusão em produto/serviço pago) requer acordo por escrito e pagamento de
royalty ao autor — veja [LICENSE](LICENSE) para detalhes.

## 🔗 Links

- [Issues](https://github.com/MarbleLabs1/wifi-qr-reader/issues)

## 👤 Autor

**MarbleCeo** - [@MarbleCeo](https://github.com/MarbleCeo)
