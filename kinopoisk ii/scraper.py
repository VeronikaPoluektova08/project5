# -- coding: utf-8 --
"""
Нейро-критик Кинопоиска
Анализ тональности отзывов с Кинопоиска.
"""

import threading
import time
import re
from collections import Counter
import sys

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

# ---------- Utilities: Scraper using Selenium ----------
def create_driver(headless=True):
    """Настраивает и возвращает экземпляр WebDriver."""
    options = Options()
    if headless:
        # Рекомендуемый новый headless режим для современных версий Chrome
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1200,1000")
    options.add_argument("--lang=ru-RU")
    # Предотвращение обнаружения автоматизации
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Установка драйвера через webdriver-manager
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except WebDriverException as e:
        raise RuntimeError(f"Не удалось запустить Chrome WebDriver. Убедитесь, что Chrome установлен, и проверьте права доступа. Детали: {e}")

def load_full_reviews_page(driver, url, max_scroll_seconds=15):
    """Загружает страницу и прокручивает её, чтобы подгрузить все отзывы."""
    driver.set_page_load_timeout(30)
    try:
        driver.get(url)
    except TimeoutException:
        print("Предупреждение: Таймаут загрузки страницы.")
        pass
    except WebDriverException as e:
        raise RuntimeError(f"Ошибка при обращении к URL: {e}")

    time.sleep(3)
    end_time = time.time() + max_scroll_seconds
    
    # Клик по кнопке "Читать рецензию полностью"
    try:
        read_more_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Читать рецензию полностью')]")
        for btn in read_more_buttons:
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.1)
    except:
        pass
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    while time.time() < end_time:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            buttons = driver.find_elements(By.XPATH,
                "//button[contains(., 'Показать') or contains(., 'Ещё') or contains(., 'Загрузить ещё') or contains(., 'Показать ещё')]")
            clicked = False
            for b in buttons:
                try:
                    if b.is_displayed() and b.is_enabled():
                        driver.execute_script("arguments[0].click();", b)
                        clicked = True
                        time.sleep(1.0)
                except Exception:
                    pass
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height and not clicked:
                break
            last_height = new_height
        except Exception:
            time.sleep(1)

    time.sleep(1)
    return driver.page_source

# ---------- Extract reviews from HTML ----------
def extract_reviews_from_html(html, max_reviews=200):
    soup = BeautifulSoup(html, "html.parser")
    reviews = []

    selectors = [
        'div[data-test="review-snippet-wrapper"]',
        '[itemprop="reviewBody"]',
        '.styles_reviewText',
        'div[class*="styles_reviewContent"]',
        'div[class*="styles_text"]',
    ]

    for sel in selectors:
        for el in soup.select(sel):
            t = el.get_text(" ", strip=True)
            if t and len(t) >= 50:
                reviews.append(t)
        if reviews:
            break

    unique = []
    seen = set()
    for r in reviews:
        norm = re.sub(r'\s+', ' ', r).strip()
        if norm and len(norm) > 50 and norm not in seen:
            seen.add(norm)
            unique.append(norm)
            if len(unique) >= max_reviews:
                break
    return unique

# ---------- Sentiment analysis ----------
class SentimentAnalyzer:
    def __init__(self, model_name="blanchefort/rubert-base-cased-sentiment", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        if self.device == "cuda":
            print("Используется CUDA (GPU)")
        else:
            print("Используется CPU")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        self.id2label = getattr(self.model.config, "id2label", {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"})

    def predict(self, texts, batch_size=8):
        out = []
        label_map = {"POSITIVE": "Положительный", "NEGATIVE": "Отрицательный", "NEUTRAL": "Нейтральный"}
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            enc = self.tokenizer(batch, padding=True, truncation=True, max_length=512, return_tensors="pt")
            enc = {k: v.to(self.device) for k, v in enc.items()}
            with torch.no_grad():
                logits = self.model(**enc).logits
                probs = F.softmax(logits, dim=-1).cpu()
            for p in probs:
                idx = int(torch.argmax(p).item())
                label_raw = self.id2label.get(idx, "NEUTRAL")
                label = label_map.get(label_raw, label_raw)
                confidence = float(p.max().item())
                out.append((label, confidence))
        return out

# ---------- GUI Application ----------
class NeuroCriticApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Нейро-критик Кинопоиска")
        self.geometry("1100x700")
        self.resizable(True, True)

        # Верхняя панель управления
        frm_top = ttk.Frame(self, padding=8)
        frm_top.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(frm_top, text="URL страницы с отзывами Кинопоиска:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar(value="https://www.kinopoisk.ru/film/1346361/")
        entry = ttk.Entry(frm_top, textvariable=self.url_var, width=80)
        entry.pack(side=tk.LEFT, padx=(8,8))
        self.btn_start = ttk.Button(frm_top, text="Запустить анализ", command=self.on_start_pressed)
        self.btn_start.pack(side=tk.LEFT)

        # Главная область (слева - отзывы, справа - график)
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Левая панель (Отзывы)
        left_pane = ttk.Frame(paned_window, padding="0 0 8 0")
        paned_window.add(left_pane, weight=2)
        ttk.Label(left_pane, text="Отзывы (анализ):").pack(anchor=tk.W)
        self.reviews_tree = ttk.Treeview(left_pane, columns=("sentiment","score"), show="headings", height=20)
        self.reviews_tree.heading("sentiment", text="Тональность")
        self.reviews_tree.heading("score", text="Дов. (0-1)")
        self.reviews_tree.column("sentiment", width=100, anchor=tk.CENTER)
        self.reviews_tree.column("score", width=60, anchor=tk.CENTER)
        self.reviews_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Label(left_pane, text="Полный текст выделенного отзыва:").pack(anchor=tk.W, pady=(6,0))
        self.full_text = scrolledtext.ScrolledText(left_pane, height=8, wrap=tk.WORD, font=('Arial', 10))
        self.full_text.pack(fill=tk.X, expand=False)
        self.reviews_tree.bind("<<TreeviewSelect>>", self.on_review_select)

        # Правая панель (Статистика)
        right_pane = ttk.Frame(paned_window, padding="8 0 0 0")
        paned_window.add(right_pane, weight=1)
        ttk.Label(right_pane, text="Сводная статистика:").pack(anchor=tk.W)
        self.summary_label = ttk.Label(right_pane, text="Нет данных", justify=tk.LEFT, font=('Arial', 10, 'bold'))
        self.summary_label.pack(anchor=tk.W, pady=(4,8))
        self.fig = Figure(figsize=(4.5,4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_pane)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Строка статуса
        self.status_var = tk.StringVar(value="Инициализация...")
        status = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)

        self.reviews = []
        self.analysis = []
        self.sentiment = None
        self._prepare_sentiment_analyzer_async()

    def _prepare_sentiment_analyzer_async(self):
        def target():
            try:
                self._set_status("Загружаю модель тональности (может занять время)...")
                self.sentiment = SentimentAnalyzer()
                self._set_status("Модель загружена. Вставьте URL и нажмите 'Запустить анализ'.")
                self.btn_start.config(state=tk.NORMAL)
            except RuntimeError as e:
                self._set_status(f"Критическая ошибка WebDriver: {e}")
                messagebox.showerror("Ошибка", f"Критическая ошибка WebDriver. Невозможно продолжить:\n{e}")
                self.btn_start.config(state=tk.DISABLED)
            except Exception as e:
                self._set_status(f"Ошибка загрузки модели: {e}")
                messagebox.showerror("Ошибка", f"Не удалось загрузить модель с Hugging Face. Проверьте подключение к интернету:\n{e}")
                self.btn_start.config(state=tk.DISABLED)
        self.btn_start.config(state=tk.DISABLED)
        threading.Thread(target=target, daemon=True).start()

    def _set_status(self, text):
        try:
            self.status_var.set(text)
        except Exception:
            pass

    def on_start_pressed(self):
        url = self.url_var.get().strip()
        if not url.startswith("http"):
            messagebox.showwarning("Ввод", "URL должен начинаться с http/https")
            return
        if self.sentiment is None:
            messagebox.showwarning("Статус", "Модель еще не загружена. Подождите.")
            return
        self._set_status("Запуск анализа...")
        self.btn_start.config(state=tk.DISABLED)
        threading.Thread(target=self.run_full_pipeline, args=(url,), daemon=True).start()

    def run_full_pipeline(self, url):
        driver = None
        try:
            self.clear_results()
            self._set_status("1/3: Загрузка страницы...")
            driver = create_driver(headless=True)
            page_html = load_full_reviews_page(driver, url)

            self._set_status("2/3: Извлечение отзывов...")
            reviews = extract_reviews_from_html(page_html)
            if not reviews:
                self._set_status("Отзывы не найдены.")
                messagebox.showinfo("Результат", "Не удалось извлечь отзывы. Убедитесь, что это страница отзывов, или попробуйте другую ссылку.")
                return
            self.reviews = reviews
            self._set_status(f"3/3: Найдено {len(reviews)} отзывов. Анализ тональности...")
            self.analysis = self.sentiment.predict(reviews, batch_size=8)
            self._set_status(f"Готово. Проанализировано {len(reviews)} отзывов.")
            self.after(0, self.update_results_ui)
        except RuntimeError as e:
            self._set_status(f"Ошибка сбора данных: {e}")
            self.after(0, lambda: messagebox.showerror("Ошибка сбора данных", str(e)))
        except Exception as e:
            self._set_status(f"Неизвестная ошибка: {e}")
            self.after(0, lambda: messagebox.showerror("Ошибка", f"Произошла ошибка: {e}"))
        finally:
            self.after(0, lambda: self.btn_start.config(state=tk.NORMAL))
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    def clear_results(self):
        for i in self.reviews_tree.get_children():
            self.reviews_tree.delete(i)
        self.full_text.delete("1.0", tk.END)
        self.ax.clear()
        self.ax.set_title("Распределение тональности")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()
        self.summary_label.config(text="Нет данных")

    def update_results_ui(self):
        self.clear_results()
        for idx, (label, score) in enumerate(self.analysis):
            tag = "pos" if label == "Положительный" else "neg" if label == "Отрицательный" else "neu"
            self.reviews_tree.insert("", "end", iid=str(idx), tags=(tag,), values=(label, f"{score:.2f}"))
        self.reviews_tree.tag_configure('pos', background='#e6ffe6', foreground='#006600')
        self.reviews_tree.tag_configure('neg', background='#ffe6e6', foreground='#cc0000')
        self.reviews_tree.tag_configure('neu', background='#ffffe6', foreground='#996600')

        counts = Counter([lbl for lbl, _ in self.analysis])
        total = sum(counts.values()) or 1
        pos, neu, neg = counts.get("Положительный", 0), counts.get("Нейтральный", 0), counts.get("Отрицательный", 0)
        summary = f"Всего проанализировано: {total}\n"
        summary += f"🟢 Положительных: {pos} ({pos/total:.1%})\n"
        summary += f"🟡 Нейтральных: {neu} ({neu/total:.1%})\n"
        summary += f"🔴 Отрицательных: {neg} ({neg/total:.1%})"
        rec = self.make_recommendation(pos, neg, total)
        self.summary_label.config(text=summary + f"\n\n👉 Рекомендация: {rec}")

        self.ax.clear()
        if total:
            labels = ["Положительные", "Нейтральные", "Отрицательные"]
            sizes = [pos, neu, neg]
            colors = ["#2D9230", "#FFAA0D", "#F71000"]
            filtered_data = [(l, s, c) for l, s, c in zip(labels, sizes, colors) if s > 0]
            self.ax.pie([s for l, s, c in filtered_data], labels=[l for l, s, c in filtered_data],
                        autopct="%1.1f%%", colors=[c for l, s, c in filtered_data], startangle=90)
            self.ax.axis('equal')
        self.ax.set_title("Распределение тональности")
        self.canvas.draw()

    def on_review_select(self, event):
        sel = self.reviews_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if idx < len(self.analysis) and idx < len(self.reviews):
            lbl, score = self.analysis[idx]
            txt = self.reviews[idx]
            self.full_text.delete("1.0", tk.END)
            self.full_text.insert(tk.END, f"[{lbl} | Достоверность: {score:.2f}]\n\n{txt}")

    def make_recommendation(self, pos, neg, total):
        if total == 0:
            return "Нет данных"
        pos_ratio, neg_ratio = pos / total, neg / total
        if pos_ratio >= 0.7:
            return "Абсолютно рекомендуется к просмотру!"
        elif pos_ratio >= 0.55:
            return "Скорее рекомендуется, позитивных отзывов большинство"
        elif neg_ratio >= 0.7:
            return "Лучше воздержаться, крайне много негатива"
        elif neg_ratio >= 0.5:
            return "Много отрицательных отзывов, смотрите на свой страх и риск"
        return "Отзывы смешанные, нет явного перевеса в какую-либо сторону."


def main():
    app = NeuroCriticApp()
    app.mainloop()

if __name__ == "__main__":
    main()