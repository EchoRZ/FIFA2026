import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import time

# 2026世界杯官方日期范围 (6月11日 - 7月19日)
start_date = datetime(2026, 6, 11)
end_date = datetime(2026, 7, 19)

cal = Calendar()
cal.add('prodid', '-//2026 FIFA World Cup Calendar//')
cal.add('version', '2.0')
cal.add('calscale', 'GREGORIAN')
cal.add('x-wr-calname', '🏆 2026 FIFA World Cup')
cal.add('x-wr-timezone', 'UTC')

current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime('%Y%m%d')
    # ESPN 世界杯 API 路径
    url = f"http://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates={date_str}"
    
    try:
        response = requests.get(url, timeout=10).json()
        for event in response.get('events', []):
            comp = event['competitions'][0]
            
            # 1. 解析时间 (ESPN返回UTC)
            date_utc = comp['date'].replace('Z', '+00:00')
            start_time = datetime.fromisoformat(date_utc)
            
            # 2. 提取主客队
            teams = {c['homeAway']: c['team'] for c in comp['competitors']}
            away_team = teams.get('away', {}).get('displayName', 'TBD')
            home_team = teams.get('home', {}).get('displayName', 'TBD')
            
            # 3. 提取赛事阶段 (如 Group A) 与 场馆
            group_name = comp.get('group', {}).get('name', '')
            venue = comp.get('venue', {}).get('fullName', 'TBD')
            match_title = event.get('name', f"{away_team} at {home_team}")
            
            # 生成日历标题 (带阶段和Emoji)
            summary = f"🏆 {group_name + ': ' if group_name else ''}{match_title}"
            
            # 4. 创建日历事件
            e = Event()
            e.add('summary', summary)
            e.add('dtstart', start_time)
            # 足球比赛预留 2小时15分钟 (90分钟+15分钟中场+补时缓冲)
            e.add('dtend', start_time + timedelta(hours=2, minutes=15)) 
            e.add('dtstamp', datetime.now(pytz.utc))
            e.add('uid', f"fifa2026-{event['id']}@example.com")
            e.add('location', venue) # 添加场馆，日历中可直接看地图
            
            # 5. 描述信息
            status_detail = comp.get('status', {}).get('type', {}).get('detail', 'Scheduled')
            desc = f"Status: {status_detail}\nVenue: {venue}"
            e.add('description', desc)
            
            if event.get('links'):
                e.add('url', event['links'][0].get('href', ''))
                
            cal.add_component(e)
    except Exception as e:
        print(f"⚠️ 获取 {date_str} 数据失败: {e}")
        
    current_date += timedelta(days=1)
    time.sleep(1) # 礼貌请求，防止遍历40天时被ESPN限流

with open('worldcup2026.ics', 'wb') as f:
    f.write(cal.to_ical())
print("✅ worldcup2026.ics 生成成功！")
