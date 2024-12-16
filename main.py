# main.py
from omegaconf import DictConfig, OmegaConf
import hydra
import os
from hydra.utils import get_original_cwd, to_absolute_path


@hydra.main(config_path="configs", config_name="config")
def main(config:DictConfig) -> None:
    print(OmegaConf.to_yaml(config, resolve=True))
    print("CURRENT WORKING DIRECTORY: ", os.getcwd())
    print("ORIGINAL WORKING DIR: ", get_original_cwd())
    print("TO ABSOLUTE PATH('some_file.txt')", to_absolute_path("some_file.txt"))

if __name__ == "__main__":
    main()
