from playwright.sync_api import sync_playwright
import csv
import time
import os

def parse_kazdata_companies():
    """
    Парсит данные крупных предприятий Павлодара с сайта KazDATA
    """
    url = "https://kazdata.kz/04/2015-kazakhstan-pavlodar-i-oblast-311.html"
    companies = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Устанавливаем User-Agent
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        try:
            print(f"Переходим на страницу: {url}")
            page.goto(url, timeout=30000)
            
            # Даем время на загрузку
            time.sleep(3)
            
            # Ищем таблицу с классом "sp"
            try:
                table_selector = 'table.sp'
                page.wait_for_selector(table_selector, timeout=15000)
                print("Таблица найдена, начинаем парсинг...")
                
                # Получаем все строки таблицы (исключая заголовок)
                rows = page.locator(f'{table_selector} tbody tr').all()
                
                if len(rows) <= 1:  # Проверяем наличие данных
                    print("Данные в таблице не найдены")
                    return companies
                
                print(f"Найдено {len(rows) - 1} строк с данными компаний")
                
                # Парсим каждую строку (пропускаем заголовок)
                for i, row in enumerate(rows[1:], 1):
                    try:
                        # Получаем все ячейки строки
                        cells = row.locator('td').all()
                        
                        if len(cells) >= 8:
                            company_data = {
                                'bin': cells[0].inner_text().strip(),
                                'name': cells[1].inner_text().strip(),
                                'oked': cells[2].inner_text().strip(),
                                'industry': cells[3].inner_text().strip(),
                                'kato': cells[4].inner_text().strip(),
                                'settlement': cells[5].inner_text().strip(),
                                'krp': cells[6].inner_text().strip(),
                                'company_size': cells[7].inner_text().strip().replace('\n', ' ')
                            }
                            
                            # Очистка данных
                            for key, value in company_data.items():
                                if isinstance(value, str):
                                    company_data[key] = ' '.join(value.split())
                            
                            if company_data['bin']:  # Проверяем, что БИН не пустой
                                companies.append(company_data)
                                print(f"Добавлена компания {i}: {company_data['name'][:50]}...")
                            else:
                                print(f"Пропущена строка {i}: нет БИН")
                        else:
                            print(f"Пропущена строка {i}: недостаточно ячеек ({len(cells)})")
                            
                    except Exception as e:
                        print(f"Ошибка при парсинге строки {i}: {e}")
                        continue
                
            except Exception as e:
                print(f"Таблица не найдена или ошибка при парсинге: {e}")
                # Пробуем альтернативный селектор
                try:
                    print("Пробуем альтернативный поиск таблицы...")
                    rows = page.locator('table tr').all()
                    print(f"Найдено строк в любой таблице: {len(rows)}")
                    
                    for i, row in enumerate(rows):
                        cells = row.locator('td').all()
                        if len(cells) >= 8:
                            print(f"Строка {i}: {cells[0].inner_text()[:20]} | {cells[1].inner_text()[:30]}")
                except:
                    pass
                
        except Exception as e:
            print(f"Ошибка при загрузке страницы: {e}")
        finally:
            browser.close()
    
    return companies

def save_to_csv(companies, filename):
    """
    Сохраняет данные в CSV файл
    """
    os.makedirs('data', exist_ok=True)
    
    fieldnames = ['bin', 'name', 'oked', 'industry', 'kato', 'settlement', 'krp', 'company_size']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(companies)
    
    print(f"Данные сохранены в файл {filename}")
    print(f"Всего компаний: {len(companies)}")

def main():
    """
    Основная функция
    """
    print("Парсинг крупных предприятий Павлодара с сайта KazDATA.kz")
    print("=" * 60)
    
    companies = parse_kazdata_companies()
    
    if companies:
        filename = "data/pavlodar_large_companies.csv"
        save_to_csv(companies, filename)
        
        print("\n" + "=" * 60)
        print("Парсинг успешно завершен!")
        print(f"Найдено компаний: {len(companies)}")
        
        # Показываем первые несколько компаний
        print("\nПримеры найденных компаний:")
        for i, company in enumerate(companies[:5]):
            print(f"{i+1}. {company['name']} (БИН: {company['bin']})")
    else:
        print("Данные не получены или произошла ошибка")

if __name__ == "__main__":
    main() 