#!/usr/bin/env python3
"""
Asistencia_bot (@JackRocko_bot) — Tecnología con descuento ≥40%, precio $100–$6000
Busca ofertas cada 3 horas y las envía al canal/chat configurado.
"""

import os
import json
import time
import logging
import asyncio
import hashlib
import datetime
from typing import Optional

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

# ─── CONFIGURACIÓN ───────────────────────────────────────────────────────────
BOT_TOKEN = "8699234184:AAFphRqFAJtt3C99stShlYfwJFoPpz0cVZA"

# Aquí pon el chat_id donde el bot enviará las ofertas.
# Puede ser tu ID personal, un grupo o un canal.
# Ejecuta el bot una vez y escríbele /start para obtener tu chat_id automáticamente.
CHAT_ID_FILE = "chat_ids.json"

PRECIO_MIN = 100
PRECIO_MAX = 6000
DESCUENTO_MIN = 40          # porcentaje mínimo
INTERVALO_HORAS = 3

SEEN_FILE = "seen_deals.json"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def load_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def deal_id(deal: dict) -> str:
    key = f"{deal.get('title','')}{deal.get('url','')}"
    return hashlib.md5(key.encode()).hexdigest()[:12]

# ─── FUENTES DE OFERTAS ──────────────────────────────────────────────────────

async def fetch_mercadolibre(client: httpx.AsyncClient) -> list[dict]:
    """Busca en Mercado Libre México — tecnología con descuento."""
    deals = []
    keywords = [
        "laptop", "smartphone", "tablet", "smartwatch", "audifonos",
        "teclado mecanico", "monitor gaming", "ssd", "disco duro",
        "camara digital", "impresora", "router wifi", "consola",
        "bocina bluetooth", "power bank", "memoria ram", "procesador"
    ]
    base = "https://api.mercadolibre.com/sites/MLM/search"

    for kw in keywords[:6]:   # limitamos para no saturar la API
        try:
            params = {
                "q": kw,
                "category": "MLM1648",   # Computación
                "price": f"{PRECIO_MIN}-{PRECIO_MAX}",
                "discount": DESCUENTO_MIN,
                "limit": 5,
                "sort": "relevance",
            }
            r = await client.get(base, params=params, timeout=15)
            r.raise_for_status()
            results = r.json().get("results", [])
            for item in results:
                original = item.get("original_price") or 0
                current  = item.get("price") or 0
                if original and current and original > current:
                    disc = round((1 - current / original) * 100)
                else:
                    disc = item.get("discount_percentage") or 0

                if disc < DESCUENTO_MIN:
                    continue
                if not (PRECIO_MIN <= current <= PRECIO_MAX):
                    continue

                deals.append({
                    "source":    "Mercado Libre 🛒",
                    "title":     item.get("title", "Sin título"),
                    "price":     current,
                    "original":  original or current,
                    "discount":  disc,
                    "url":       item.get("permalink", ""),
                    "currency":  "MXN",
                    "thumbnail": item.get("thumbnail", ""),
                    "seller":    item.get("seller", {}).get("nickname", ""),
                })
        except Exception as e:
            log.warning(f"ML error ({kw}): {e}")

    return deals


async def fetch_mercadolibre_electronica(client: httpx.AsyncClient) -> list[dict]:
    """Segunda categoría: Electrónica (MLM1000)."""
    deals = []
    base = "https://api.mercadolibre.com/sites/MLM/search"
    try:
        params = {
            "category": "MLM1000",
            "price": f"{PRECIO_MIN}-{PRECIO_MAX}",
            "discount": DESCUENTO_MIN,
            "limit": 20,
            "sort": "price_desc",
        }
        r = await client.get(base, params=params, timeout=15)
        r.raise_for_status()
        for item in r.json().get("results", []):
            original = item.get("original_price") or 0
            current  = item.get("price") or 0
            if original and current and original > current:
                disc = round((1 - current / original) * 100)
            else:
                disc = item.get("discount_percentage") or 0

            if disc < DESCUENTO_MIN:
                continue
            if not (PRECIO_MIN <= current <= PRECIO_MAX):
                continue

            deals.append({
                "source":    "Mercado Libre ⚡",
                "title":     item.get("title", "Sin título"),
                "price":     current,
                "original":  original or current,
                "discount":  disc,
                "url":       item.get("permalink", ""),
                "currency":  "MXN",
                "thumbnail": item.get("thumbnail", ""),
                "seller":    item.get("seller", {}).get("nickname", ""),
            })
    except Exception as e:
        log.warning(f"ML Electrónica error: {e}")
    return deals


async def fetch_amazon_deals(client: httpx.AsyncClient) -> list[dict]:
    """
    Amazon scraping ligero vía Rainforest-style endpoint gratuito.
    Usamos la API pública de búsqueda de Amazon (no oficial, sin clave).
    """
    deals = []
    # Usamos serpapi alternativo gratuito (jserp / axesso demo)
    # Como alternativa sólida usamos el endpoint público de búsqueda de Amazon
    keywords = ["laptop descuento", "tablet oferta", "auriculares gaming"]
    for kw in keywords:
        try:
            url = f"https://www.amazon.com.mx/s?k={kw.replace(' ','+')}&rh=p_36%3A{PRECIO_MIN*100}-{PRECIO_MAX*100}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "es-MX,es;q=0.9",
            }
            r = await client.get(url, headers=headers, timeout=20, follow_redirects=True)
            # Parseo básico sin beautifulsoup: extraer títulos y precios con regex
            import re
            prices = re.findall(r'\$[\d,]+\.\d{2}', r.text)
            titles = re.findall(r'"result_info".*?"title":"([^"]{10,80})"', r.text)
            if prices and titles:
                for i, title in enumerate(titles[:3]):
                    try:
                        price_str = prices[i].replace('$','').replace(',','')
                        price = float(price_str)
                        if PRECIO_MIN <= price <= PRECIO_MAX:
                            deals.append({
                                "source":    "Amazon MX 📦",
                                "title":     title,
                                "price":     price,
                                "original":  price * 1.5,   # estimado
                                "discount":  33,
                                "url":       f"https://www.amazon.com.mx/s?k={kw.replace(' ','+')}",
                                "currency":  "MXN",
                                "thumbnail": "",
                                "seller":    "Amazon",
                            })
                    except Exception:
                        pass
        except Exception as e:
            log.warning(f"Amazon error ({kw}): {e}")
    return deals


# ─── MOTOR PRINCIPAL ─────────────────────────────────────────────────────────

async def collect_all_deals() -> list[dict]:
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            fetch_mercadolibre(client),
            fetch_mercadolibre_electronica(client),
            return_exceptions=True,
        )
    all_deals = []
    for r in results:
        if isinstance(r, list):
            all_deals.extend(r)
    # Deduplicar por título
    seen_titles = set()
    unique = []
    for d in all_deals:
        t = d["title"][:50].lower()
        if t not in seen_titles:
            seen_titles.add(t)
            unique.append(d)
    # Ordenar: mayor descuento primero
    unique.sort(key=lambda x: x["discount"], reverse=True)
    return unique[:20]   # max 20 por ronda


def format_deal_message(deal: dict, idx: int) -> str:
    bar_filled = min(int(deal["discount"] / 5), 20)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)
    ahorro = deal["original"] - deal["price"]
    ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    msg = (
        f"🔥 *OFERTA #{idx}* — {deal['source']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 *{deal['title']}*\n\n"
        f"💰 Precio: *${deal['price']:,.0f} {deal['currency']}*\n"
        f"~~Antes: ${deal['original']:,.0f}~~\n"
        f"💸 Ahorro: *${ahorro:,.0f}*\n"
        f"🏷️ Descuento: *{deal['discount']}%*\n"
        f"`{bar}`\n\n"
    )
    if deal.get("seller"):
        msg += f"🏪 Vendedor: {deal['seller']}\n"
    msg += f"🕐 Encontrado: {ts}\n"
    return msg


async def send_deals(bot: Bot, chat_ids: list, deals: list[dict]):
    if not deals:
        log.info("No se encontraron ofertas nuevas.")
        return

    # Encabezado
    header = (
        f"🤖 *@JackRocko\\_bot — Reporte de Ofertas Tech*\n"
        f"🕐 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        f"📊 *{len(deals)} ofertas nuevas* | Desc. ≥40% | $100–$6,000 MXN\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    for cid in chat_ids:
        try:
            await bot.send_message(
                chat_id=cid,
                text=header,
                parse_mode=ParseMode.MARKDOWN,
            )
            for i, deal in enumerate(deals, 1):
                try:
                    msg = format_deal_message(deal, i)
                    kb = InlineKeyboardMarkup([[
                        InlineKeyboardButton("🛒 Ver oferta", url=deal["url"])
                    ]]) if deal.get("url") else None

                    await bot.send_message(
                        chat_id=cid,
                        text=msg,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=kb,
                        disable_web_page_preview=False,
                    )
                    await asyncio.sleep(0.5)
                except Exception as e:
                    log.warning(f"Error enviando oferta {i}: {e}")

            footer = (
                f"✅ *Fin del reporte*\n"
                f"⏰ Próxima búsqueda en *{INTERVALO_HORAS} horas*\n"
                f"💡 Usa /buscar \\<producto\\> para búsqueda manual"
            )
            await bot.send_message(
                chat_id=cid,
                text=footer,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception as e:
            log.error(f"Error enviando a {cid}: {e}")


async def job_buscar_ofertas(bot: Bot):
    log.info("🔍 Iniciando búsqueda de ofertas...")
    chat_ids = load_json(CHAT_ID_FILE, [])
    if not chat_ids:
        log.warning("No hay chat_ids registrados. Escríbele /start al bot.")
        return

    seen = set(load_json(SEEN_FILE, []))
    deals = await collect_all_deals()

    new_deals = []
    for d in deals:
        did = deal_id(d)
        if did not in seen:
            new_deals.append(d)
            seen.add(did)

    # Limitar historial a 500 entradas
    seen_list = list(seen)[-500:]
    save_json(SEEN_FILE, seen_list)

    log.info(f"Ofertas nuevas: {len(new_deals)} / {len(deals)} encontradas")
    await send_deals(bot, chat_ids, new_deals)


# ─── HANDLERS DE COMANDOS ────────────────────────────────────────────────────

from telegram.ext import (
    Application, CommandHandler, ContextTypes,
)
from telegram import Update

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    chat_ids = load_json(CHAT_ID_FILE, [])
    if cid not in chat_ids:
        chat_ids.append(cid)
        save_json(CHAT_ID_FILE, chat_ids)
        msg = (
            f"✅ *¡Registrado!*\n"
            f"Chat ID: `{cid}`\n\n"
            f"🤖 *@JackRocko\\_bot* buscará ofertas de tecnología cada *{INTERVALO_HORAS} horas*.\n\n"
            f"📋 *Criterios:*\n"
            f"• Descuento mínimo: *40%*\n"
            f"• Precio: *$100 – $6,000 MXN*\n"
            f"• Fuentes: Mercado Libre\n\n"
            f"Comandos disponibles:\n"
            f"/buscar \\<producto\\> — Buscar ahora\n"
            f"/ofertas — Lanzar búsqueda manual\n"
            f"/estado — Ver estado del bot\n"
            f"/salir — Dejar de recibir alertas"
        )
    else:
        msg = f"✅ Ya estás registrado \\(Chat ID: `{cid}`\\)\nUsa /ofertas para buscar ahora."

    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


async def cmd_ofertas(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Buscando ofertas de tecnología... un momento.")
    bot = ctx.bot
    chat_ids = [update.effective_chat.id]
    seen = set(load_json(SEEN_FILE, []))
    deals = await collect_all_deals()
    # En búsqueda manual mostramos todo (no filtrar por vistos)
    log.info(f"Manual search: {len(deals)} ofertas")
    await send_deals(bot, chat_ids, deals)


async def cmd_buscar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = " ".join(ctx.args) if ctx.args else ""
    if not query:
        await update.message.reply_text("❓ Uso: /buscar <producto>\nEjemplo: /buscar laptop gaming")
        return

    await update.message.reply_text(f"🔍 Buscando: *{query}*...", parse_mode=ParseMode.MARKDOWN)

    deals = []
    async with httpx.AsyncClient() as client:
        try:
            base = "https://api.mercadolibre.com/sites/MLM/search"
            params = {
                "q": query,
                "price": f"{PRECIO_MIN}-{PRECIO_MAX}",
                "discount": DESCUENTO_MIN,
                "limit": 10,
                "sort": "relevance",
            }
            r = await client.get(base, params=params, timeout=15)
            r.raise_for_status()
            for item in r.json().get("results", []):
                original = item.get("original_price") or 0
                current  = item.get("price") or 0
                if original and current and original > current:
                    disc = round((1 - current / original) * 100)
                else:
                    disc = item.get("discount_percentage") or 0
                if disc < DESCUENTO_MIN or not (PRECIO_MIN <= current <= PRECIO_MAX):
                    continue
                deals.append({
                    "source":    "Mercado Libre 🛒",
                    "title":     item.get("title", "Sin título"),
                    "price":     current,
                    "original":  original or current,
                    "discount":  disc,
                    "url":       item.get("permalink", ""),
                    "currency":  "MXN",
                    "thumbnail": item.get("thumbnail", ""),
                    "seller":    item.get("seller", {}).get("nickname", ""),
                })
        except Exception as e:
            await update.message.reply_text(f"❌ Error al buscar: {e}")
            return

    if deals:
        await send_deals(ctx.bot, [update.effective_chat.id], deals)
    else:
        await update.message.reply_text(
            f"😔 No encontré *{query}* con ≥40% descuento en ese rango de precio.\n"
            f"Intenta con otra búsqueda.",
            parse_mode=ParseMode.MARKDOWN,
        )


async def cmd_estado(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_ids = load_json(CHAT_ID_FILE, [])
    seen = load_json(SEEN_FILE, [])
    msg = (
        f"📊 *Estado del bot*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"✅ Bot activo\n"
        f"👥 Chats registrados: *{len(chat_ids)}*\n"
        f"📦 Ofertas en historial: *{len(seen)}*\n"
        f"⏰ Intervalo: cada *{INTERVALO_HORAS} horas*\n"
        f"💰 Precio: *$100 – $6,000 MXN*\n"
        f"🏷️ Descuento mín.: *40%*\n"
        f"🕐 Hora servidor: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


async def cmd_salir(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    chat_ids = load_json(CHAT_ID_FILE, [])
    if cid in chat_ids:
        chat_ids.remove(cid)
        save_json(CHAT_ID_FILE, chat_ids)
        await update.message.reply_text("👋 Removido. Ya no recibirás alertas.\nUsa /start para volver.")
    else:
        await update.message.reply_text("No estabas registrado.")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",   cmd_start))
    app.add_handler(CommandHandler("ofertas", cmd_ofertas))
    app.add_handler(CommandHandler("buscar",  cmd_buscar))
    app.add_handler(CommandHandler("estado",  cmd_estado))
    app.add_handler(CommandHandler("salir",   cmd_salir))

    scheduler = AsyncIOScheduler(timezone="America/Mexico_City")
    scheduler.add_job(
        job_buscar_ofertas,
        trigger="interval",
        hours=INTERVALO_HORAS,
        args=[app.bot],
        id="buscar_ofertas",
        next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=10),
    )

    async def on_startup(app):
        scheduler.start()
        log.info(f"✅ Bot iniciado. Buscará cada {INTERVALO_HORAS}h.")

    async def on_shutdown(app):
        scheduler.shutdown()

    app.post_init    = on_startup
    app.post_shutdown = on_shutdown

    log.info("🤖 @JackRocko_bot arrancando...")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
