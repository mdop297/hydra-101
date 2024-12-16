import hydra
from omegaconf import DictConfig
from hydra.utils import instantiate
import torch

class MyClass:
    def __init__(self, name: str) -> None:
        self.name = name

    def say_hello(self) -> None:
        print(f"Hello {self.name}")


@hydra.main(config_path="configs", config_name="instantiate-config", version_base=None)
def main(config: DictConfig) -> None:
    my_class = MyClass(name="Minh")
    my_class.say_hello()

    my_class_hydra = instantiate(config.my_class)
    my_class_hydra.say_hello()

    partial_optimizer = instantiate(config.optimizer)
    print(partial_optimizer)
    parameters = torch.nn.Parameter(torch.randn(10, 10))
    optimizer = partial_optimizer([parameters])
    print(optimizer)

if __name__ == "__main__":
    main()


