# Hydra-101

### 1. How to add hydra config from terminal 

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