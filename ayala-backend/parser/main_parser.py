from playwright.sync_api import sync_playwright
import csv
import time
import re
import os
import random

# Настройки прокси
USE_PROXY = False  # Установите True чтобы включить прокси
PROXY_ROTATION_INTERVAL = 1000  # Менять прокси каждые N компаний

# Список прокси серверов (только HTTP)
PROXY_LIST = [
    {
        'server': 'http://94.131.2.254:40068',
        'username': 'NuhaiProxy_VP3eYoUt',
        'password': 'Vh0VvZE9'
    }
]

def get_random_proxy():
    """Возвращает случайный прокси из списка или None если прокси отключены"""
    if not USE_PROXY or not PROXY_LIST:
        return None
    return random.choice(PROXY_LIST)

def create_browser_with_proxy(playwright, proxy_config=None, retry_without_proxy=True):
    """Создает браузер с настройками прокси"""
    browser_args = {
        'headless': False,
        'args': ['--disable-blink-features=AutomationControlled']
    }
    
    if proxy_config:
        try:
            browser_args['proxy'] = {
                'server': proxy_config['server'],
                'username': proxy_config['username'],
                'password': proxy_config['password']
            }
            print(f"Использую прокси: {proxy_config['server']}")
            return playwright.chromium.launch(**browser_args)
        except Exception as e:
            print(f"❌ Ошибка подключения к прокси {proxy_config['server']}: {e}")
            if retry_without_proxy:
                print("🔄 Пробую работать без прокси...")
                return create_browser_with_proxy(playwright, None, False)
            else:
                raise e
    else:
        print("Работаю без прокси")
        return playwright.chromium.launch(**browser_args)

def get_company_data(url):
    """
    Получает данные компаний с сайта statsnet.co используя Playwright с ротацией прокси
    """
    companies = []
    total_companies_processed = 0
    failed_companies = 0
    
    with sync_playwright() as p:
        # Начинаем с первого прокси
        current_proxy = get_random_proxy()
        browser = create_browser_with_proxy(p, current_proxy)
        page = browser.new_page()
        
        # Устанавливаем User-Agent и дополнительные настройки
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Устанавливаем размер окна
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        page_num = 1
        
        try:
            while True:
                print(f"\n🔍 Парсинг страницы {page_num}...")
                
                # Формируем URL страницы
                page_url = f"{url}?page={page_num}" if page_num > 1 else url
                
                # Переходим на страницу
                try:
                    print(f"📄 Загружаю: {page_url}")
                    page.goto(page_url, timeout=30000)
                    # Даем время на загрузку JavaScript
                    time.sleep(3)
                except Exception as e:
                    print(f"❌ Ошибка при загрузке страницы: {e}")
                    # Попробуем еще раз с увеличенным таймаутом
                    try:
                        print("🔄 Повторная попытка загрузки...")
                        page.goto(page_url, timeout=60000)
                        time.sleep(5)
                    except Exception as e2:
                        print(f"❌ Повторная ошибка: {e2}")
                        break
                
                # Ждем загрузки элементов компаний
                try:
                    page.wait_for_selector('li.flex.flex-col.border-b.py-2', timeout=15000)
                    print("✅ Элементы компаний найдены")
                except Exception as e:
                    print(f"❌ Элементы компаний не найдены: {e}")
                    # Попробуем найти альтернативные селекторы
                    try:
                        alternative_elements = page.locator('li').all()
                        print(f"🔍 Найдено {len(alternative_elements)} элементов li на странице")
                        if len(alternative_elements) == 0:
                            print("🚫 Страница не содержит ожидаемых элементов. Завершаю парсинг.")
                            break
                    except:
                        print("🚫 Не удалось найти никаких элементов. Завершаю парсинг.")
                        break
                
                # Получаем все элементы компаний
                company_elements = page.locator('li.flex.flex-col.border-b.py-2').all()
                
                if not company_elements:
                    print("🚫 Больше нет данных. Парсинг завершен.")
                    break
                
                print(f"📋 Найдено {len(company_elements)} компаний на странице {page_num}")
                
                page_companies_processed = 0
                page_companies_failed = 0
                
                for i, element in enumerate(company_elements):
                    try:
                        print(f"🔄 Обрабатываю компанию {i+1}/{len(company_elements)}...")
                        company_data = parse_company_element(element)
                        if company_data and company_data.get('name'):
                            companies.append(company_data)
                            total_companies_processed += 1
                            page_companies_processed += 1
                            print(f"✅ Добавлена: {company_data['name'][:50]}...")
                            
                            # Проверяем, нужно ли сменить прокси
                            if USE_PROXY and total_companies_processed % PROXY_ROTATION_INTERVAL == 0:
                                print(f"\n🔄 Смена прокси после {total_companies_processed} компаний...")
                                
                                # Сохраняем текущие данные перед сменой прокси
                                if companies:
                                    temp_filename = f"data/almaty_temp_{total_companies_processed}.csv"
                                    save_to_csv(companies, temp_filename)
                                    companies = []
                                
                                # Закрываем текущий браузер
                                browser.close()
                                
                                # Создаем новый браузер с новым прокси
                                current_proxy = get_random_proxy()
                                browser = create_browser_with_proxy(p, current_proxy)
                                page = browser.new_page()
                                
                                # Восстанавливаем настройки
                                page.set_extra_http_headers({
                                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                                })
                                page.set_viewport_size({"width": 1920, "height": 1080})
                                print("✅ Прокси успешно изменен\n")
                        else:
                            page_companies_failed += 1
                            failed_companies += 1
                            print(f"⚠️ Компания {i+1} не обработана (нет данных)")
                            
                    except Exception as e:
                        page_companies_failed += 1
                        failed_companies += 1
                        print(f"❌ Ошибка при парсинге компании {i+1}: {e}")
                        continue
                
                print(f"📊 Страница {page_num}: обработано {page_companies_processed}, ошибок {page_companies_failed}")
                
                # Сохраняем данные каждые 10 страниц в отдельный файл
                if page_num % 10 == 0 and companies:
                    start_page = page_num - 9
                    end_page = page_num
                    filename = f"data/almaty_pages_{start_page}-{end_page}.csv"
                    save_to_csv(companies, filename)
                    print(f"💾 Сохранено {len(companies)} компаний в файл {filename}")
                    companies = []  # Очищаем список для следующих 10 страниц
                
                page_num += 1
                
                # Небольшая задержка между страницами
                print(f"⏱️ Пауза 3 секунды перед следующей страницей...")
                time.sleep(3)
                
                # Ограничиваем количество страниц для безопасности
                if page_num > 50:  # Максимум 50 страниц
                    print("🛑 Достигнут лимит страниц (50)")
                    break
                    
        except Exception as e:
            print(f"❌ Критическая ошибка при работе с браузером: {e}")
        finally:
            # Сохраняем оставшиеся данные, если есть
            if companies:
                last_full_batch = ((page_num - 1) // 10) * 10
                start_page = last_full_batch + 1
                end_page = page_num - 1
                filename = f"data/almaty_pages_{start_page}-{end_page}.csv"
                save_to_csv(companies, filename)
                print(f"💾 Сохранены оставшиеся {len(companies)} компаний в файл {filename}")
            
            browser.close()
    
    print(f"\n📈 Итоговая статистика:")
    print(f"✅ Всего обработано компаний: {total_companies_processed}")
    print(f"❌ Ошибок при обработке: {failed_companies}")
    
    return companies

def parse_company_element(element):
    """
    Парсит данные одной компании из Playwright элемента
    """
    company_data = {}
    
    try:
        # Название компании
        name_element = element.locator('h2').first
        company_data['name'] = name_element.inner_text().strip() if name_element.count() > 0 else ""
        
        if not company_data['name']:
            return None
        
        # Инициализируем переменные
        address = ""
        activity = ""
        manager = ""
        company_size = ""
        
        # Получаем все параграфы
        paragraphs = element.locator('p').all()
        
        for p in paragraphs:
            try:
                text = p.inner_text().strip()
                
                # Адрес (содержит "Казахстан")
                if "Казахстан" in text:
                    address = text
                
                # Размер предприятия (содержит "чел." или "предприятие")
                elif "чел." in text or "предприятие" in text:
                    company_size = text
                
                # Руководитель (содержит "руководитель")
                elif "руководитель" in text:
                    # Пытаемся получить только имя без "— руководитель"
                    manager_parts = text.split("—")
                    if len(manager_parts) > 1:
                        manager = manager_parts[0].strip()
                    else:
                        manager = text.replace("руководитель", "").strip()
            except:
                continue
        
        # Описание деятельности
        try:
            activity_elements = element.locator('div.text-sm.gap-1').all()
            for activity_div in activity_elements:
                # Проверяем, что это не div с размером компании
                activity_text = activity_div.inner_text().strip()
                if activity_text and "чел." not in activity_text and "предприятие" not in activity_text:
                    activity = activity_text
                    break
        except:
            pass
        
        # БИН и НДС
        bin_number = ""
        nds_number = ""
        
        try:
            # Ищем div с классом d-flex для БИН и НДС
            bin_nds_element = element.locator('div.d-flex').first
            if bin_nds_element.count() > 0:
                text = bin_nds_element.inner_text()
                
                # Извлекаем БИН
                bin_match = re.search(r'БИН\s*(\d+)', text)
                if bin_match:
                    bin_number = bin_match.group(1)
                
                # Извлекаем НДС
                nds_match = re.search(r'НДС\s*([\d-]+)', text)
                if nds_match:
                    nds_number = nds_match.group(1)
        except:
            pass
        
        # Получаем ссылку на компанию
        company_link = ""
        try:
            link_element = element.locator('a[href]').first
            if link_element.count() > 0:
                href = link_element.get_attribute('href')
                if href:
                    company_link = f"https://statsnet.co{href}"
        except:
            pass
        
        # Получаем статус компании (зеленый/красный индикатор)
        status = ""
        try:
            status_element = element.locator('span.ui-status').first
            if status_element.count() > 0:
                status_class = status_element.get_attribute('class')
                if 'ui-status--green' in status_class:
                    status = "Активная"
                elif 'ui-status--red' in status_class:
                    status = "Неактивная"
        except:
            pass
        
        company_data.update({
            'address': address,
            'activity': activity,
            'manager': manager,
            'company_size': company_size,
            'bin': bin_number,
            'nds': nds_number,
            'link': company_link,
            'status': status
        })
        
    except Exception as e:
        print(f"❌ Критическая ошибка при извлечении данных компании: {e}")
        return None
    
    return company_data

def save_to_csv(companies, filename):
    """
    Сохраняет данные компаний в CSV файл
    """
    # Создаем директорию data если она не существует
    os.makedirs('data', exist_ok=True)
    
    fieldnames = ['name', 'address', 'activity', 'manager', 'company_size', 'bin', 'nds', 'link', 'status']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for company in companies:
            # Очищаем данные от лишних пробелов и переносов строк
            cleaned_company = {}
            for key, value in company.items():
                if isinstance(value, str):
                    cleaned_company[key] = ' '.join(value.split())
                else:
                    cleaned_company[key] = value
            writer.writerow(cleaned_company)
    
    print(f"💾 Данные сохранены в файл {filename}")
    print(f"📊 Всего компаний: {len(companies)}")

def merge_csv_files(file_list, output_filename):
    """
    Объединяет несколько CSV файлов в один
    """
    fieldnames = ['name', 'address', 'activity', 'manager', 'company_size', 'bin', 'nds', 'link', 'status']
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for filename in sorted(file_list):
            with open(filename, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    writer.writerow(row)

def main():
    """
    Основная функция
    """
    url = "https://statsnet.co/states/kz/almaty"
    csv_filename = "data/almaty.csv"
    
    print("🚀 Начинаем парсинг данных с сайта statsnet.co с помощью Playwright...")
    print(f"🌐 URL: {url}")
    print(f"📁 Файл для сохранения: {csv_filename}")
    print(f"🔧 Прокси: {'включены' if USE_PROXY else 'отключены'}")
    print("-" * 60)
    
    try:
        companies = get_company_data(url)
        
        print("-" * 60)
        print("🎉 Парсинг успешно завершен!")
        
        # Подсчитываем общее количество компаний из всех файлов
        import glob
        total_companies = 0
        
        # Получаем все файлы (обычные и временные)
        csv_files = glob.glob("data/almaty_pages_*.csv")
        temp_files = glob.glob("data/almaty_temp_*.csv")
        all_files = csv_files + temp_files
        
        if all_files:
            print(f"📁 Создано файлов: {len(all_files)}")
            for file in sorted(all_files):
                with open(file, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines()) - 1  # -1 для заголовка
                    total_companies += lines
                    print(f"  📄 {file}: {lines} компаний")
            
            print(f"\n📈 Всего спарсено: {total_companies} компаний")
            
            # Объединяем все файлы в один итоговый (опционально)
            if len(all_files) > 1:
                print("\n🔄 Объединение всех файлов...")
                merge_csv_files(all_files, "data/almaty_complete.csv")
                print("✅ Все данные объединены в файл data/almaty_complete.csv")
        else:
            print("❌ Файлы с данными не найдены.")
    
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 