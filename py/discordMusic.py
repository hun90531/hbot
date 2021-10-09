import bs4
from selenium import webdriver
from youtube_dl import YoutubeDL


YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


# 검색어 msg를 입력받아 노래 제목과 링크를 가져오기
def getMusicInfo(msg):
    # 검색 결과 중 원하는 영상 선택
        if len(msg.split()) >= 2 and msg.split()[-2] == '-s':
            i = int(msg.split()[-1]) - 1
            msg = ' '.join(msg.split()[:-2])
        
        # 검색 결과 중 가장 위에 있는 항목 선택
        else:
            i = 0

        options = webdriver.ChromeOptions()
        options.add_argument('headless')

        # chromedriver와 셀레니움을 통해 유튜브 검색을 실행하는 코드
        driver = webdriver.Chrome(executable_path = 'chromedriver.exe', options=options)
        
        print(f'msg : {msg}')
        driver.get('https://www.youtube.com/results?search_query=' + msg)

        bs = bs4.BeautifulSoup(driver.page_source, 'html.parser')

        # 검색 결과에서 id 값이 'vidio-title'인 태그를 추출후
        titles = bs.find_all('a', {'id' : 'video-title'})

        title = titles[i].text.strip() # 검색 결과 중 i 번째 선택 (-s 없으면 0  )

        # 상대 경로로 되어있는 href 값을 가져와 url 만들기
        url = 'https://www.youtube.com' + titles[i].get('href')

        driver.quit()

        return title, url

# url을 입력받아 음악 재생
def playMusic(url):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
    URL = info['formats'][0]['url']
    
    return URL