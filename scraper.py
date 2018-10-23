import requests
from bs4 import BeautifulSoup
import token_reader as token
import urllib.request
import json

yt_url = "https://www.youtube.com"
yt_search = "/results?search_query="
mozhdr = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}
yt_api_key = token.get_yt_api_key()

def scrape_yt(search_term):
    search = search_term.replace(" ", "+")
    full_url = yt_url + yt_search + search
    print(full_url)
    sb_get = requests.get(full_url, headers = mozhdr)

    souped_data = BeautifulSoup(sb_get.content, "html.parser")
    yt_links = souped_data.find_all("a", class_ = "yt-uix-tile-link")

    top_5_links = []
    top_5_titles = []
    top_5_durations = []
    added_links = 0

    for link in yt_links:
        link_href = link.get("href")
        if '/watch?' in link_href: 
            video_id=link_href.split("=")[1]

            duration_string = ""
            searchUrl="https://www.googleapis.com/youtube/v3/videos?id="+video_id+"&key="+yt_api_key+"&part=contentDetails"
            response = urllib.request.urlopen(searchUrl).read()
            data = json.loads(response)
            all_data=data['items']
            contentDetails=all_data[0]['contentDetails']
            duration=contentDetails['duration'][2:]
            
            h = 0
            m = 0
            s = 0

            h_pos = duration.find("H")
            m_pos = duration.find("M")
            s_pos = duration.find("S")

            if h_pos != -1:
                h = int(duration[:h_pos])
                m = int(duration[h_pos+1:m_pos])
                s = int(duration[m_pos+1:s_pos])
            elif m_pos != -1:
                m = int(duration[:m_pos])
                s = int(duration[m_pos+1:s_pos])
            elif s_pos != -1:
                s = int(duration[:s_pos])

            if h > 0:
                if h < 10:
                    duration_string += "0"
                duration_string += str(h) + ":"
            if m > 0:
                if m < 10:
                    duration_string += "0"
                duration_string += str(m) + ":"
            else:
                duration_string += "00:"
            if s > 0:
                if s < 10:
                    duration_string += "0"
                duration_string += str(s)

            link_url = yt_url + link.get("href")
            link_title = link.get("title")

            top_5_links.append(link_url)
            top_5_titles.append(link_title)
            top_5_durations.append(duration_string)
            added_links += 1
        
        if added_links > 4:
            break

    return (top_5_links, top_5_titles, top_5_durations)

