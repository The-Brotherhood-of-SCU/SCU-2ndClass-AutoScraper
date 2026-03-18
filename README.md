## 支持/Support
如果觉得这个项目有用的话请给一颗⭐️，非常感谢。

If you find this project useful, please leave a ⭐️ for me. Thank you very much.

# 使用方式
有两种方式提供 `Token`：

1. 环境变量（推荐）：在运行前设置 `SCU_TOKEN` 环境变量，脚本会优先使用它。
	```bash
	export SCU_TOKEN="your_token_here"
 	python3 -m venv venv
 	source venv/bin/activate
 	pip3 install requests
	python3 main.py
	```

2. 配置文件（备用）：编辑 `config.ini`，在 `[account]` 下填入 `Token`，并在 `[settings]` 下填入 `days_ahead`：
	```ini
	[account]
	Token = your_token_here

	[settings]
	days_ahead = 3
	```

依赖：

```
pip install requests
```

安全提示：请不要将有效的 Token 提交到公共仓库。优先使用环境变量。若不慎提交，请立即更换 Token。

## 如何获取Token
在浏览器中打开https://zjczs.scu.edu.cn/ccylmp/
完成登陆

在https://zjczs.scu.edu.cn/ccylmp/
任何界面上按下`F12` 或 `右键`-`检查`

打开`应用`-`本地存储空间`-`https://zjczs.scu.edu.cn/`-`userinfo`-`data`-`token`

<img width="1512" height="945" alt="image" src="https://github.com/user-attachments/assets/36e9a066-004b-499a-a106-75f5686ba181" />

复制`token`内所有内容，注意不包括双引号，粘贴到 `SCU_TOKEN` 环境变量或 `config.ini` 中的 `Token` 字段。

