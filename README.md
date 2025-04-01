

https://github.com/user-attachments/assets/339275e2-d784-4bdd-9c73-9b4a3d55fb7a


# **ПАСЬЯНС（Solitaire in EXAPUNKS）的机器人**

## **使用方法**
- 适用于 **2560x1600 分辨率**
- **150% 缩放**
- **全屏模式**
- 需要**手动打开纸牌游戏界面**

## **图像识别**
- 通过 **直方图比较**，每个识别符号提供多个模板匹配，**取最高得分**
- **花色**图标*基本能正确识别
- **数字识别容易出错，因此使用 OCR**

## **求解方法**
- **暴力 DFS**
- 如果搜索深度超过 **1000** 或计算时间超过 **3 分钟**，则**直接重开**

## **其他说明**
- **模型搭建得不太好**，但能用，所以**懒得改了** 😆


# ПАСЬЯНС（Solitaire in EXAPUNKS）bot

## Usage
- Works at **2560x1600 resolution**
- **150% scaling**
- **Fullscreen mode**
- The Solitaire game interface must be opened manually

## Image Recognition
- Uses **histogram comparison**, every sign has multi-template to match and **use the highest score**
- Suit icons are generally easy to distinguish
- **Numbers are prone to recognition errors, so OCR is used**

## Solving Method
- **Brute-force DFS**
- If the depth exceeds **1000** or the solving time exceeds **3 minutes**, the bot **restarts**

## Other Notes
- **The model isn’t well-optimized**, but it works, so I’m **too lazy to fix it** 😆
