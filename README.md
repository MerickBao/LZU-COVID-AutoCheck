### 兰州大学定时自动健康打卡

每天定时自动打卡（3，6，8，10点，可以自己修改），并将打卡结果推送到微信。

### 使用步骤

#### 1.fork本仓库

#### 2.然后在仓库`Settings --> secrets`中添加三个`secrets`

`CARDID`：学生卡号

`PASSWORD`：兰州大学个人工作平台密码

`SENDKEY`：server酱SendKey，可以点击进入[server酱官网](https://sct.ftqq.com/)，进行登录绑定微信，然后获取SendKey

![获取SendKey](https://gitee.com/MerickBao/pic-embedding/raw/master/img/20211110113318.png)

填写完成后可以看到有三个绿色的仓库`secrets`

![完成结果](https://gitee.com/MerickBao/pic-embedding/raw/master/img/20211110112751.png)

#### 3.进行测试

点击进入仓库`Actions`，然后按下图顺序点击进行测试：

![测试](https://gitee.com/MerickBao/pic-embedding/raw/master/img/20211110113922.png)

如果一切顺利，在微信中就可以看到打卡结果的推送了，如果失败，请优先检查步骤2中`secres`设置是否正确，学号密码是否填写正确。

![打卡结果推送](https://gitee.com/MerickBao/pic-embedding/raw/master/img/20211110114312.png)

#### 4.后续

如果上面一切正常，那么就OK了，然后每天会定时打卡，并将打卡结果推送到微信。默认打卡时间是每天3，6，8，10点，也可自行修改（修改`.github/workflows/lzu-covid-auto-check.yml`），但要注意时间点不要超过五个，因为Server酱免费用户每日API调用限制为5次。

### 引用

本项目使用了`Hollow Man`大佬的[健康打卡](https://gitee.com/hollowman6/LZU-Auto-COVID-Health-Report)进行修改，添加了server酱推送。

