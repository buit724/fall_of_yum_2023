import time

from flask import Flask, render_template
from typing import Dict, List, Tuple, Literal

from psnawp_api import PSNAWP
from psnawp_api.models.trophies.trophy import Trophy
from psnawp_api.models.trophies.trophy_constants import TrophyType
from psnawp_api.models.trophies.trophy_titles import TrophyTitle
from psnawp_api.models.user import User

import datetime
from zoneinfo import ZoneInfo

from titleinfo import TitleInfo
from trophyinfo import TrophyInfo

yum_tz = ZoneInfo("America/New_York")
fall_of_yum_start = datetime.datetime(2023, 9, 1, 19, 0, 0, 0, yum_tz)

titles_to_look_for: Dict[str, Tuple[str, Literal["PS Vita", "PS3", "PS4", "PS5"]]] = {
    'NPWR21279_00': ("11772-bugsnax", "PS5"),
    'NPWR21945_00': ("11765-dead-by-daylight", "PS5"),
    'NPWR08199_00': ("3483-dark-souls-ii-scholar-of-the-first-sin", "PS4"),
    'NPWR20842_00': ("12996-ratchet-clank-rift-apart", "PS5"),
    'NPWR21757_00': ("15880-lego-star-wars-the-skywalker-saga", "PS5"),
    'NPWR23774_00': ("13635-hades", "PS5"),
    'NPWR20006_00': ("13954-deathloop", "PS5"),
    'NPWR21115_00': ("12873-resident-evil-village", "PS5"),
    'NPWR17582_00': ("9594-catherine-full-body", "PS4"),
    'NPWR25297_00': ("16773-fall-guys-ultimate-knockout", "PS5")
}

app = Flask(__name__)


def format_time(time: datetime.datetime) -> str:
    return time.astimezone(yum_tz).strftime("%m/%d/%Y, %I:%M:%S%p %Z")


def format_date(date: datetime.date) -> str:
    return date.strftime("%m/%d/%Y")


def is_plat(trophy: Trophy) -> bool:
    return trophy.trophy_type == TrophyType.PLATINUM


@app.context_processor
def utility_processor():
    return dict(format_time=format_time, is_plat=is_plat, format_date=format_date)


@app.route("/")
def home():
    res: Tuple[List[TitleInfo], List[TrophyInfo]] = get_titles()
    titles: List[TitleInfo] = res[0]

    # Sort complete by completion date
    complete_titles: List[TitleInfo] = [t for t in titles if t.trophies_left == 0]
    complete_titles.sort(key=lambda x: x.fall_trophies[0].earned_date_time)

    # Sort incomplete by number of trophies left
    incomplete_titles: List[TitleInfo] = [t for t in titles if t.trophies_left > 0]
    incomplete_titles.sort(key=lambda x: x.trophies_left)  # sort by trophies left

    grouped_trophies = grouped_fall_trophies(res[1])

    return render_template("status.html",
                           complete_titles=complete_titles,
                           incomplete_titles=incomplete_titles,
                           trophies=grouped_trophies[0],
                           trophy_count=grouped_trophies[1])


def grouped_fall_trophies(trophies: List[TrophyInfo]) -> List[Tuple[datetime.date, List[TrophyInfo], str]]:
    table_colors: List[str] = ['table-primary', "table-info", 'table-success',
                               "table-warning", "table-secondary", "table-light"]

    trophies.sort(key=lambda x: x.earned_date_time, reverse=True)
    groups: Dict[datetime.date, List[TrophyInfo]] = {}
    for trophy in trophies:
        groups.setdefault(trophy.earned_date_time.astimezone(yum_tz).date(), []).append(trophy)

    result: List[Tuple[datetime.date, List[TrophyInfo], str]] = []
    ind = 0
    trophy_count = 0
    for date in sorted(groups.keys(), reverse=True):
        result.append((date, groups.get(date), table_colors[ind % len(table_colors)]))
        ind += 1
        trophy_count += len(groups.get(date))

    return result, trophy_count


def get_titles() -> Tuple[List[TitleInfo], List[TrophyInfo]]:
    # Get yummus profile
    psnawp: PSNAWP = PSNAWP('KR640OE86Um82g3GzyGPGjZJbYmpXmD8jSDaddUKY0WukyI3WdMZoAlWxZSWTy06')
    yummus: User = psnawp.user(online_id='yummus_')

    # Go over all the desired games
    titles: List[TitleInfo] = []
    fall_trophies: List[TrophyInfo] = []
    for title in [x for x in yummus.trophy_titles() if x.np_communication_id in titles_to_look_for.keys()]:
        title_info: TitleInfo = get_complete_title(yummus, title)
        titles.append(title_info)
        fall_trophies.extend([TrophyInfo(t, title_info) for t in title_info.fall_trophies])

    # titles.sort(key=lambda x: x.trophies_left)  # sort by trophies left
    # fall_trophies.sort(key=lambda x: x.trophy.earned_date_time, reverse=True)  # sort by complete time

    return titles, fall_trophies


def get_complete_title(yummus: User, title: TrophyTitle) -> TitleInfo:
    # Get all the trophies for this game
    trophies = yummus.trophies(np_communication_id=title.np_communication_id,
                               platform=titles_to_look_for[title.np_communication_id][1],
                               include_metadata=True)

    trophies_left: List[Trophy] = []  # trophies not earned
    fall_trophies: List[Trophy] = []  # earned during fall of yum
    for trophy in trophies:
        if trophy.earned is False:
            if trophy.trophy_type is not TrophyType.PLATINUM:
                trophies_left.append(trophy)
        elif trophy.earned_date_time > fall_of_yum_start:
            fall_trophies.append(trophy)

    title_psn_link: str = f"https://psnprofiles.com/trophies/{titles_to_look_for[title.np_communication_id][0]}/yummus_?order=psn-rarity&trophies=unearned"
    return TitleInfo(title, title_psn_link, len(trophies_left), fall_trophies)
