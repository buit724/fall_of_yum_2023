from typing import List, Dict, Tuple

from psnawp_api.models.trophies.trophy import Trophy
from psnawp_api.models.trophies.trophy_titles import TrophyTitle

import app
import datetime


class TitleInfo:
    def __init__(self, title: TrophyTitle, title_psn_link: str, trophies_left: int, fall_trophies: List[Trophy]):
        self.title_icon_url: str = title.title_icon_url
        self.title_name: str = title.title_name
        self.title_psn_link: str = title_psn_link
        self.trophies_left: int = trophies_left
        self.fall_trophies = fall_trophies

    def is_complete(self) -> bool:
        """
        Check if this has been plat already
        :return:
        """
        return self.trophies_left == 0

    def status(self) -> str:
        """
        Get the current status
        :return: The current status
        """
        return f"Complete Date: {app.format_time(self.fall_trophies[0].earned_date_time)}" if self.is_complete() \
            else f"{self.trophies_left} Trophies Left"

    def status_css(self) -> str:
        return "text-success" if self.is_complete() else "text-orange"

    def card_css(self) -> str:
        return "complete-card" if self.is_complete() else "incomplete-card"

    def grouped_trophies(self) -> List[Tuple[datetime.date, List[Trophy]]]:
        groups: Dict[datetime.date, List[Trophy]] = {}
        for trophy in self.fall_trophies:
            groups.setdefault(trophy.earned_date_time.astimezone(app.yum_tz).date(), []).append(trophy)

        result: List[Tuple[datetime.date, List[Trophy]]] = []
        for date in sorted(groups.keys(), reverse=True):
            result.append((date, groups.get(date)))

        return result

