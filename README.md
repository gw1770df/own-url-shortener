## Own-url-shortener

建立属于自己的url缩短服务。

世面url缩短服务数不胜数，但有些不能自定义uri，能定义uri又不一定能用上心仪的，等等原因，不如搭建一个属于自己的url缩短服务。

博客地址地址：[https://word.gw1770df.cc](https://word.gw1770df.cc/2016-10-09/python/%e8%87%aa%e5%b7%b1%e7%9a%84url%e7%bc%a9%e7%9f%ad%e6%9c%8d%e5%8a%a1/)

### DEMO:
![demo](https://word.gw1770df.cc/wp-content/uploads/2016/10/own-url-shortener-demo-1.jpg)

## 动机

有时候想分享自己的文章给别人看，又不能很方便的通过网络发送给他，这时候可能只有两个选择：
1. 在他的设备上为他打开自己的文章。
2. 告诉他一个短地址。

将例如将地址`https://github.com/gw1770df/own-url-shortener`
射影为`http://s.g1770.cc/us`


## 准备工作

你需要：
1. 一个域名，越短越好
2. 一台linux服务器
3. 安装配置好 nginx 和 redis [nginx安装教程](https://word.gw1770df.cc/2016-09-01/linux/web_server/nginx-%e5%ae%89%e8%a3%85%e9%85%8d%e7%bd%ae/)

### 解决python依赖

> sudo pip install flask redis requests

[pip安装教程](https://word.gw1770df.cc/2016-08-03/python/pip-%e5%ae%89%e8%a3%85%e4%b8%8e%e4%bd%bf%e7%94%a8/)

### 获取代码

> git clone https://github.com/gw1770df/own-url-shortener.git

### 修改配置文件

编辑配置文件 _config.py，修改为自己的配置。
```
#!/usr/bin/env python2.7
# coding:utf-8

# 监听端口
server_port = 11081

# debug模式开关
server_debug = False

# 用于url缩短的域名 要以'/'结尾
host = 'http://s.g1770.cc/'

# 当uri没有对应关系时，跳转到的地址A
miss_url = 'https://word.gw1770df.cc'

# redis连接信息
redis_connect_cfg = ('127.0.0.1', 6379, 0)

# redis uri_list 变量名称
uri_list_name = 'uri_list'


# 随机uri包含的字符 可选项：
# 'lower_letters' 小写字母
# 'upper_letters' 大写字母
# 'digits'        数字
short_uri_includ = ['lower_letters', 'digits']

# 随机uri长度
short_uri_length = 4
```

### nginx配置文件


```
upstream url_shortener {
  server 127.0.0.1:11801; # 配置为自己的端口
}

server {
    listen       80;
    server_name  s.g1770.cc; #配置为自己的域名

    access_log  /home/www-data/log/s.g1770.cc combined; # 访问日志

    location /assets {
        root /home/gw1770/home/git/own-url-shortener/templates; # 静态文件路径
                                                                # 设置own-url-shortener/templates文件夹的决定路径
    }

    location / {
        proxy_pass http://url_shortener;
    }

}
```

### 运行

> python url_shortener.py

如果没有问题则以nohup方式启动。推荐使用supervisor管理程序运行。
[supervisor教程](https://word.gw1770df.cc/2016-08-04/linux/supervisor-%e4%bd%bf%e7%94%a8%e6%95%99%e7%a8%8b/)


### 尽情的使用吧

## 一些建议
目前程序中没有添加用户认证模块，服务直接暴露在公网上可能会有一些问题，建议先使用nginx自带用户验证功能配合使用。
[nginx用户验证功能配置教程](https://word.gw1770df.cc/2016-09-25/linux/web_server/nginx%E5%BA%94%E7%94%A8%E5%9C%BA%E6%99%AF/#auth)