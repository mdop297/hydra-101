# Hydra-101

### 1. How to add hydra config from terminal 
```yaml
# config.yaml
# empty file
```
```python
# main.py
from omegaconf import DictConfig, OmegaConf
import hydra

@hydra.main(config_path="configs", config_name="config")
def main(config:DictConfig) -> None:
    print(OmegaConf.to_yaml(config))

if __name__ == "__main__":
    main()
```
```bash 56
python main.py +training.batch_size=32 +training.epochs=20 +training.lr=5e-5
```

### 2. How to specify a config file
Pass parameters into decorator: 
- config_path: path to file yaml contain the configs
- config_name: name of the yaml config file without ".yaml"

### 3. Override the configuration in config.yaml.
- only for config that exists in yaml file
```bash
python main.py training.batch_size=64
```
- both config that exists or not
```bash
python main.py ++training.model=vgg16
```
### 4. OmegaConf
- OmegaConf can create config from dictionary: OmegaConf.create({...})
- load config from yaml file: `OmegaConf.load("./config.yaml")`
- Change config loaded from a .yaml file in python code:
    ```bash
        config = OmegaConf.load("./config.yaml")
        config.training.lr = 5e-10
        # create new value
        config.new_key = "new_value"
        print(OmegaConf.to_yaml(config))
    ```
- Set value to be mandatory by `???`. We must specify the value before accessing it.
    ```yaml
    # in config.yaml 
    training: 
        batch_size: 128
        epochs: 20
        lr: 5e-5
        optim: ???
    ```
- Value interpolation config:
    ```yaml
    # config.yaml
    server: 
        host: localhost
        port: 80
    client: 
        url: http://${server.host}:${server.port}
        # value in current level:
        description: Client of ${.url}
    ```
    ```python
    # main.py
    def main() -> None:
        config=OmegaConf.load("./config.yaml")
        print(OmegaConf.to_yaml(config, resolve=True))
    ```
    - stack variable in config file
    ```yaml
    # yaml file
    selected_plan: A
    plans: 
        A: plan A
        B: plan B
    plan: 
        ${plan[${selected_plan}]}
    ```
- Use environment variable in configuration
    ```python
    # .py
    def main() -> None:
        os.environ["USER"] = "nhatminh"
        config=OmegaConf.load("./env-config.yaml")
        print(OmegaConf.to_yaml(config, resolve=True))
    ```
    ```yaml
    # .yaml
    user: 
        name: ${oc.env:USER}
        home: /home/${oc.env:USER}
    ```
- Merge configuration
    ```python
    # .py
    # merge config files
    OmegaConf.merge(loaded_config_1, loaded_config_2)
    # merge config with cli
    OmegaConf.merge_with_cli()
    ```
### 5. Grouping config files using CLI

```text
configs
├── config.yaml
└── experiments
    ├── resnet18.yaml
    └── resnet50.yaml
```

```bash
# config.yaml
```
```python
# main.py
from omegaconf import DictConfig, OmegaConf
import hydra

@hydra.main(config_path="configs", config_name="config", version_base=None)
def main(config) -> None:
    print(OmegaConf.to_yaml(config, resolve=True))

if __name__ == "__main__":
    main()
```

```bash
python main.py +experiments=resnet18
```
### 6. Select default config (without usin cli)
```yaml
defaults:
  - experiments: resnet18
```
everything else is the same.
#### Override config file
```yaml
# in config.yaml
defaults:
  - experiments: resnet18
  - _self_

experiments:
    optim: SGD
```
#### Merge config file
```text
configs
├── config-to-merge.yaml
├── config.yaml
└── experiments
    ├── resnet18.yaml
    └── resnet50.yaml
```

```yaml
# in config.yaml
defaults:
  - experiments: resnet18
  - config-to-merge
  - _self_

experiments:
    optim: SGD
```
### 7. Multirun
```bash
python main.py -m experiments=resnet18,resnet50
```
- output
```cmd
[2024-12-16 14:07:14,459][HYDRA] Launching 2 jobs locally
[2024-12-16 14:07:14,459][HYDRA]        #0 : experiments=resnet18
experiments:
  model: resnet18
  optim: SGD
  lr: 5.0e-05
  lr_scheduler: MultiStepLR
somekey: some value

[2024-12-16 14:07:14,575][HYDRA]        #1 : experiments=resnet50
experiments:
  model: resnet50
  optim: SGD
  lr: 5.0e-05
  lr_scheduler: MultiStepLR
somekey: some value
```
- multi configs
```text
configs
├── config-to-merge.yaml
├── config.yaml
├── experiments
│   ├── resnet18.yaml
│   └── resnet50.yaml
└── loss_function
    ├── arcface.yaml
    ├── cosface.yaml
    └── softmax.yaml
```

```yaml
#config.yaml
defaults:
  - experiments: resnet18
  - loss_function: softmax
  - config-to-merge
  - _self_

experiments:
    optim: SGD
```

```bash
python main.py -m experiments=resnet18,resnet50 \
                  loss_function=arcface,cosface,softmax
#output: Launching 6 jobs 
```
- short command to specify that you need to run all the configs except for runs with `softmax` loss
```bash
python main.py -m experiments='glob(*)' loss_function='glob(*, exclude=soft*)'
# output: Launching 4 jobs
```

### 8. Outputs and Working directory
```python
# main.py
# main.py
from omegaconf import DictConfig, OmegaConf
import hydra
import os
from hydra.utils import get_original_cwd, to_absolute_path

# don't pass version_base parameter
@hydra.main(config_path="configs", config_name="config")
def main(config:DictConfig) -> None:
    print(OmegaConf.to_yaml(config, resolve=True))
    print("CURRENT WORKING DIRECTORY: ", os.getcwd())
    print("ORIGINAL WORKING DIR: ", get_original_cwd())
    print("TO ABSOLUTE PATH('some_file.txt')", to_absolute_path("some_file.txt"))

if __name__ == "__main__":
    main()
# output: ...
# CURRENT WORKING DIRECTORY:  /home/nhatminh/Workspace/mlops/hands-on-projects/cyberbullying-detection/02-hydra-101/outputs/2024-12-16/14-36-10
```
### 9. Logging
```python
# main.py
from omegaconf import DictConfig, OmegaConf
import hydra, os, logging
from hydra.utils import get_original_cwd, to_absolute_path

logger = logging.getLogger(__name__)

@hydra.main(config_path="configs", config_name="config")
def main(config:DictConfig) -> None:
    print(OmegaConf.to_yaml(config, resolve=True))
    logger.info("info message")
    logger.debug("debug message")

if __name__ == "__main__":
    main()
```
- info level
```bash
python main.py
```
- debug level
```python
python main.py hydra.verbose=true
```
base on the command, we can add the hydra.verbose config in config.yaml file as below:
```yaml
defaults:
  - experiments: resnet18
  - loss_function: softmax
  - config-to-merge
  - _self_

experiments:
    optim: SGD

hydra:
  verbose: true
```
#### Disable the hydra logging
- remove `hydra.verbose: true`
```yaml
#config.yaml
defaults:
  - experiments: resnet18
  - loss_function: softmax
  - config-to-merge
  - _self_
  - override hydra/job_logging: disabled

experiments:
    optim: SGD
```
### 10. Debugging hydra config
- Actually, we don't need to print out our config to check it. We can simply run these commands
#### With `user` config
```bash
python main.py -c job
```
Alternative
```bash
python main.py --cfg job
```
#### With `hydra` config
```bash
python main.py --cfg hydra
```
#### Both of `user` configs and `hydra` configs
```bash
python main.py -c all
```
#### Combine override with debugging configs
```bash
python main.py experiments.optim=some_optimizer -c job
```
#### Debugging configs in packages
- This is useful when we have a large config file
```bash
python main.py -c job --package experiments
```
### 11. Instantiate: Create python objects from configurations
```text
working files:
    - hydra_instantiate.py
    - configs/instantiate-config.yaml
```
To create object from configs using `hydra.utils.instantiate` function, we need to specify `_target_` value, the destination class
```yaml
#configs/instantiate-config.yaml
my_class: 
  _target_: hydra_instantiate.MyClass
  name: Minh from hydra

optimizer:
  _target_: torch.optim.Adam
  _partial_: true #view more in below
  lr: 0.001
  betas: [0.9, 0.999]
  eps: 1e-6
  weight_decay: 0
  amsgrad: false
```
```python
#hydra_instantiate.py
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

```
- output
```bash
# my_class
Hello Minh
# my_class_hydra
Hello Minh from hydra
# partial_optimizer
functools.partial(<class 'torch.optim.adam.Adam'>, lr=0.001, betas=[0.9, 0.999], eps=1e-06, weight_decay=0, amsgrad=False)
# optimizer
Adam (
Parameter Group 0
    amsgrad: False
    betas: [0.9, 0.999]
    capturable: False
    differentiable: False
    eps: 1e-06
    foreach: None
    fused: None
    lr: 0.001
    maximize: False
    weight_decay: 0
)
```
#### Use case of `_partial_`
When we have some parameters of config values that can not pass into config file like: parameter of ML model. Hydra will return a partial function (an object which is passed some parameters into it, and we need to pass some mandatory value to make it a fully instance or function).

### 12. Packages (@)
```text
packages
├── config.yaml
└── task
    ├── mnist_classification.yaml
    └── model
        ├── adapter
        │   └── mnist_classification_resnet18.yaml
        ├── backbone
        │   └── resnet18.yaml
        ├── head
        │   └── identity_head.yaml
        └── simple_model.yaml
```
Working files
```
- packages directory
- packages.py
```
```yaml
#syntax: real_task_name@overriden_name: config_name (name of the .yaml file)
defaults:
  - task: mnist_classification
  - task@other_task: mnist_classification
  # another way
  - /task/model/simple_model@my_model
```
```python
import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(config_path="./packages", config_name='config', version_base=None)
def main(config=DictConfig) -> None:
    print(OmegaConf.to_yaml(config))

if __name__ == "__main__":
    main() 
```

### 13. Small project
