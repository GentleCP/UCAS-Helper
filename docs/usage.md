使用教程
=================

   * [使用前提](#使用前提)
   * [部署项目](#部署项目)
      * [自动部署](#自动部署)
      * [手动部署](#手动部署)
   * [修改配置](#修改配置)
   * [运行项目](#运行项目)
   * [更新项目](#更新项目)


# 使用前提
项目采用python语言编写，需要你本地装有python3环境（建议python3.5+），如果采用`git`方式克隆，需先安装好`git`

# 部署项目
提供两种部署使用方法：`自动化部署`(懒人推荐)和`手动部署`，前者在`windows`环境下要求安装`git`，采用`git`提供的终端（需要用到`shell`命令，`windows`cmd不支持）。
> 注意：推荐采用`git clone`的方式部署项目到本地，这样在后续有更新的时候可以直接通过git命令更新项目

## 自动部署
> 注意：如果选择采用虚拟环境，请确保`mkvirtualenv`命令可用。

- 已安装`git`,在`git bash`终端执行  
    ```text
    git clone --depth 1 https://github.com/GentleCP/UCAS-Helper.git  && cd UCAS-Helper && pip install -r requirements.txt   
    ```
    > 如果使用`pip3`，自行替换`pip`

## 手动部署
1. 下载源代码压缩包或下载`realease`版本代码(推荐) 并解压 
2. 进入项目目录安装依赖包
    ```text
    pip install -r requirements.txt  # 强烈建议使用虚拟环境
    conda env create -f environment.yml  # 如果采用conda环境
    ```

# 修改配置
- 配置方式1：运行`python ucashelper config`(仅支持`linux,mac`平台，不支持`windows`)来启动配置引导程序，这会引导你设置用户信息和资源存储路径
- 配置方式2：当你无法通过上述命令进行配置时，你也可以手动更改`conf/user_config.ini`，补充用户信息和资源存储路径信息

- 登录wifi*（可选）：如果你需要自动校园wifi登录（包括多个账户自动切换），需要配置`accounts.json`
    ```text
      {
          "useful_accounts": [
            {
               "stuid":"xxx",
               "pwd":"xxx"
            },
            {
                "stuid":"xxx",
                "pwd":"xxx"
            }
           
          ],
          "useless_accounts": [],
          "current_month": 12
        }
    ```
    > 每个账号一个，允许存储多个账号，当遇到一个账号流量不够的时候自动切换到下一个账号登录
    

# 运行项目

当确认配置信息修改完毕后，可以在终端或cmd下通过执行`python ucashelper.py ui`来启动小白操作窗口，同时也可以根据需要直接在命令行传入不同参数执行相应的操作，具体如下：

```text
python ucashelper.py --help # 查看命令使用帮助，直接运行python ucashelper.py 效果等同
python ucashelper.py ui # 小白操作窗口
python ucashelper.py config  # 引导配置，不支持windows

python ucashelper.py down # 下载课程资源
python ucashelper.py grade # 查看成绩
python ucashelper.py hack # 破解wifi账号
python ucashelper.py login # 登录校园网，确保在校园网环境下未登录情况执行
python ucashelper.py logout # 登出校园网
python ucashelper.py assess # 自动评教，评教内容在settings.py中设置
```

# 更新项目
在`UCAS-Helper`项目根目录下执行以下命令
```
git stash && git fetch --all && git merge && git stash pop
```

