from flask import Flask, render_template
from typing import Dict, List, Tuple, Literal

from psnawp_api import PSNAWP
from psnawp_api.models.trophies.trophy import Trophy
from psnawp_api.models.trophies.trophy_constants import TrophyType
from psnawp_api.models.trophies.trophy_titles import TrophyTitle
from psnawp_api.models.user import User

from datetime import datetime
from zoneinfo import ZoneInfo

yum_tz = ZoneInfo("America/New_York")
fall_of_yum_start = datetime(2023, 9, 1, 19, 0, 0, 0, yum_tz)

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


@app.context_processor
def utility_processor():
    def format_time(time: datetime) -> str:
        return time.astimezone(yum_tz).strftime("%m/%d/%Y, %I:%M:%S%p %Z")

    return dict(format_time=format_time)


@app.route("/")
def home():
    res: Tuple[List[Tuple[TrophyTitle, str, int, List[Trophy]]], List[Tuple[Trophy, str, str]]] = get_titles()
    return render_template("status.html", titles=res[0], trophies=res[1])


def get_titles() -> Tuple[List[Tuple[TrophyTitle, str, int, List[Trophy]]], List[Tuple[Trophy, str, str]]]:
    # Get yummus profile
    psnawp: PSNAWP = PSNAWP('KR640OE86Um82g3GzyGPGjZJbYmpXmD8jSDaddUKY0WukyI3WdMZoAlWxZSWTy06')
    yummus: User = psnawp.user(online_id='yummus_')

    # for trophy in yummus.trophies(np_communication_id='NPWR17582_00', platform='PS4'):
    #    print(trophy)

    # Go over all the desired games
    titles: List[Tuple[TrophyTitle, str, int, List[Trophy]]] = []
    fall_trophies: List[Tuple[Trophy, str, str]] = []
    for title in [x for x in yummus.trophy_titles() if x.np_communication_id in titles_to_look_for.keys()]:
        complete_title = get_complete_title(yummus, title)
        titles.append(complete_title)
        fall_trophies.extend([(t, title.title_name, complete_title[1]) for t in complete_title[3]])
        #print(title.title_name)
        #print(f"Trophies left to do: {title_complete[2]}")
        #print(f"Trophies earned recently: {len(title_complete[3])}")
        #for trophy in title_complete[3]:
        #    print(f"{trophy.trophy_name} - {trophy.trophy_detail} ({trophy.earned_date_time})")
        #print(f"https://psnprofiles.com/trophies/{title_complete[1]}/yummus_?order=psn-rarity&trophies=unearned")

    titles.sort(key=lambda x: x[2])  # sort by trophies left
    fall_trophies.sort(key=lambda x: x[0].earned_date_time, reverse=True)  # sort by complete time

    return titles, fall_trophies


def get_complete_title(yummus: User, title: TrophyTitle) -> Tuple[TrophyTitle, str, int, List[Trophy]]:
    # Get all the trophies for this game
    trophies = yummus.trophies(np_communication_id=title.np_communication_id,
                               platform=titles_to_look_for[title.np_communication_id][1],
                               include_metadata=True)

    trophies_left = []  # trophies not earned
    fall_trophies = []  # earned during fall of yum
    for trophy in trophies:
        if trophy.trophy_type is not TrophyType.PLATINUM:
            if trophy.earned is False:
                trophies_left.append(trophy)
            elif trophy.earned_date_time > fall_of_yum_start:
                fall_trophies.append(trophy)

    fall_trophies.sort(key=lambda x: x.earned_date_time, reverse=True)
    title_psn_link = f"https://psnprofiles.com/trophies/{titles_to_look_for[title.np_communication_id][0]}/yummus_?order=psn-rarity&trophies=unearned"
    return title, title_psn_link, len(trophies_left), fall_trophies
