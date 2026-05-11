# 🤖 Asistencia_bot (@JackRocko_bot)
## Bot de Ofertas de Tecnología — Instrucciones de Despliegue

---

## ⚙️ Requisitos
- Python 3.10 o superior
- pip actualizado

---

## 🚀 Instalación local (PC / VPS / Raspberry Pi)

```bash
# 1. Entra a la carpeta
cd asistencia_bot

# 2. Crea entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Arranca el bot
python bot.py
```

---

## ☁️ Despliegue en servidor 24/7 (Railway / Render / VPS)

### Railway (gratis)
1. Crea cuenta en https://railway.app
2. Nuevo proyecto → Deploy from GitHub
3. Sube la carpeta o conecta tu repo
4. Variables de entorno: ninguna (el token ya está en el código)
5. Start command: `python bot.py`

### Render (gratis)
1. https://render.com → New Web Service
2. Build command: `pip install -r requirements.txt`
3. Start command: `python bot.py`

### VPS con systemd (Ubuntu)
```bash
sudo nano /etc/systemd/system/jackrocko.service

[Unit]
Description=JackRocko Ofertas Bot
After=network.target

[Service]
ExecStart=/ruta/venv/bin/python /ruta/bot.py
WorkingDirectory=/ruta/asistencia_bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

sudo systemctl enable jackrocko
sudo systemctl start jackrocko
```

---

## 📱 Primer uso

1. Abre Telegram y busca **@JackRocko_bot**
2. Escribe `/start`
3. El bot registra tu chat y comenzará a enviarte alertas

---

## 🔧 Comandos disponibles

| Comando | Descripción |
|---------|-------------|
| `/start` | Registrarse y activar alertas |
| `/ofertas` | Buscar ofertas ahora mismo |
| `/buscar laptop` | Buscar un producto específico |
| `/estado` | Ver estadísticas del bot |
| `/salir` | Dejar de recibir alertas |

---

## 📊 Criterios de filtrado

- ✅ Categoría: Tecnología (computación + electrónica)
- ✅ Descuento mínimo: **40%**
- ✅ Precio: **$100 – $6,000 MXN**
- ✅ Fuente: Mercado Libre México
- ✅ Deduplicación: no repite ofertas ya enviadas
- ✅ Frecuencia: cada **3 horas**

---

## 📁 Archivos generados

- `chat_ids.json` — lista de chats suscritos
- `seen_deals.json` — historial de ofertas enviadas (evita repetir)
