## 1.配置虚拟环境

### 1.1 该项目相关包列表

    Twisted(手动安装)
    scrapy
    pywin32

### 1.2 安装相关包需要注意的项

    1. 在安装scrapy框架前我们需要先安装Twisted,直接pip安装时会报错,我们先去https://www.lfd.uci.edu/~gohlke/pythonlibs/该地址下载
    与你所使用的环境相匹配的.whl文件然后使用pip install安装该文件
    2. 此时我们再pip install scrapy就可以成功安装了
