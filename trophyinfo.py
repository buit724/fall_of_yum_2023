import datetime

from psnawp_api.models.trophies.trophy import Trophy
from psnawp_api.models.trophies.trophy_constants import TrophyType

from titleinfo import TitleInfo


class TrophyInfo:
    def __init__(self, trophy: Trophy, title_info: TitleInfo):
        self.trophy_icon_url: str = trophy.trophy_icon_url
        self.trophy_name: str = trophy.trophy_name
        self.earned_date_time: datetime.datetime = trophy.earned_date_time
        self.trophy_type = trophy.trophy_type
        self.title_info: TitleInfo = title_info

    def is_plat(self) -> bool:
        """
        Whether this trophy is a plat trophy
        :return: Whether this trophy is a plat trophy
        """

        return self.trophy_type == TrophyType.PLATINUM
