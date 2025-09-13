import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import sys # Импортируем модуль sys для работы с аргументами командной строки

def get_all_links(url):
    """
    Извлекает все ссылки с веб-страницы
    """
    try:
        # Отправляем GET-запрос
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Парсим HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Извлекаем все возможные ссылки
        all_links = set()

        # 1. Обычные ссылки (тег <a>)
        for link in soup.find_all('a', href=True):
            absolute_url = urljoin(url, link['href'])
            all_links.add(absolute_url)

        # 2. Изображения (тег <img>)
        for img in soup.find_all('img', src=True):
            absolute_url = urljoin(url, img['src'])
            all_links.add(absolute_url)

        # 3. Скрипты (тег <script>)
        for script in soup.find_all('script', src=True):
            absolute_url = urljoin(url, script['src'])
            all_links.add(absolute_url)

        # 4. CSS (тег <link>)
        for css in soup.find_all('link', href=True):
            absolute_url = urljoin(url, css['href'])
            all_links.add(absolute_url)

        # 5. Видео (тег <video>)
        for video in soup.find_all('video', src=True):
            absolute_url = urljoin(url, video['src'])
            all_links.add(absolute_url)

        # 6. Аудио (тег <audio>)
        for audio in soup.find_all('audio', src=True):
            absolute_url = urljoin(url, audio['src'])
            all_links.add(absolute_url)

        # 7. Source (тег <source>)
        for source in soup.find_all('source', src=True):
            absolute_url = urljoin(url, source['src'])
            all_links.add(absolute_url)

        # 8. Фреймы (тег <iframe>)
        for iframe in soup.find_all('iframe', src=True):
            absolute_url = urljoin(url, iframe['src'])
            all_links.add(absolute_url)

        # 9. Ссылки в мета-тегах
        for meta in soup.find_all('meta', content=True):
            if 'url' in meta.get('property', '').lower() or 'image' in meta.get('property', '').lower():
                absolute_url = urljoin(url, meta['content'])
                all_links.add(absolute_url)

        return sorted(all_links)

    except requests.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return []
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []

def categorize_links(links):
    """
    Категоризирует ссылки по типам
    """
    categories = {
        'images': [],
        'videos': [],
        'documents': [],
        'scripts': [],
        'styles': [],
        'pages': [],
        'other': []
    }

    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico']
    video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
    document_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']
    script_extensions = ['.js']
    style_extensions = ['.css']

    for link in links:
        parsed_url = urlparse(link)
        path = parsed_url.path.lower()

        if any(path.endswith(ext) for ext in image_extensions):
            categories['images'].append(link)
        elif any(path.endswith(ext) for ext in video_extensions):
            categories['videos'].append(link)
        elif any(path.endswith(ext) for ext in document_extensions):
            categories['documents'].append(link)
        elif any(path.endswith(ext) for ext in script_extensions):
            categories['scripts'].append(link)
        elif any(path.endswith(ext) for ext in style_extensions):
            categories['styles'].append(link)
        elif re.search(r'\.(php|html|htm|aspx|jsp)$', path) or path == '/' or path == '':
            categories['pages'].append(link)
        else:
            categories['other'].append(link)

    return categories

def save_to_file(links, filename='links.txt'):
    """
    Сохраняет ссылки в файл
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for link in links:
            f.write(link + '\n')
    print(f"Ссылки сохранены в файл: {filename}")

def main():
    # Проверяем, был ли передан URL как аргумент командной строки
    if len(sys.argv) < 2:
        print("Ошибка: URL не указан.")
        print("Пример использования: python crawler.py https://example.com")
        sys.exit(1) # Выходим из скрипта, если URL не предоставлен

    # Берем URL из первого аргумента командной строки
    url = sys.argv[1]

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    print(f"Сканирование: {url}")
    print("Пожалуйста, подождите...\n")

    # Получаем все ссылки
    all_links = get_all_links(url)

    if not all_links:
        print("Не удалось получить ссылки или сайт не отвечает")
        return

    # Категоризируем ссылки
    categorized = categorize_links(all_links)

    # Выводим результаты
    print(f"Всего найдено ссылок: {len(all_links)}\n")

    for category, links in categorized.items():
        if links:
            print(f"=== {category.upper()} ({len(links)}) ===")
            for link in links:
                print(link)
            print()


    # Сохраняем все ссылки в файл
    save_to_file(all_links, 'all_links.txt')

    # Сохраняем категоризированные ссылки
    with open('categorized_links.txt', 'w', encoding='utf-8') as f:
        for category, links in categorized.items():
            f.write(f"=== {category.upper()} ({len(links)}) ===\n")
            for link in links:
                f.write(link + '\n')
            f.write('\n')

    print("\nГотово! Все ссылки сохранены в файлы:")
    print("- all_links.txt (все ссылки)")
    print("- categorized_links.txt (категоризированные ссылки)")

if __name__ == "__main__":
    main()
