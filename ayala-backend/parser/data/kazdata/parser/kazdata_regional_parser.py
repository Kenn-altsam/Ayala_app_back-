from playwright.sync_api import sync_playwright
import csv
import time
import os
import re
from typing import Dict, List

class KazDataRegionalParser:
    """
    Единый парсер для сбора данных по всем регионам Казахстана с KazDATA
    """
    
    def __init__(self):
        # Все известные региональные URL с различными КРП кодами
        self.regional_urls = {
            'pavlodar': [
                'https://kazdata.kz/04/2015-kazakhstan-pavlodar-i-oblast-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-pavlodar-i-oblast-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-pavlodar-i-oblast-305.html'
            ],
            'almaty_oblast': [
                'https://kazdata.kz/04/2015-kazakhstan-almaty-oblast-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-almaty-oblast-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-almaty-oblast-305.html',
                'https://kazdata.kz/04/2015-kazakhstan-almaty-i-oblast-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-taldykorgan-i-oblast-311.html'
            ],
            'astana': [
                'https://kazdata.kz/04/2015-kazakhstan-astana-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-astana-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-astana-305.html'
            ],
            'almaty_city': [
                'https://kazdata.kz/04/2015-kazakhstan-almaty-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-almaty-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-almaty-305.html'
            ],
            'shymkent': [
                'https://kazdata.kz/04/2015-kazakhstan-shymkent-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-shymkent-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-shymkent-305.html'
            ],
            'karaganda': [
                'https://kazdata.kz/04/2015-kazakhstan-karaganda-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-karaganda-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-karaganda-305.html'
            ],
            'aktobe': [
                'https://kazdata.kz/04/2015-kazakhstan-aktobe-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-aktobe-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-aktobe-305.html'
            ],
            'atyrau': [
                'https://kazdata.kz/04/2015-kazakhstan-atyrau-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-atyrau-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-atyrau-305.html'
            ],
            'kostanay': [
                'https://kazdata.kz/04/2015-kazakhstan-kostanay-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-kostanay-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-kostanay-305.html'
            ],
            'mangistau': [
                'https://kazdata.kz/04/2015-kazakhstan-aktau-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-aktau-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-aktau-305.html'
            ],
            'semey': [
                'https://kazdata.kz/04/2015-kazakhstan-semey-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-semey-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-semey-305.html'
            ],
            'oral': [
                'https://kazdata.kz/04/2015-kazakhstan-oral-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-oral-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-oral-305.html'
            ],
            'taraz': [
                'https://kazdata.kz/04/2015-kazakhstan-taraz-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-taraz-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-taraz-305.html'
            ],
            'kokshetau': [
                'https://kazdata.kz/04/2015-kazakhstan-kokshetau-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-kokshetau-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-kokshetau-305.html'
            ],
            'petropavlovsk': [
                'https://kazdata.kz/04/2015-kazakhstan-petropavlovsk-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-petropavlovsk-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-petropavlovsk-305.html'
            ],
            'turkestan': [
                'https://kazdata.kz/04/2015-kazakhstan-turkestan-311.html',
                'https://kazdata.kz/04/2015-kazakhstan-turkestan-310.html',
                'https://kazdata.kz/04/2015-kazakhstan-turkestan-305.html'
            ]
        }
        
        self.companies_by_region = {}
    
    def parse_single_page(self, url: str, region: str, browser) -> List[Dict]:
        """
        Парсит одну страницу и возвращает список компаний
        """
        companies = []
        page = browser.new_page()
        
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        try:
            print(f"    Парсинг: {url}")
            page.goto(url, timeout=30000)
            time.sleep(2)
            
            # Пробуем различные селекторы для поиска таблицы
            selectors_to_try = [
                'table.sp tbody tr',
                'table.sp tr',
                'table tbody tr',
                'table tr',
                '.sp tbody tr',
                '.sp tr'
            ]
            
            for selector in selectors_to_try:
                try:
                    rows = page.locator(selector).all()
                    if len(rows) > 1:
                        companies_found = 0
                        
                        for row in rows:
                            try:
                                cells = row.locator('td, th').all()
                                
                                if len(cells) >= 8:
                                    bin_text = cells[0].inner_text().strip()
                                    
                                    # Проверяем, что это БИН (только цифры, длина >= 10)
                                    if bin_text.isdigit() and len(bin_text) >= 10:
                                        company_data = {
                                            'bin': bin_text,
                                            'name': cells[1].inner_text().strip(),
                                            'oked': cells[2].inner_text().strip(),
                                            'industry': cells[3].inner_text().strip(),
                                            'kato': cells[4].inner_text().strip(),
                                            'settlement': cells[5].inner_text().strip(),
                                            'krp': cells[6].inner_text().strip(),
                                            'company_size': cells[7].inner_text().strip().replace('\n', ' '),
                                            'region': region,
                                            'source_url': url
                                        }
                                        
                                        # Очищаем данные от лишних пробелов
                                        for key, value in company_data.items():
                                            if isinstance(value, str):
                                                company_data[key] = ' '.join(value.split())
                                        
                                        companies.append(company_data)
                                        companies_found += 1
                                        
                            except Exception:
                                continue
                        
                        if companies_found > 0:
                            print(f"      ✅ Найдено {companies_found} компаний")
                            break
                            
                except Exception:
                    continue
            
            if not companies:
                print(f"      ❌ Данные не найдены")
                
        except Exception as e:
            print(f"      ❌ Ошибка: {str(e)[:100]}...")
        finally:
            page.close()
        
        return companies
    
    def parse_all_regions(self):
        """
        Парсит все регионы
        """
        print("🇰🇿 Парсинг всех региональных данных KazDATA")
        print("=" * 70)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            
            try:
                total_regions_processed = 0
                total_companies_found = 0
                
                for region, urls in self.regional_urls.items():
                    print(f"\n📍 Регион: {region.upper()}")
                    region_companies = []
                    
                    for url in urls:
                        companies = self.parse_single_page(url, region, browser)
                        region_companies.extend(companies)
                        
                        # Небольшая пауза между запросами
                        time.sleep(1)
                    
                    if region_companies:
                        # Удаляем дубликаты по БИН
                        unique_companies = {}
                        for company in region_companies:
                            bin_number = company['bin']
                            if bin_number not in unique_companies:
                                unique_companies[bin_number] = company
                        
                        region_companies = list(unique_companies.values())
                        self.companies_by_region[region] = region_companies
                        
                        print(f"  ✅ Итого уникальных компаний для {region}: {len(region_companies)}")
                        total_companies_found += len(region_companies)
                        total_regions_processed += 1
                    else:
                        print(f"  ❌ Данные для {region} не найдены")
                
                print(f"\n" + "=" * 70)
                print(f"🎯 ИТОГИ ПАРСИНГА:")
                print(f"   Регионов обработано: {total_regions_processed}")
                print(f"   Всего компаний найдено: {total_companies_found}")
                
            finally:
                browser.close()
    
    def save_regional_data(self):
        """
        Сохраняет данные каждого региона в отдельный CSV файл
        """
        # Создаем директорию kazdata
        kazdata_dir = 'kazdata'
        os.makedirs(kazdata_dir, exist_ok=True)
        
        fieldnames = [
            'bin', 'name', 'oked', 'industry', 'kato', 
            'settlement', 'krp', 'company_size', 'region', 'source_url'
        ]
        
        print(f"\n💾 Сохранение данных в директорию /{kazdata_dir}/")
        print("-" * 50)
        
        total_files_created = 0
        
        for region, companies in self.companies_by_region.items():
            if companies:
                filename = f"{kazdata_dir}/{region}_large_companies.csv"
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(companies)
                
                print(f"✅ {region}_large_companies.csv - {len(companies)} компаний")
                total_files_created += 1
        
        # Также создаем общий сводный файл
        if self.companies_by_region:
            all_companies = []
            for companies in self.companies_by_region.values():
                all_companies.extend(companies)
            
            summary_filename = f"{kazdata_dir}/all_regions_summary.csv"
            with open(summary_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_companies)
            
            print(f"✅ all_regions_summary.csv - {len(all_companies)} компаний (сводный)")
            total_files_created += 1
        
        print(f"\n📊 Создано файлов: {total_files_created}")
        return total_files_created
    
    def show_statistics(self):
        """
        Показывает подробную статистику по регионам
        """
        if not self.companies_by_region:
            print("Нет данных для показа статистики")
            return
        
        print(f"\n📈 ПОДРОБНАЯ СТАТИСТИКА")
        print("=" * 70)
        
        # Сортируем регионы по количеству компаний
        sorted_regions = sorted(
            self.companies_by_region.items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )
        
        for region, companies in sorted_regions:
            print(f"{region.ljust(20)} | {len(companies):>4} компаний")
        
        # Статистика по размерам предприятий
        krp_stats = {}
        for companies in self.companies_by_region.values():
            for company in companies:
                krp = company.get('krp', 'unknown')
                krp_stats[krp] = krp_stats.get(krp, 0) + 1
        
        print(f"\n📊 По размерам предприятий (КРП):")
        for krp, count in sorted(krp_stats.items()):
            krp_name = {
                '311': 'Крупные (1001+ чел.)',
                '310': 'Крупные (501-1000 чел.)', 
                '305': 'Крупные (251-500 чел.)'
            }.get(krp, f'КРП {krp}')
            print(f"  {krp_name}: {count} компаний")

def main():
    """
    Основная функция
    """
    parser = KazDataRegionalParser()
    
    print("🚀 Запуск полного парсинга региональных данных KazDATA")
    print("Будут созданы файлы формата: {region}_large_companies.csv")
    print("Директория сохранения: /kazdata/")
    
    # Парсинг всех регионов
    parser.parse_all_regions()
    
    if parser.companies_by_region:
        # Сохранение данных
        files_created = parser.save_regional_data()
        
        # Статистика
        parser.show_statistics()
        
        print(f"\n🎉 ПАРСИНГ ЗАВЕРШЕН УСПЕШНО!")
        print(f"📁 Проверьте директорию /kazdata/ - создано {files_created} файлов")
    else:
        print("\n❌ Данные не получены. Возможны проблемы с доступом к сайту.")

if __name__ == "__main__":
    main()

def parse_kyzylorda_companies(html_data):
    """
    Parses company data from Kyzylorda region HTML and returns a list of company dictionaries
    """
    companies = []
    
    # Split the HTML into company blocks
    company_blocks = html_data.split('<li class="flex flex-col border-b py-2">')
    
    for block in company_blocks[1:]:  # Skip first empty element
        try:
            company = {}
            
            # Extract company name
            name_start = block.find('<h2>') + 4
            name_end = block.find('</h2>')
            if name_start > 4 and name_end != -1:
                company['name'] = block[name_start:name_end].strip()
            
            # Extract address
            addr_start = block.find('<p class="text-sm">') + 18
            addr_end = block.find('</p>', addr_start)
            if addr_start > 18 and addr_end != -1:
                company['address'] = block[addr_start:addr_end].strip()
            
            # Extract activity
            activity_start = block.find('<div class="text-sm gap-1">') + 26
            activity_end = block.find('</div>', activity_start)
            if activity_start > 26 and activity_end != -1:
                company['activity'] = block[activity_start:activity_end].strip()
            
            # Extract manager
            manager_start = block.find('text-statsnet flex gap-1 flex-wrap">') + 35
            if manager_start > 35:
                manager_end = block.find('<span class="text-black">', manager_start)
                if manager_end != -1:
                    company['manager'] = block[manager_start:manager_end].strip()
            
            # Extract company size
            size_start = block.find('Малое предприятие')
            if size_start != -1:
                size_text = block[size_start:].split('</p>')[0].strip()
                company['company_size'] = size_text
            
            # Extract BIN
            bin_start = block.find('БИН') + 3
            if bin_start > 3:
                bin_text = block[bin_start:].split('</span>')[0].strip()
                company['bin'] = bin_text
            
            # Extract status (active/inactive)
            if 'ui-status--green' in block:
                company['status'] = 'Активная'
            elif 'ui-status--red' in block:
                company['status'] = 'Неактивная'
            
            # Extract company link
            link_start = block.find('href="') + 6
            link_end = block.find('"', link_start)
            if link_start > 6 and link_end != -1:
                company['link'] = f"https://statsnet.co{block[link_start:link_end]}"
            
            # Clean all text fields
            for key, value in company.items():
                if isinstance(value, str):
                    # Remove extra characters and normalize whitespace
                    cleaned_value = value.replace('>"', '').replace('">', '').replace('>', '')
                    company[key] = ' '.join(cleaned_value.split())
            
            if company.get('name') and company.get('bin'):  # Only add if we have at least name and BIN
                companies.append(company)
                
        except Exception as e:
            print(f"Error parsing company block: {e}")
            continue
    
    return companies

def save_to_csv(companies, filename):
    """
    Saves the parsed company data to a CSV file
    """
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    fieldnames = ['name', 'address', 'activity', 'manager', 'company_size', 'bin', 'status', 'link']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(companies)
    
    print(f"Data saved to {filename}")
    print(f"Total companies: {len(companies)}") 