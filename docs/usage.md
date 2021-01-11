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
    git clone https://github.com/GentleCP/UCAS-Helper.git  && cd UCAS-Helper && pip install -r requirements.txt   
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
> Note: `settings.py`中用户账户、资源存储路径的信息即将迁移到`conf/user_config.ini`中

- 运行`python ucashelper config`来启动配置引导程序，这会引导你设置用户信息和资源存储路径
> 你也可以手动更改`conf/user_config.ini`，但我不建议你将这两个配置内容存储到`settings.py`中，后期会彻底将这部分内容转移

- 根据需求修改配置文件:`settings.py`,`accounts.json`
    - 获取课程资源
        - 进入[settings.py](settings.py)，找到`USER_INFO`修改你自己的用户名和密码
        - 修改`SOURCE_DIR`，这个目录是所有课程资源存放的目录，根据你的个人需求修改  
          
            > 例如`D:/UCAS-sources`
        > 在校园网内无需登录wifi，直接可登录课程网站
    - 登录wifi  
        - wifi登录需修改根目录下的`accounts.json`，添加到useful_accounts中，格式如下：
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
            每个账号一个，允许存储多个账号，当遇到一个账号流量不够的时候自动切换到下一个账号登录
    

# 运行项目

当确认配置信息修改完毕后，可以在终端或cmd下通过执行`python ucashelper.py ui`来启动小白操作窗口，同时也可以根据需要直接在命令行传入不同参数执行相应的操作，具体如下：

```text
python ucashelper.py --help # 查看命令使用帮助，直接运行python ucashelper.py 效果等同
python ucashelper.py ui # 小白操作窗口
python ucashelper.py config  # 引导配置

python ucashelper.py down # 下载课程资源
python ucashelper.py grade # 查看成绩
python ucashelper.py hack # 破解wifi账号
python ucashelper.py login # 登录校园网，确保在校园网环境下未登录情况执行
python ucashelper.py logout # 登出校园网
python ucashelper.py assess # 自动评教，评教内容在settings.py中设置
```

# 更新项目
- 现已支持程序启动时自动进行更新检查，在有更新的时候自动更新，不需要用户手动进行更新操作，如果你不希望每次都进行更新检查，可进入`settings.py`中设置`ALLOW_AUTO_UPDATE=False`  
    > 注意：由于自动更新依赖git，所以如果是通过`release`版本下载的代码无法使用自动更新功能，因此，本次也是最后一次发布`release`版本，后续更新都将采用此更新方式，如果你只想临时使用，不期待后续更新，可选择下载最新代码。


由于课程站点的变更，可能导致部分功能失效无法使用，待作者修复后，需要更新最新的版本代码到本地，现在提供自动化一条命令更新项目的方式。

> 需通过git方式部署，若直接下载源代码或`realease`压缩包，则需上github下载最新版本代码

在`UCAS-Helper`项目根目录下执行以下命令
```
git stash && git fetch --all && git merge && git stash pop
```

