import requests
from bs4 import BeautifulSoup
import smtplib
import json
import os
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

URL = "https://cse.pusan.ac.kr/cse/14221/subview.do"
BASE_URL = "https://cse.pusan.ac.kr"
SENDER = os.environ["EMAIL_SENDER"]
PASSWORD = os.environ["EMAIL_PASSWORD"]
RECEIVER = os.environ["EMAIL_RECEIVER"]
LAST_SEEN_FILE = "last_seen.json"

def get_notices():
    import urllib.request
    req = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        html = response.read().decode("utf-8")

    soup = BeautifulSoup(html, "html.parser")
    print("HTML 길이:", len(html))
    print("td.td-subject 개수:", len(soup.select("td.td-subject")))

    notices = []
    rows = soup.select("td.td-subject")
    for row in rows:
        a_tag = row.select_one("a")
        if not a_tag:
            continue
        title = a_tag.get_text(strip=True)
        href = a_tag.get("href", "")
        link = BASE_URL + href if href.startswith("/") else href

        tr = row.find_parent("tr")
        date_td = tr.select_one("td.td-date") if tr else None
        date = date_td.get_text(strip=True) if date_td else ""

        num_td = tr.select_one("td.td-num") if tr else None
        num = num_td.get_text(strip=True) if num_td else ""

        notices.append({"num": num, "title": title, "link": link, "date": date})

    return notices

def load_last_seen():
    try:
        with open(LAST_SEEN_FILE, "r") as f:
            data = json.load(f)
            return data if data else {"last_num": None}
    except:
        return {"last_num": None}

def save_last_seen(num):
    with open(LAST_SEEN_FILE, "w") as f:
        json.dump({"last_num": num}, f)
    subprocess.run(["git", "config", "user.email", "actions@github.com"])
    subprocess.run(["git", "config", "user.name", "GitHub Actions"])
    subprocess.run(["git", "add", LAST_SEEN_FILE])
    subprocess.run(["git", "commit", "-m", "chore: update last_seen"])
    subprocess.run(["git", "push"])

def send_email(new_notices, date_range):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[PNU CSE] [{date_range}] 정보컴퓨터공학부에서 {len(new_notices)}개의 새 소식이 왔습니다!"
    msg["From"] = SENDER
    msg["To"] = RECEIVER

    rows_html = ""
    for n in new_notices:
        rows_html += f"""
        <tr>
            <td style="padding:10px; border-bottom:1px solid #eee;">
                <a href="{n['link']}" style="color:#0057a8; text-decoration:none; font-weight:bold;">{n['title']}</a>
                <br><span style="color:#999; font-size:12px;">게시일: {n['date']}</span>
            </td>
        </tr>"""

    html = f"""
    <html><body style="font-family:sans-serif; color:#333;">
      <div style="max-width:600px; margin:auto; border:1px solid #ddd; border-radius:8px; overflow:hidden;">
        <div style="background:#0057a8; padding:20px;">
          <h2 style="color:white; margin:0;">🔔 [정보컴퓨터공학부] 공지사항</h2>
        </div>
        <table style="width:100%; border-collapse:collapse;">
          {rows_html}
        </table>
        <div style="padding:12px; background:#f9f9f9; text-align:center; font-size:12px; color:#aaa;">
          부산대학교 정보컴퓨터공학부 공지 자동알림
        </div>
      </div>
    </body></html>"""

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(SENDER, PASSWORD)
        s.send_message(msg)
    print(f"✅ 이메일 발송 완료: {len(new_notices)}개 공지")

def main():
    notices = get_notices()
    if not notices:
        print("공지를 가져오지 못했습니다.")
        return

    numbered = [n for n in notices if n["num"].isdigit()]
    if not numbered:
        print("새 공지 없음")
        return

    last = load_last_seen()
    last_num = last.get("last_num")

    if last_num is None:
        save_last_seen(numbered[0]["num"])
        print(f"최초 실행: {numbered[0]['num']} 저장 완료")
        return

    new_notices = [n for n in numbered if int(n["num"]) > int(last_num)]

    if not new_notices:
        print("새 공지 없음")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    send_email(new_notices, today)
    save_last_seen(numbered[0]["num"])

if __name__ == "__main__":
    main()
