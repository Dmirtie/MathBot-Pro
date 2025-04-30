from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import math
import cmath
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

TOKEN = ""
WAITING_NUMBERS = 1


def get_main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("/gcd"), KeyboardButton("/lcm")],
        [KeyboardButton("/sum"), KeyboardButton("/sub")],
        [KeyboardButton("/mul"), KeyboardButton("/div")],
        [KeyboardButton("/all"), KeyboardButton("/quadratic")],
        [KeyboardButton("/help")]
    ], resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🔢 *Привет! Я математический бот. Вот что я умею:*

Нажмите на кнопку с нужной операцией или введите команду вручную:

НОД (/gcd) - Найти наибольший общий делитель
НОК (/lcm) - Найти наименьшее общее кратное
Сумма (/sum) - Сложить два числа
Вычитание (/sub) - Вычесть числа
Умножение (/mul) - Умножить числа
Деление (/div) - Разделить числа
Все операции (/all) - Показать все операции
Квадратное уравнение (/quadratic) - Решить уравнение
Помощь (/help) - Показать справку

*Как использовать:*
1. Нажмите на кнопку с нужной операцией
2. Затем отправьте числа через пробел (например: 5 10)
"""
    await update.message.reply_text(help_text,
                                    parse_mode="Markdown",
                                    reply_markup=get_main_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


async def start_operation(update: Update, context: ContextTypes.DEFAULT_TYPE, operation: str):
    context.user_data['operation'] = operation
    await update.message.reply_text(
        f"Отправьте мне числа для операции {operation} (через пробел)\n"
        "Например: 5 10",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Отмена")]], resize_keyboard=True)
    )
    return WAITING_NUMBERS


async def gcd_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start_operation(update, context, "НОД")


async def lcm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start_operation(update, context, "НОК")


async def sum_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start_operation(update, context, "суммы")


async def sub_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start_operation(update, context, "вычитания")


async def mul_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start_operation(update, context, "умножения")


async def div_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start_operation(update, context, "деления")


async def all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start_operation(update, context, "всех операций")


async def quadratic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start_operation(update, context, "квадратного уравнения")


async def handle_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == "отмена":
        await update.message.reply_text("Операция отменена", reply_markup=get_main_keyboard())
        return ConversationHandler.END

    operation = context.user_data.get('operation')
    if not operation:
        await update.message.reply_text("Сначала выберите операцию", reply_markup=get_main_keyboard())
        return ConversationHandler.END

    try:
        text = update.message.text
        if operation == "квадратного уравнения":
            numbers = list(map(float, text.split()))
            if len(numbers) != 3:
                raise ValueError("Для квадратного уравнения нужно 3 числа (a b c)")
            a, b, c = numbers

            equation = f"{a}x²" + (f" + {b}x" if b >= 0 else f" - {-b}x") + (
                f" + {c}" if c >= 0 else f" - {-c}") + " = 0"

            if a == 0:
                if b == 0:
                    if c == 0:
                        response = "Уравнение 0 = 0 имеет бесконечно много решений"
                    else:
                        response = f"Уравнение {c} = 0 не имеет решений"
                else:
                    x = -c / b
                    response = (
                        f"🔢 *Уравнение:* {equation}\n\n"
                        "Это линейное уравнение (a = 0)\n\n"
                        f"Решение:\n"
                        f"{b}x + {c} = 0\n"
                        f"{b}x = {-c}\n"
                        f"x = {-c}/{b}\n"
                        f"x = {x:.2f}"
                    )

                # Построение графика для линейного уравнения
                plt.figure()
                x_vals = np.linspace(-10, 10, 400)
                if b == 0:
                    y_vals = np.full_like(x_vals, c)
                    equation_line = f'y = {c}'
                else:
                    y_vals = b * x_vals + c
                    equation_line = f'y = {b}x + {c}'
                plt.plot(x_vals, y_vals, label=equation_line)
                plt.axhline(0, color='black', linewidth=0.5)
                plt.axvline(0, color='black', linewidth=0.5)
                if b != 0:
                    x_sol = -c / b
                    plt.scatter([x_sol], [0], color='green', label='Решение')
                plt.title('График уравнения')
                plt.xlabel('x')
                plt.ylabel('y')
                plt.grid(True)
                plt.legend()

                buf = BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                plt.close()

                await update.message.reply_photo(photo=buf, caption=response, parse_mode="Markdown",
                                                 reply_markup=get_main_keyboard())
                return ConversationHandler.END

            D = b ** 2 - 4 * a * c
            sqrt_D = cmath.sqrt(D) if D < 0 else math.sqrt(D)

            solution = f"🔢 *Уравнение:* {equation}\n\n"
            solution += f"1. Находим дискриминант:\nD = b² - 4ac = {b}² - 4·{a}·{c} = {b ** 2} - {4 * a * c} = {D}\n\n"

            if D > 0:
                x1 = (-b + sqrt_D) / (2 * a)
                x2 = (-b - sqrt_D) / (2 * a)
                solution += (
                    f"2. D > 0 ⇒ уравнение имеет 2 действительных корня:\n\n"
                    f"x₁ = (-b + √D)/(2a) = ({-b} + {math.sqrt(D):.2f})/(2·{a}) = {x1:.2f}\n"
                    f"x₂ = (-b - √D)/(2a) = ({-b} - {math.sqrt(D):.2f})/(2·{a}) = {x2:.2f}"
                )
            elif D == 0:
                x = -b / (2 * a)
                solution += (
                    f"2. D = 0 ⇒ уравнение имеет 1 действительный корень:\n\n"
                    f"x = -b/(2a) = {-b}/(2·{a}) = {x:.2f}"
                )
            else:
                x1 = (-b + sqrt_D) / (2 * a)
                x2 = (-b - sqrt_D) / (2 * a)
                solution += (
                    f"2. D < 0 ⇒ уравнение имеет 2 комплексных корня:\n\n"
                    f"x₁ = (-b + √D)/(2a) = ({-b} + {sqrt_D:.2f})/(2·{a}) ≈ {x1:.2f}\n"
                    f"x₂ = (-b - √D)/(2a) = ({-b} - {sqrt_D:.2f})/(2·{a}) ≈ {x2:.2f}"
                )

            # Построение графика квадратного уравнения
            plt.figure()
            x_vertex = -b / (2 * a)
            y_vertex = a * x_vertex ** 2 + b * x_vertex + c
            x_min = x_vertex - 10
            x_max = x_vertex + 10
            x_vals = np.linspace(x_min, x_max, 400)
            y_vals = a * x_vals ** 2 + b * x_vals + c

            plt.plot(x_vals, y_vals, label=f'y = {a}x² + {b}x + {c}')
            plt.axhline(0, color='black', linewidth=0.5)
            plt.axvline(0, color='black', linewidth=0.5)
            plt.scatter(x_vertex, y_vertex, color='red', label='Вершина')

            if D >= 0:
                x1_real = x1.real if isinstance(x1, complex) else x1
                x2_real = x2.real if isinstance(x2, complex) else x2
                plt.scatter([x1_real, x2_real], [0, 0], color='green', label='Корни')

            plt.title('График квадратного уравнения')
            plt.xlabel('x')
            plt.ylabel('y')
            plt.grid(True)
            plt.legend()

            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plt.close()

            await update.message.reply_photo(photo=buf, caption=solution, parse_mode="Markdown",
                                             reply_markup=get_main_keyboard())
            return ConversationHandler.END

        else:
            numbers = list(map(float, text.split()))
            if len(numbers) != 2:
                raise ValueError("Нужно отправить ровно два числа через пробел")
            a, b = numbers

            if operation == "НОД":
                result = math.gcd(int(a), int(b))
                response = f"НОД чисел {int(a)} и {int(b)} = {result}"

            elif operation == "НОК":
                gcd = math.gcd(int(a), int(b))
                result = (int(a) * int(b)) // gcd
                response = f"НОК чисел {int(a)} и {int(b)} = {result}"

            elif operation == "суммы":
                result = a + b
                response = f"{a} + {b} = {result}"

            elif operation == "вычитания":
                result = a - b
                response = f"{a} - {b} = {result}"

            elif operation == "умножения":
                result = a * b
                response = f"{a} × {b} = {result}"

            elif operation == "деления":
                if b == 0:
                    response = "⚠ Ошибка! На ноль делить нельзя!"
                else:
                    result = a / b
                    response = f"{a} ÷ {b} = {result:.2f}"

            elif operation == "всех операций":
                gcd = math.gcd(int(a), int(b))
                lcm = (int(a) * int(b)) // gcd
                sum_ab = a + b
                sub_ab = a - b
                sub_ba = b - a
                mul_ab = a * b

                if b != 0:
                    div_ab = f"{a} ÷ {b} = {a / b:.2f}"
                else:
                    div_ab = "Деление на ноль невозможно!"

                response = (
                    f"🔢 *Все операции для чисел {a} и {b}:*\n\n"
                    f"▪ НОД (наибольший общий делитель) = {gcd}\n"
                    f"▪ НОК (наименьшее общее кратное) = {lcm}\n"
                    f"▪ Сумма: {a} + {b} = {sum_ab}\n"
                    f"▪ Разность: {a} - {b} = {sub_ab}\n"
                    f"▪ Обратная разность: {b} - {a} = {sub_ba}\n"
                    f"▪ Произведение: {a} × {b} = {mul_ab}\n"
                    f"▪ Деление: {div_ab}"
                )

            await update.message.reply_text(
                response,
                parse_mode="Markdown" if operation == "всех операций" else None,
                reply_markup=get_main_keyboard()
            )

    except ValueError as e:
        await update.message.reply_text(
            f"⚠ Ошибка! {str(e)}\nПопробуйте еще раз или нажмите 'Отмена'",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Отмена")]], resize_keyboard=True)
        )
        return WAITING_NUMBERS
    except Exception as e:
        await update.message.reply_text(
            "⚠ Произошла ошибка при обработке чисел",
            reply_markup=get_main_keyboard()
        )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена", reply_markup=get_main_keyboard())
    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("gcd", gcd_command),
            CommandHandler("lcm", lcm_command),
            CommandHandler("sum", sum_command),
            CommandHandler("sub", sub_command),
            CommandHandler("mul", mul_command),
            CommandHandler("div", div_command),
            CommandHandler("all", all_command),
            CommandHandler("quadratic", quadratic_command),
        ],
        states={
            WAITING_NUMBERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_numbers)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("Бот запущен...")
    app.run_polling()


if __name__ == '__main__':
    main()
