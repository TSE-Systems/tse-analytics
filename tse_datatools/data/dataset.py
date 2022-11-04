from typing import Optional, Literal

from tse_datatools.data.actimot_data import ActimotData
from tse_datatools.data.animal import Animal
from tse_datatools.data.box import Box
from tse_datatools.data.calorimetry_data import CalorimetryData
from tse_datatools.data.drinkfeed_data import DrinkFeedData
from tse_datatools.data.group import Group


class Dataset:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.loaded: bool = False

        self.meta: Optional[dict] = None

        self.boxes: dict[int, Box] = {}
        self.animals: dict[int, Animal] = {}
        self.groups: dict[str, Group] = {}

        self.calorimetry: Optional[CalorimetryData] = None
        self.actimot: Optional[ActimotData] = None
        self.drinkfeed: Optional[DrinkFeedData] = None

    def extract_groups_from_field(self, field: Literal["text1", "text2", "text3"] = "text1") -> dict[str, Group]:
        """Extract groups assignment from Text1, Text2 or Text3 field"""
        groups_dict = {}
        for animal in self.animals.values():
            group_name = getattr(animal, field)
            if group_name not in groups_dict:
                groups_dict[group_name] = []
            groups_dict[group_name].append(animal.id)

        groups: dict[str, Group] = {}
        for key, value in groups_dict.items():
            group = Group(key, value)
            groups[group.name] = group
        return groups

    def load(self, extract_groups=False):
        """Load raw data."""
        from tse_datatools.loaders.dataset_loader import DatasetLoader
        DatasetLoader.load(self)

        if self.meta is not None:
            items = self.meta.get("Boxes")
            if items is not None:
                self.animals.clear()
                self.boxes.clear()
                for item in items:
                    animal = Animal(
                        item.get("AnimalNo"),
                        item.get("BoxNo"),
                        item.get("Weight"),
                        item.get("Text1"),
                        item.get("Text2"),
                        item.get("Text3")
                    )
                    self.animals[animal.id] = animal

                    box = Box(animal.box_id, animal.id)
                    self.boxes[box.id] = box

        if extract_groups:
            self.groups = self.extract_groups_from_field()

    def unload(self):
        """Dispose raw data in order to free memory."""
        self.meta = None

        self.boxes = []
        self.animals = []
        self.groups = []

        self.calorimetry = None
        self.actimot = None
        self.drinkfeed = None

        self.loaded = False

    def __getstate__(self):
        state = self.__dict__.copy()
        state['loaded'] = False
        state['meta'] = None
        state['calorimetry'] = None
        state['actimot'] = None
        state['drinkfeed'] = None
        return state


if __name__ == "__main__":
    import timeit
    from tse_datatools.analysis.processor import apply_time_binning

    tic = timeit.default_timer()
    # dataset = Dataset("Test Dataset", "C:\\Users\\anton\\Downloads\\20220404.22001.Ferran")
    # dataset = Dataset("Test Dataset", "C:\\Users\\anton\\Downloads\\Diagnostic-run20220519")
    dataset = Dataset("Test Dataset", "C:\\Users\\anton\\Downloads\\Diagnostic-run20220519.Zip")
    dataset.load(extract_groups=True)
    df_by_groups = dataset.drinkfeed.filter_by_groups([dataset.groups["EcN-Con+CD"]])
    df_by_animals = dataset.drinkfeed.filter_by_animals([37, 48])

    result = apply_time_binning(dataset.drinkfeed.df, 1, "hour", "sum")
    print(timeit.default_timer() - tic)
