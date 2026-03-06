#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.exceptions import RequestEntityTooLarge
from playwright.sync_api import sync_playwright
import os
import json
import re
from datetime import datetime
from pathlib import Path
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size (для 8 фото)

# Створюємо папки
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('output', exist_ok=True)

def add_unit_if_needed(value, unit):
    """Додає одиницю виміру до значення, якщо її немає"""
    if not value or not value.strip():
        return value
    value = value.strip()
    # Перевіряємо, чи вже є одиниця виміру
    if unit in value:
        return value
    # Додаємо одиницю виміру
    return f"{value} {unit}"

def format_number_with_spaces(value):
    """Форматує число з пробілами для тисяч (наприклад: 2405600 -> 2 405 600)"""
    if not value or not value.strip():
        return value
    try:
        # Видаляємо всі пробіли та перетворюємо на число
        num_str = value.strip().replace(' ', '').replace(',', '.')
        if '.' in num_str:
            parts = num_str.split('.')
            integer_part = parts[0]
            decimal_part = '.' + parts[1] if len(parts) > 1 else ''
        else:
            integer_part = num_str
            decimal_part = ''
        
        # Форматуємо цілу частину з пробілами
        integer_num = int(integer_part)
        formatted = f"{integer_num:,}".replace(',', ' ')
        
        return formatted + decimal_part
    except (ValueError, AttributeError):
        # Якщо не число, повертаємо як є
        return value

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/download/<filename>')
def download_pdf(filename):
    """Завантаження створеного PDF"""
    try:
        return send_file(f"output/{filename}", as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/generate', methods=['POST'])
def generate_pdf():
    try:
        # Отримуємо дані з форми
        form_data = request.form.to_dict()
        files = request.files.getlist('photos')
        
        # Завантажуємо фото
        uploaded_images = []
        upload_dir = app.config['UPLOAD_FOLDER']
        for i, file in enumerate(files[:8]):
            if file.filename:
                extension = file.filename.rsplit('.', 1)[1]
                filename = f"img_{i+1}_{uuid.uuid4().hex}.{extension}"
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                # Зберігаємо відносний шлях для HTML
                uploaded_images.append(f"uploads/{filename}")
        
        # Читаємо шаблон
        with open('commercial_proposal_final.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Замінюємо дані з автоматичним додаванням одиниць виміру
        # Основні характеристики
        html_content = html_content.replace('MAN TGM 15 290', form_data.get('model', ''))
        html_content = html_content.replace('WMAN16ZZ0MY417832', form_data.get('vin', ''))
        html_content = html_content.replace('2020', form_data.get('year', ''))
        
        # Пробіг - додаємо " км" (не " тис. км")
        mileage = form_data.get('mileage', '')
        if mileage:
            mileage = add_unit_if_needed(mileage, 'км')
            mileage = format_number_with_spaces(mileage.replace(' км', '')) + ' км'
        # Використовуємо більш специфічну заміну з контекстом
        def replace_mileage(match):
            return match.group(1) + (mileage if mileage else '') + match.group(2)
        html_content = re.sub(r'(<span class="spec-label">Пробіг:</span>\s*<span class="spec-value">)559000(</span>)', 
                             replace_mileage, html_content)
        
        html_content = html_content.replace('Білий', form_data.get('color', ''))
        html_content = html_content.replace('Німеччина', form_data.get('country', ''))
        html_content = html_content.replace('Вантажний фургон', form_data.get('body_type', ''))
        html_content = html_content.replace('4×2', form_data.get('wheel_formula', ''))
        html_content = html_content.replace('Дизель', form_data.get('engine_type', ''))
        
        # Об'єм двигуна - додаємо " л"
        engine_volume = form_data.get('engine_volume', '')
        if engine_volume:
            engine_volume = add_unit_if_needed(engine_volume, 'л')
        # Використовуємо більш специфічну заміну з контекстом
        def replace_engine_volume(match):
            return match.group(1) + (engine_volume if engine_volume else '') + match.group(2)
        html_content = re.sub(r'(<span class="spec-label">Об\'єм двигуна:</span>\s*<span class="spec-value">)6\.9(</span>)', 
                             replace_engine_volume, html_content)
        
        # Потужність - додаємо " кВт"
        power = form_data.get('power', '')
        if power:
            power = add_unit_if_needed(power, 'кВт')
        # Використовуємо більш специфічну заміну з контекстом
        def replace_power(match):
            return match.group(1) + (power if power else '') + match.group(2)
        html_content = re.sub(r'(<span class="spec-label">Потужність:</span>\s*<span class="spec-value">)213\.3(</span>)', 
                             replace_power, html_content)
        
        html_content = html_content.replace('Автомат', form_data.get('gearbox', ''))
        
        # Кількість місць - додаємо " місця"
        seats = form_data.get('seats', '')
        if seats:
            seats = add_unit_if_needed(seats, 'місця')
        # Використовуємо більш специфічну заміну з контекстом
        def replace_seats(match):
            return match.group(1) + (seats if seats else '') + match.group(2)
        html_content = re.sub(r'(<span class="spec-label">Кількість місць:</span>\s*<span class="spec-value">)2(</span>)', 
                             replace_seats, html_content)
        
        # Технічний стан - переміщено в кінець Основні характеристики
        def replace_technical_state(match):
            return match.group(1) + (form_data.get('technical_state', '') if form_data.get('technical_state') else '') + match.group(2)
        html_content = re.sub(r'(<span class="spec-label">Технічний стан:</span>\s*<span class="spec-value">)Відмінний(</span>)', 
                             replace_technical_state, html_content)
        
        # Замінюємо ціни з автоматичним додаванням одиниць та форматуванням
        price_with_vat = form_data.get('price_with_vat', '')
        if price_with_vat:
            price_with_vat = format_number_with_spaces(price_with_vat)
            price_with_vat = add_unit_if_needed(price_with_vat, 'грн')
        # Використовуємо більш специфічну заміну з контекстом
        def replace_price_with_vat(match):
            return match.group(1) + (price_with_vat if price_with_vat else '') + match.group(2)
        html_content = re.sub(r'(<div class="price-main">)2405600(</div>)', 
                             replace_price_with_vat, html_content)
        
        price_without_vat = form_data.get('price_without_vat', '')
        if price_without_vat:
            price_without_vat = format_number_with_spaces(price_without_vat)
            price_without_vat = add_unit_if_needed(price_without_vat, 'грн')
        # Використовуємо більш специфічну заміну з контекстом
        def replace_price_without_vat(match):
            return match.group(1) + (price_without_vat if price_without_vat else '') + match.group(2)
        html_content = re.sub(r'(<div class="label">Вартість без ПДВ</div>\s*<div class="value">)2004666\.67(</div>)', 
                             replace_price_without_vat, html_content)
        
        vat = form_data.get('vat', '')
        if vat:
            vat = format_number_with_spaces(vat)
            vat = add_unit_if_needed(vat, 'грн')
        # Використовуємо більш специфічну заміну з контекстом
        def replace_vat(match):
            return match.group(1) + (vat if vat else '') + match.group(2)
        html_content = re.sub(r'(<div class="label">Сума ПДВ</div>\s*<div class="value">)400933\.33(</div>)', 
                             replace_vat, html_content)
        
        # Дубль вартості з ПДВ (замість готівкової вартості)
        price_with_vat_duplicate = form_data.get('price_with_vat', '')
        if price_with_vat_duplicate:
            price_with_vat_duplicate = format_number_with_spaces(price_with_vat_duplicate)
            price_with_vat_duplicate = add_unit_if_needed(price_with_vat_duplicate, 'грн')
        # Використовуємо більш специфічну заміну з контекстом
        def replace_price_with_vat_duplicate(match):
            return match.group(1) + (price_with_vat_duplicate if price_with_vat_duplicate else '') + match.group(2)
        html_content = re.sub(r'(<div class="label">Вартість з ПДВ</div>\s*<div class="value">)2405600(</div>)', 
                             replace_price_with_vat_duplicate, html_content)
        
        
        # Створюємо тимчасову папку для всіх файлів
        temp_folder = f'temp_{uuid.uuid4().hex}'
        os.makedirs(temp_folder, exist_ok=True)
        import shutil
        
        # Створюємо структуру папок в тимчасовій папці
        os.makedirs(os.path.join(temp_folder, 'img', 'logo'), exist_ok=True)
        os.makedirs(os.path.join(temp_folder, 'img', 'qr'), exist_ok=True)
        
        # Копіюємо логотип та QR код
        logo_src = 'img/logo/M-TRUCK logo iron.png'
        logo_dst = os.path.join(temp_folder, 'img', 'logo', 'M-TRUCK logo iron.png')
        if os.path.exists(logo_src):
            shutil.copy2(logo_src, logo_dst)
        
        qr_src = 'img/qr/qrcode.webp'
        qr_dst = os.path.join(temp_folder, 'img', 'qr', 'qrcode.webp')
        if os.path.exists(qr_src):
            shutil.copy2(qr_src, qr_dst)
        
        # Замінюємо і копіюємо фото користувача
        for i in range(8):
            if i < len(uploaded_images) and uploaded_images[i] and os.path.exists(uploaded_images[i]):
                # Копіюємо завантажене фото в тимчасову папку
                src = uploaded_images[i]
                ext = src.split('.')[-1]
                new_img_name = f'img_{i+1}.{ext}'
                dst = os.path.join(temp_folder, new_img_name)
                shutil.copy2(src, dst)
                
                # Замінюємо src в HTML (знаходимо img теги в image-grid)
                # Знаходимо всі img теги (включаючи з порожнім src)
                pattern = r'<img src="[^"]*" alt="Photo [0-9]" loading="lazy">'
                matches = list(re.finditer(pattern, html_content))
                
                if matches and i < len(matches):
                    # Замінюємо src в конкретному img тегу
                    old_tag = matches[i].group(0)
                    new_tag = re.sub(r'src="[^"]*"', f'src="{new_img_name}"', old_tag)
                    html_content = html_content.replace(old_tag, new_tag, 1)
        
        # Зберігаємо тимчасовий HTML
        temp_html = os.path.join(temp_folder, 'template.html')
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Генеруємо PDF
        model_safe = form_data.get('model', 'MAN').replace(' ', '_').replace('/', '_')
        output_file = f"output/Комерційна_пропозиція_{model_safe}.pdf"
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 794, "height": 1123})
            
            html_path = os.path.abspath(temp_html)
            # Форматуємо шлях для file:// протоколу (працює на Windows та macOS)
            if os.name == 'nt':  # Windows
                html_path = html_path.replace('\\', '/')
                if not html_path.startswith('/'):
                    html_path = '/' + html_path
                file_url = f"file://{html_path}"
            else:  # macOS/Linux
                file_url = f"file://{html_path}"
            page.goto(file_url)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            
            page.pdf(
                path=output_file,
                format="A4",
                print_background=True,
                margin={"top": "0.5in", "right": "0.5in", "bottom": "0.5in", "left": "0.5in"},
                prefer_css_page_size=True,
                display_header_footer=False,
                scale=1.0
            )
            
            browser.close()
        
        # Видаляємо тимчасову папку
        import shutil
        shutil.rmtree(temp_folder)

        # Видаляємо завантажені фото з uploads/ (не зберігати їх у проекті)
        try:
            for rel_path in uploaded_images:
                # uploaded_images містить відносні шляхи типу 'uploads/filename.ext'
                abs_path = os.path.abspath(rel_path)
                if abs_path.startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])) and os.path.exists(abs_path):
                    os.remove(abs_path)
        except Exception:
            # Ігноруємо помилки видалення, PDF вже збережений
            pass
        
        filename = output_file.split('/')[-1]
        
        return jsonify({
            'success': True,
            'file': filename,
            'download_url': f'/api/download/{filename}',
            'message': f'✅ PDF успішно створено!'
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': f'{str(e)}\n{traceback.format_exc()}'
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 ГЕНЕРАТОР PDF КОМЕРЦІЙНИХ ПРОПОЗИЦІЙ")
    print("=" * 60)
    print("📱 Відкрийте браузер за адресою: http://localhost:5000")
    print("⏹️  Для зупинки натисніть Ctrl+C")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)

