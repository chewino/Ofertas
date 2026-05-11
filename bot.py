#!/usr/bin/env python3
"""
Asistencia_bot (@JackRocko_bot) — Tecnología con descuento ≥40%, precio $100–$6000
"""

import json
import logging
import asyncio
import hashlib
import datetime

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

BOT_TOKEN       = "8699234184:AAFphRqFAJtt3C99stShlYfwJFoPpz0cVZA"
CHAT_ID_FILE    = "chat_ids.json"
SEEN_FILE       = "seen_deals.json"
PRECIO_MIN      = 100
PRECIO_MAX      = 6000
DESCUENTO_MIN   = 40
INTERVALO_HORAS = 3

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def deal_id(deal):
    key = f"{deal.get('title','')}{deal.get('url','')}"
    return hashlib.md5(key.encode()).hexdigest()[:12]

def parse_item(item):
    current  = float(item.get("price") or 0)
    original = float(item.get("original_price") or 0)
    if current <= 0 or original <= current:
        return None
    discount = round((1 - current / original) * 100)
    if discount < DESCUENTO_MIN:
        return None
    if not (PRECIO_MIN <= current <= PRECIO_MAX):
        return None
    return {
        "source":   "Mercado Libre 🛒",
        "title":    item.get("title", "Sin título"),
        "price":    current,
        "original": original,
        "discount": discount,
        "url":      item.get("permalink", ""),
        "currency": "MXN",
        "seller":   item.get("seller", {}).get("nickname", ""),
    }

KEYWORDS = [
    "laptop", "tablet", "smartphone", "smartwatch", "audifonos bluetooth",
    "monitor", "teclado mecanico", "ssd", "disco duro externo",
    "router wifi", "camara web", "bocina bluetooth", "power bank",
    "memoria ram", "tarjeta grafica", "consola", "drone",
    "impresora", "proyector",
]

async def search_ml(client, query, limit=20):
    try:
        r = await client.get(
            "https://api.mercadolibre.com/sites/MLM/search",
            params={"q": query, "price": f"{PRECIO_MIN}-{PRECIO_MAX}", "limit": limit, "sort": "price_asc"},
            timeout=15,
        )
        r.raise_for_status()
        deals = []
        for item in r.json().get("results", []):
            d = parse_item(item)
            if d:
                deals.append(d)
        return deals
    except Exception as e:
        log.warning(f"ML error ({query}): {e}")
        return []

async def collect_all_deals():
    all_deals = []
    async with httpx.AsyncClient() as client:
        for i in range(0, len(KEYWORDS), 5):
            batch = KEYWORDS[i:i+5]
            results = await asyncio.gather(*[search_ml(client, kw) for kw in batch])
            for r in results:
                all_deals.extend(r)
            await asyncio.sleep(0.5)

    seen_titles = set()
    unique = []
    for d in all_deals:
        t = d["title"][:50].lower()
        if t not in seen_titles:
            seen_titles.add(t)
            unique.append(d)
    unique.sort(key=lambda x: x["discount"], reverse=True)
    return unique[:25]

def escape_md(text):
    for ch in r"_*[]()~`>#+-=|{}.!":
        text = text.replace(ch, f"\\{ch}")
    return text

def format_deal(deal, idx):
    ahorro = deal["original"] - deal["price"]
    bar = "█" * min(deal["discount"] // 5, 20) + "░" * max(0, 20 - deal["discount"] // 5)
    ts  = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    title = escape_md(deal["title"])
    seller = escape_md(deal.get("seller", ""))
    return (
        f"🔥 *OFERTA \\#{idx}* — {deal['source']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 *{title}*\n\n"
        f"💰 Precio: *\\${deal['price']:,.0f} MXN*\n"
        f"~~Antes: \\${deal['original']:,.0f}~~\n"
        f"💸 Ahorro: *\\${ahorro:,.0f}*\n"
        f"🏷️ Descuento: *{deal['discount']}%*\n"
        f"`{bar}`\n"
        + (f"🏪 _{seller}_\n" if seller else "")
        + f"🕐 _{escape_md(ts)}_"
    )

async def send_deals(bot, chat_ids, deals):
    if not deals:
        for cid in chat_ids:
            await bot.send_message(cid, "😔 No encontré ofertas nuevas con ≥40% de descuento ahora. Reintentaré en 3 horas.")
        return

    header = (
        f"🤖 *@JackRocko\\_bot — Ofertas Tech*\n"
        f"📅 {escape_md(datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))}\n"
        f"📊 *{len(deals)} ofertas* \\| Desc\\. ≥40% \\| \\$100–\\$6,000 MXN\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    for cid in chat_ids:
        try:
            await bot.send_message(cid, header, parse_mode=ParseMode.MARKDOWN_V2)
            for i, deal in enumerate(deals, 1):
                try:
                    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Ver oferta", url=deal["url"])]]) if deal.get("url") else None
                    await bot.send_message(cid, format_deal(deal, i), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=kb, disable_web_page_preview=True)
                    await asyncio.sleep(0.4)
                except Exception as e:
                    log.warning(f"Error oferta {i}: {e}")
            await bot.send_message(cid, f"✅ *Fin del reporte*\n⏰ Próxima búsqueda en *{INTERVALO_HORAS} horas*", parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(f"Error enviando a {cid}: {e}")

async def job_buscar(bot):
    log.info("🔍 Buscando ofertas...")
    chat_ids = load_json(CHAT_ID_FILE, [])
    if not chat_ids:
        log.warning("Sin chat_ids — escríbele /start al bot.")
        return
    seen  = set(load_json(SEEN_FILE, []))
    deals = await collect_all_deals()
    new_deals = [d for d in deals if deal_id(d) not in seen]
    for d in new_deals:
        seen.add(deal_id(d))
    save_json(SEEN_FILE, list(seen)[-500:])
    log.info(f"Nuevas: {len(new_deals)} / encontradas: {len(deals)}")
    await send_deals(bot, chat_ids, new_deals)

async def cmd_start(update, ctx):
    cid = update.effective_chat.id
    ids = load_json(CHAT_ID_FILE, [])
    if cid not in ids:
        ids.append(cid)
        save_json(CHAT_ID_FILE, ids)
        txt = (
            f"✅ *¡Registrado\\!* Chat ID: `{cid}`\n\n"
            f"🤖 Recibirás alertas cada *{INTERVALO_HORAS} horas*\n\n"
            f"📋 *Criterios:*\n• Descuento mínimo: *40%*\n• Precio: *\\$100 – \\$6,000 MXN*\n• Fuente: Mercado Libre MX\n\n"
            f"*Comandos:*\n/ofertas — Buscar ahora\n/buscar laptop — Buscar producto\n/estado — Ver estado\n/salir — Desactivar"
        )
    else:
        txt = f"✅ Ya estás registrado \\(Chat ID: `{cid}`\\)\nUsa /ofertas para buscar ahora\\."
    await update.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN_V2)

async def cmd_ofertas(update, ctx):
    await update.message.reply_text("🔍 Buscando ofertas... un momento.")
    deals = await collect_all_deals()
    await send_deals(ctx.bot, [update.effective_chat.id], deals)

async def cmd_buscar(update, ctx):
    query = " ".join(ctx.args) if ctx.args else ""
    if not query:
        await update.message.reply_text("❓ Uso: /buscar <producto>\nEjemplo: /buscar laptop gaming")
        return
    await update.message.reply_text(f"🔍 Buscando: {query}...")
    async with httpx.AsyncClient() as client:
        deals = await search_ml(client, query, limit=50)
    if deals:
        await send_deals(ctx.bot, [update.effective_chat.id], deals[:10])
    else:
        await update.message.reply_text(f"😔 No encontré '{query}' con ≥40% descuento en $100–$6,000 MXN. Intenta otra búsqueda.")

async def cmd_estado(update, ctx):
    ids  = load_json(CHAT_ID_FILE, [])
    seen = load_json(SEEN_FILE, [])
    txt = (
        f"📊 *Estado del bot*\n━━━━━━━━━━━━━━━━\n"
        f"✅ Activo\n👥 Chats: *{len(ids)}*\n📦 Historial: *{len(seen)} ofertas*\n"
        f"⏰ Intervalo: *{INTERVALO_HORAS}h*\n💰 Rango: *\\$100 – \\$6,000 MXN*\n"
        f"🏷️ Desc\\. mín\\.: *40%*\n🕐 {escape_md(datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))}"
    )
    await update.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN_V2)

async def cmd_salir(update, ctx):
    cid = update.effective_chat.id
    ids = load_json(CHAT_ID_FILE, [])
    if cid in ids:
        ids.remove(cid)
        save_json(CHAT_ID_FILE, ids)
        await update.message.reply_text("👋 Removido. Ya no recibirás alertas.\nUsa /start para volver.")
    else:
        await update.message.reply_text("No estabas registrado.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",   cmd_start))
    app.add_handler(CommandHandler("ofertas", cmd_ofertas))
    app.add_handler(CommandHandler("buscar",  cmd_buscar))
    app.add_handler(CommandHandler("estado",  cmd_estado))
    app.add_handler(CommandHandler("salir",   cmd_salir))

    scheduler = AsyncIOScheduler(timezone="America/Mexico_City")
    scheduler.add_job(
        job_buscar, trigger="interval", hours=INTERVALO_HORAS, args=[app.bot],
        id="job_ofertas",
        next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=15),
    )

    async def on_startup(a):
        scheduler.start()
        log.info(f"✅ Bot iniciado. Buscará cada {INTERVALO_HORAS}h.")

    async def on_shutdown(a):
        scheduler.shutdown()

    app.post_init     = on_startup
    app.post_shutdown = on_shutdown

    log.info("🤖 @JackRocko_bot arrancando...")
    app.run_polling(allowed_updates=["message"])

if __name__ == "__main__":
    main()
