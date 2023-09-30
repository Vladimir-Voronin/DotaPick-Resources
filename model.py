class Hero:
    """ Contains all info about specific hero. """

    def __init__(self, *, id_=None, dotabuff_name=None, name=None, general_winrate=None,
                 update_date=None, winrate_dict=None, image_path=None, roles_set=None, allies_set=None):
        self.id = id_
        self.dotabuff_name = dotabuff_name
        self.name = name
        self.general_winrate = general_winrate
        self.update_date = update_date
        self.winrate_dict = winrate_dict
        self.image_path = image_path
        self.roles_set = roles_set
        self.allies_set = allies_set

    def __repr__(self):
        return f"""Hero: {self.name}, dotabuff_name: {self.dotabuff_name}, general_winrate: {self.general_winrate}"""

    def copy(self):
        new_winrate_dict = None if self.winrate_dict is None else self.winrate_dict.copy()
        new_roles_set = None if self.roles_set is None else self.roles_set.copy()
        new_allies_set = None if self.allies_set is None else self.allies_set.copy()
        return Hero(id_=self.id, dotabuff_name=self.dotabuff_name, name=self.name, general_winrate=self.general_winrate,
                    update_date=self.update_date,
                    winrate_dict=new_winrate_dict,
                    image_path=self.image_path,
                    roles_set=new_roles_set,
                    allies_set=new_allies_set)


class Role:
    def __init__(self, *, id_=None, name=None):
        self.id = id_
        self.name = name

    def __repr(self):
        return f'Role: id == {self.id}, name == {self.name}'


class Filter:
    def __init__(self, *, id_=None, name=None):
        self.id = id_
        self.name = name

    def __repr(self):
        return f'Filter: id == {self.id}, name == {self.name}'


class SkillLevel:
    def __init__(self, *, id_=None, name=None):
        self.id = id_
        self.name = name

    def __repr(self):
        return f'SkillLevel: id == {self.id}, name == {self.name}'
