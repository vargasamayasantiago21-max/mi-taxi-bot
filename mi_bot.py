import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Estados de la conversación
NOMBRE, CANT_PERSONAS, TIPO_SERVICIO, TAXI_DESDE, TAXI_HASTA, FINCA_FECHA_INICIO, FINCA_FECHA_FIN = range(7)


# ---------- FLUJO INICIO ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy Kevin, la IA de reservas de TaxiRadioPR.\n"
        "Por favor dime tu nombre para poder empezar.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NOMBRE


async def nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.message.text
    context.user_data["nombre"] = nombre
    await update.message.reply_text(
        f"¡Hola {nombre}!, ¿Para cuántas personas es el servicio?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return CANT_PERSONAS


async def cant_personas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cant = int(update.message.text)
        context.user_data["cant_personas"] = cant

        keyboard = [["Taxi"], ["Finca"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        await update.message.reply_text(
            "¿Con qué tipo de servicio te podemos ayudar?\n"
            "Elige una opción:",
            reply_markup=reply_markup,
        )
        return TIPO_SERVICIO
    except ValueError:
        await update.message.reply_text("Por favor, escribe solo un número.")
        return CANT_PERSONAS


async def tipo_servicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    servicio = update.message.text.lower()
    context.user_data["servicio"] = servicio

    await update.message.reply_text(
        "Puedes escribir /cancel para cancelar en cualquier momento."
    )

    if servicio == "taxi":
        await update.message.reply_text(
            "¿Desde qué ubicación necesitas la reserva?"
        )
        return TAXI_DESDE
    else:
        await update.message.reply_text(
            "¿Cuál sería la fecha de inicio de su estadía? (dd/mm/yyyy)"
        )
        return FINCA_FECHA_INICIO


# ---------- FLUJO TAXI ----------
async def taxi_desde(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["taxi_desde"] = update.message.text
    await update.message.reply_text("¿Hasta qué ubicación necesitas la reserva?")
    return TAXI_HASTA


async def taxi_hasta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["taxi_hasta"] = update.message.text
    data = context.user_data

    await update.message.reply_text(
        f"¡Perfecto {data['nombre']}! Para confirmar los datos de tu reserva:\n"
        f"🚕 Servicio de taxi para {data['cant_personas']} personas:\n"
        f"🗺️ Desde: {data['taxi_desde']}\n"
        f"➡️ Hasta: {data['taxi_hasta']}\n\n"
        "✅ Datos recibidos. El conductor asignado se comunicará pronto contigo por mensaje.\n"
        "Si deseas hacer una nueva reserva, escribe /start",
        reply_markup=ReplyKeyboardRemove(),
    )

    with open("reservas.txt", "a", encoding="utf-8") as f:
        f.write(str(data) + "\n\n")

    return ConversationHandler.END


# ---------- FLUJO FINCA ----------
async def finca_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["finca_inicio"] = update.message.text
    await update.message.reply_text("Fecha final de estadía (dd/mm/yyyy):")
    return FINCA_FECHA_FIN


async def finca_fin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["finca_fin"] = update.message.text
    data = context.user_data

    await update.message.reply_text(
        f"{data['nombre']}, estos son los datos de tu solicitud de finca:\n"
        f"Personas: {data['cant_personas']}\n"
        f"Desde: {data['finca_inicio']}\n"
        f"Hasta: {data['finca_fin']}\n\n"
        "✅ Datos recibidos. Te contactaremos pronto para confirmar disponibilidad.\n"
        "Si deseas hacer una nueva reserva, escribe /start",
        reply_markup=ReplyKeyboardRemove(),
    )

    with open("reservas.txt", "a", encoding="utf-8") as f:
        f.write(str(data) + "\n\n")

    return ConversationHandler.END


# ---------- CANCELAR ----------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Reserva cancelada. Usa /start para iniciar una nueva.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# ---------- MAIN ----------
def main():
    # CAMBIA ESTE TOKEN POR UNO NUEVO DE BOTFATHER
    application = Application.builder().token(
        "8036865946:AAGT1rlFaag6L-KmNpgm575MLJDdOU2GaMA"
    ).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, nombre)],
            CANT_PERSONAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, cant_personas)],
            TIPO_SERVICIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, tipo_servicio)],
            TAXI_DESDE: [MessageHandler(filters.TEXT & ~filters.COMMAND, taxi_desde)],
            TAXI_HASTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, taxi_hasta)],
            FINCA_FECHA_INICIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, finca_inicio)],
            FINCA_FECHA_FIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, finca_fin)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    print("Bot iniciado...")
    application.run_polling()


if __name__ == "__main__":
    main()
