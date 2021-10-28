import re
import requests
import threading
from bs4 import BeautifulSoup

# lock for writing into files
lock = threading.Lock()

# regex to clear html tags from text
html_tag_re = re.compile(r"<[^>]+>")

# base url
pag = "1"
base_url = (
    "https://www.kijiji.it/offerte-di-lavoro/offerta/informatica-e-web/?p="
    + pag
    + "?entryPoint=sb"
)

# clear the contentent of the file
open("jobs.txt", "w").close()

# function to remove html tags from text


def remove_html_tags(text):
    return html_tag_re.sub("", text)


def scan_page(page):
    for job in page:
        title = ""
        short_description = ""
        location = ""
        date = ""
        link = ""
        # get title
        if job.find("a", class_="cta"):
            title = remove_html_tags(job.find("a", class_="cta").string.strip())
        # get link
        if job.find("a", class_="cta"):
            link = job.find("a", class_="cta").get("href")
        # get description
        if job.find("p", class_="description"):
            short_description = remove_html_tags(
                job.find("p", class_="description").string.strip().replace("\n", " ")
            )
        # get location
        if job.find("p", class_="locale"):
            location = remove_html_tags(job.find("p", class_="locale").string.strip())
        # get date
        if job.find("p", class_="timestamp"):
            date = remove_html_tags(job.find("p", class_="timestamp").string.strip())

        s = (
            title
            + "\t"
            + short_description
            + "\t"
            + location
            + "\t"
            + date
            + "\t"
            + link
            + "\n"
        )

        s = re.sub("\t\s+", " ", s).lstrip()

        if s != "":
            # Critical section
            lock.acquire()

            f_jobs = open("jobs.txt", "a")
            f_jobs.write(s)
            f_jobs.close()

            lock.release()


def thread_fun(i):
    print("[# " + i + "] Started!")
    base_url = (
        "https://www.kijiji.it/offerte-di-lavoro/offerta/informatica-e-web/?p="
        + i
        + "?entryPoint=sb"
    )
    html_page = requests.get(url=base_url).content
    soup = BeautifulSoup(html_page, "html.parser")
    search_result = soup.find(id="search-result").find_all("li")
    scan_page(search_result)
    print("[# " + i + "] Finished!")


html_page = requests.get(url=base_url).content
soup = BeautifulSoup(html_page, "html.parser")

# search for total pages number
total_pages = int(
    (remove_html_tags(str(soup.find_all("h4", class_="pagination-hed")[0])).split())[3]
)
print("[+] Total pages: ", total_pages)

search_result = soup.find(id="search-result").find_all("div", class_="item-content")
scan_page(search_result)

threads = []

for i in range(2, total_pages + 1):
    t = threading.Thread(target=thread_fun, args=[str(i)])
    threads.append(t)
    t.start()

[thread.join() for thread in threads]
