from playwright.sync_api import sync_playwright
import csv
import time
import os
import re
from typing import List, Dict
from urllib.parse import urljoin

class KazDataCatalogParser:
    def __init__(self):
        self.base_url = "https://kazdata.kz"
        self.catalog_url = "https://kazdata.kz/04/katalog-kazakhstan.html"
        self.companies_by_region = {}
        
    def extract_region_links(self, page) -> Dict[str, List[str]]:
        """
        Извлекает ссылки на страницы с данными компаний для каждого региона
        """
        region_links = {}
        
        try:
            # Ждем загрузки контента
            page.wait_for_selector('a[href*="kazakhstan"]', timeout=10000)
            
            # Получаем все ссылки
            links = page.query_selector_all('a[href*="kazakhstan"]')
            print(f"Найдено {len(links)} ссылок на странице")
            
            for link in links:
                try:
                    href = link.get_attribute('href')
                    text = link.inner_text().strip()
                    
                    # Проверяем, что это ссылка на страницу с компаниями
                    if href and ('311.html' in href or '310.html' in href or '305.html' in href):
                        # Формируем правильный URL с /04/ в пути
                        if not href.startswith('http'):
                            if href.startswith('/'):
                                href = href[1:]  # Убираем начальный слеш если есть
                            if not href.startswith('04/'):
                                href = f"04/{href}"
                            full_url = urljoin(self.base_url, href)
                        else:
                            # Если это полный URL, добавляем /04/ если его нет
                            if '/04/' not in href:
                                parts = href.split('/')
                                domain = '/'.join(parts[:3])  # http://example.com
                                path = '/'.join(parts[3:])    # rest/of/path
                                full_url = f"{domain}/04/{path}"
                            else:
                                full_url = href
                        
                        # Извлекаем название региона из URL
                        region_match = re.search(r'kazakhstan-([a-z-]+)-\d{3}', href)
                        if region_match:
                            region = region_match.group(1)
                            if region not in region_links:
                                region_links[region] = []
                            if full_url not in region_links[region]:
                                region_links[region].append(full_url)
                                print(f"Найдена ссылка для {region}: {full_url}")
                
                except Exception as e:
                    print(f"Ошибка при обработке ссылки: {e}")
                    continue
            
        except Exception as e:
            print(f"Ошибка при извлечении ссылок: {e}")
        
        return region_links

    def parse_company_table(self, page) -> List[Dict]:
        """
        Парсит таблицу с данными компаний
        """
        companies = []
        
        try:
            # Ждем загрузку таблицы
            page.wait_for_selector('table', timeout=15000)
            
            # Получаем все таблицы на странице
            tables = page.query_selector_all('table')
            print(f"Найдено таблиц на странице: {len(tables)}")
            
            for table in tables:
                try:
                    # Проверяем, что это таблица с компаниями (должно быть 8 столбцов)
                    header_cells = table.query_selector_all('tr:first-child td, tr:first-child th')
                    if len(header_cells) >= 8:
                        # Получаем все строки таблицы
                        rows = table.query_selector_all('tr')
                        print(f"Найдено строк в таблице: {len(rows)}")
                        
                        # Пропускаем заголовок
                        for row in rows[1:]:
                            try:
                                cells = row.query_selector_all('td')
                                
                                if len(cells) >= 8:
                                    bin_text = cells[0].inner_text().strip()
                                    
                                    # Проверяем, что это БИН (только цифры)
                                    if bin_text.isdigit() and len(bin_text) >= 10:
                                        company_data = {
                                            'bin': bin_text,
                                            'name': cells[1].inner_text().strip(),
                                            'oked': cells[2].inner_text().strip(),
                                            'industry': cells[3].inner_text().strip(),
                                            'kato': cells[4].inner_text().strip(),
                                            'settlement': cells[5].inner_text().strip(),
                                            'krp': cells[6].inner_text().strip(),
                                            'company_size': cells[7].inner_text().strip().replace('\n', ' ')
                                        }
                                        
                                        # Очищаем данные
                                        for key, value in company_data.items():
                                            if isinstance(value, str):
                                                company_data[key] = ' '.join(value.split())
                                        
                                        companies.append(company_data)
                                        print(f"Добавлена компания: {company_data['name'][:50]}...")
                                    
                            except Exception as e:
                                print(f"Ошибка при парсинге строки: {e}")
                                continue
                        
                        if companies:
                            break  # Если нашли компании в этой таблице, прекращаем поиск
                    
                except Exception as e:
                    print(f"Ошибка при анализе таблицы: {e}")
                    continue
            
        except Exception as e:
            print(f"Ошибка при поиске таблиц: {e}")
        
        return companies

    def parse_region_page(self, url: str, region: str, page) -> List[Dict]:
        """
        Парсит одну страницу региона
        """
        companies = []
        
        try:
            print(f"\nПарсинг страницы {url}")
            page.goto(url, timeout=30000)
            time.sleep(2)  # Даем время на загрузку
            
            companies = self.parse_company_table(page)
            
            # Добавляем информацию о регионе и источнике
            for company in companies:
                company['region'] = region
                company['source_url'] = url
            
            print(f"✅ Найдено {len(companies)} компаний")
            
        except Exception as e:
            print(f"❌ Ошибка при парсинге страницы: {e}")
        
        return companies

    def parse_all_regions(self):
        """
        Парсит данные компаний для всех регионов
        """
        print("🇰🇿 Начинаем парсинг каталога KazDATA")
        print("=" * 60)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            # Устанавливаем User-Agent
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            try:
                # Получаем ссылки на все регионы
                print("Получаем список регионов...")
                page.goto(self.catalog_url, timeout=30000)
                time.sleep(2)
                
                region_links = self.extract_region_links(page)
                print(f"\nНайдено регионов: {len(region_links)}")
                
                # Парсим каждый регион
                total_companies = 0
                
                for region, urls in region_links.items():
                    print(f"\n📍 Регион: {region.upper()}")
                    region_companies = []
                    
                    for url in urls:
                        companies = self.parse_region_page(url, region, page)
                        region_companies.extend(companies)
                        time.sleep(1)  # Пауза между запросами
                    
                    if region_companies:
                        # Удаляем дубликаты по БИН
                        unique_companies = {}
                        for company in region_companies:
                            bin_number = company['bin']
                            if bin_number not in unique_companies:
                                unique_companies[bin_number] = company
                        
                        region_companies = list(unique_companies.values())
                        self.companies_by_region[region] = region_companies
                        
                        total_companies += len(region_companies)
                        print(f"✅ Всего уникальных компаний в {region}: {len(region_companies)}")
                    else:
                        print(f"❌ Компании не найдены в {region}")
                
                print("\n" + "=" * 60)
                print(f"🎯 ИТОГИ ПАРСИНГА:")
                print(f"   Регионов обработано: {len(region_links)}")
                print(f"   Всего компаний найдено: {total_companies}")
                
            except Exception as e:
                print(f"Критическая ошибка: {e}")
            finally:
                browser.close()

    def save_data(self):
        """
        Сохраняет данные в CSV файлы
        """
        # Создаем директорию для данных
        data_dir = 'data/regions'
        os.makedirs(data_dir, exist_ok=True)
        
        fieldnames = [
            'bin', 'name', 'oked', 'industry', 'kato', 
            'settlement', 'krp', 'company_size', 'region', 'source_url'
        ]
        
        print(f"\n💾 Сохранение данных в директорию /{data_dir}/")
        print("-" * 50)
        
        # Сохраняем данные по регионам
        for region, companies in self.companies_by_region.items():
            if companies:
                filename = f"{data_dir}/{region}_companies.csv"
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(companies)
                
                print(f"✅ {region}_companies.csv - {len(companies)} компаний")
        
        # Создаем общий файл со всеми компаниями
        all_companies = []
        for companies in self.companies_by_region.values():
            all_companies.extend(companies)
        
        if all_companies:
            filename = "data/all_kazakhstan_companies.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_companies)
            
            print(f"\n✅ {filename} - {len(all_companies)} компаний")

def main():
    parser = KazDataCatalogParser()
    parser.parse_all_regions()
    parser.save_data()

if __name__ == "__main__":
    main() 