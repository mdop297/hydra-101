from typing import Any
from omegaconf import DictConfig, OmegaConf, MISSING
import hydra
from hydra.core.config_store import ConfigStore
from pydantic.dataclasses import dataclass
from pydantic import validator


@dataclass
class ExpSchema:
    model: str = MISSING
    nrof_epochs: int = 20
    lr: float = 5e-4
    batch_size: int = 512

    @validator("batch_size")
    def batch_size_multiple_of_32(cls, batch_size: int) -> int:
        if batch_size % 32 != 0:
            raise ValueError("batch_size should be multiple of 32")
        return batch_size


@dataclass
class ResNet18ExpSchema(ExpSchema):
    model: str = "resnet18"


@dataclass
class ResNet50ExpSchema(ExpSchema):
    model: str = "resnet50"


@dataclass
class ConfigSchema:
    experiment: ExpSchema


cs = ConfigStore.instance()
cs.store(name="config_schema", node=ConfigSchema)
cs.store(group="experiment", name="resnet18_schema", node=ResNet18ExpSchema)
cs.store(group="experiment", name="resnet50_schema", node=ResNet50ExpSchema)


@hydra.main(config_path="configs", config_name="config", version_base=None)
def main(config: DictConfig) -> None:
    OmegaConf.to_object(config)
    print(OmegaConf.to_yaml(config))


if __name__ == "__main__":
    main()
