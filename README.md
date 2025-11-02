## 支持/Support
如果觉得这个项目有用的话请给一颗⭐️，非常感谢。

## 说明
本项目仅为爬虫软件，用于应对过于难用的搜索界面。该项目请求获取所有目录，寻找符合时间条件的课程id和名称并输出，以便同学们根据自己的时间选择合适的课程项目提升能力。

If you find this project useful, please leave a ⭐️ for me. Thank you very much.

# 使用方式
在`config.ini`中配置Token和天数,运行`main.py`即可

需安装`requests`

## 如何获取Token
在浏览器中打开https://zjczs.scu.edu.cn/ccylmp/
完成登陆

在https://zjczs.scu.edu.cn/ccylmp/
任何界面上按下`F12` 或 `右键`-`检查`

打开`应用`-`本地存储空间`-`https://zjczs.scu.edu.cn/`-`userinfo`-`data`-`token`

<img width="1512" height="945" alt="image" src="https://github.com/user-attachments/assets/36e9a066-004b-499a-a106-75f5686ba181" />

复制`token`内所有内容，注意不包括双引号，粘贴到`config.ini`中`your_token_here`处

