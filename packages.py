import hydra
from omegaconf import DictConfig, OmegaConf


@hydra.main(config_path="./packages", config_name='config', version_base=None)
def main(config=DictConfig) -> None:
    print(OmegaConf.to_yaml(config))

if __name__ == "__main__":
    main() 