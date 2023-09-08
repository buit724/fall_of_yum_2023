import datetime
from typing import List, Tuple

from titleinfo import TitleInfo
from trophyinfo import TrophyInfo


class ProfileInfo:
    def __init__(self, complete_titles: List[TitleInfo], incomplete_titles: List[TitleInfo], 
                 trophies: List[Tuple[datetime.date, List[TrophyInfo], str]], trophy_count: int):
        self.trophy_count = trophy_count
        self.trophies = trophies
        self.incomplete_titles = incomplete_titles
        self.complete_titles = complete_titles
        