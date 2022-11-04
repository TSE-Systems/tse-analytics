import os
import glob
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from tse_datatools.data.actimot_data import ActimotData
from tse_datatools.data.calorimetry_data import CalorimetryData
from tse_datatools.data.dataset import Dataset
from tse_datatools.data.drinkfeed_data import DrinkFeedData
from tse_datatools.data.variable import Variable
from tse_datatools.loaders.actimot_data_loader import ActimotDataLoader
from tse_datatools.loaders.calorimetry_data_loader import CalorimetryDataLoader
from tse_datatools.loaders.drinkfeed_data_loader import DrinkFeedDataLoader


class DatasetLoader:

    @staticmethod
    def load(dataset: Dataset):

        path = Path(dataset.path)
        if path.is_file() and path.suffix.lower() == ".zip":
            with TemporaryDirectory() as tmp_folder:
                with ZipFile(path, "r") as zip:
                    zip.extractall(tmp_folder)
                DatasetLoader.__load_from_folder(tmp_folder, dataset)
        else:
            DatasetLoader.__load_from_folder(dataset.path, dataset)

    @staticmethod
    def __load_from_folder(folder_path: str, dataset: Dataset):
        DatasetLoader.__load_metadata(folder_path, dataset)
        DatasetLoader.__load_calorimetry_data(folder_path, dataset)
        DatasetLoader.__load_actimot_data(folder_path, dataset)
        DatasetLoader.__load_drinkfeed_data(folder_path, dataset)

        dataset.loaded = True

    @staticmethod
    def __load_metadata(folder_path: str, dataset: Dataset):
        files = glob.glob(os.path.join(folder_path, "Content.json"), recursive=False)
        if len(files) > 0:
            with open(files[0], "rt") as f:
                meta = json.load(f)
                dataset.meta = meta

    @staticmethod
    def __load_calorimetry_data(folder_path: str, dataset: Dataset):
        files = glob.glob(os.path.join(folder_path, "Calorimetry.csv"), recursive=False)
        if len(files) > 0:
            path = files[0]
            df = CalorimetryDataLoader.load(path)
            meta = next((table for table in dataset.meta.get("Tables") if table.get("TableName") == "Calorimetry"),
                        None)
            variables = DatasetLoader.__get_variables(meta)
            dataset.calorimetry = CalorimetryData("Calorimetry", path=path, meta=meta, df=df, variables=variables)

    @staticmethod
    def __load_actimot_data(folder_path: str, dataset: Dataset):
        files = glob.glob(os.path.join(folder_path, "ActiMot.csv"), recursive=False)
        if len(files) > 0:
            path = files[0]
            df = ActimotDataLoader.load(path)
            meta = next((table for table in dataset.meta.get("Tables") if table.get("TableName") == "ActiMot"),
                        None)
            variables = DatasetLoader.__get_variables(meta)
            dataset.actimot = ActimotData("ActiMot", path=path, meta=meta, df=df, variables=variables)

    @staticmethod
    def __load_drinkfeed_data(folder_path: str, dataset: Dataset):
        files = glob.glob(os.path.join(folder_path, "DrinkFeed.csv"), recursive=False)
        if len(files) > 0:
            path = files[0]
            df = DrinkFeedDataLoader.load(path)
            meta = next((table for table in dataset.meta.get("Tables") if table.get("TableName") == "DrinkFeed"),
                        None)
            variables = DatasetLoader.__get_variables(meta)
            dataset.drinkfeed = DrinkFeedData("DrinkFeed", path=path, meta=meta, df=df, variables=variables)

    @staticmethod
    def __get_variables(meta: dict) -> dict[str, Variable]:
        variables: dict[str, Variable] = {}
        parameters = meta.get("Parameters")
        if parameters is not None:
            for parameter in parameters:
                variable = Variable(parameter.get("Name"), parameter.get("OriginalName"), parameter.get("Unit"), parameter.get("OriginalUnit"))
                variables[variable.name] = variable
        return variables
