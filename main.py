# main.py
from omegaconf import DictConfig, OmegaConf
import hydra, os, logging
from hydra.utils import get_original_cwd, to_absolute_path

logger = logging.getLogger(__name__)

@hydra.main(config_path="configs", config_name="config", version_base=None)
def main(config:DictConfig) -> None:
    # print(OmegaConf.to_yaml(config, resolve=True))
    logger.info("info message")
    # logger.debug("debug message")

if __name__ == "__main__":
    main()
