# tradingbot
Trading bot on Alpaca

## Deploy to AWS EC2

1. Log in to AWS Console → AWS EC2 Console
2. Launch a New Instance:
 * Choose Ubuntu 22.04 LTS (free-tier eligible).
 * Instance Type: Select t2.micro (1 vCPU, 1 GB RAM, free tier).
 * Configure Storage: 10GB default is enough.
 * Security Group: Open SSH (port 22) for your IP.
 * Download the Key Pair (.pem file) and save it securely.

3. Connect to EC2:
```
ssh -i your-key.pem ubuntu@your-ec2-ip
```

4. Install Python & Dependencies
Update and install the necessary packages:

```
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip git -y
```

Install the Alpaca API and pandas:
```
pip3 install alpaca-trade-api pandas requests
```

5. Clone Your Trading Bot
```
git clone https://github.com/your-username/your-trading-bot.git
cd your-trading-bot
```

6. Secure API Keys Using Environment Variables
```
echo 'export ALPACA_API_KEY="your_api_key"' >> ~/.bashrc
echo 'export ALPACA_SECRET_KEY="your_secret_key"' >> ~/.bashrc
echo 'export EMAIL_SENDER="your_sender_email"' >> ~/.bashrc
echo 'export EMAIL_RECEIVER="your_receiver_email"' >> ~/.bashrc
source ~/.bashrc
```

7. Set up email
* **Note**: you'll need to set up an app password if you're using Gmail, your regular password won't work.
* Install mailutils on Your EC2 Instance
```
sudo apt install ssmtp -y
```
* Edit config file
```
sudo nano /etc/ssmtp/ssmtp.conf
```

* Add this (replace with your Gmail credentials):
```
root=your_email@gmail.com
mailhub=smtp.gmail.com:587
AuthUser=your_email@gmail.com
AuthPass=your_gmail_app_password
UseTLS=YES
UseSTARTTLS=YES
```

7a. If the above doesn't work, use postfix
* Edit Postfix Configuration File
```
relayhost = [smtp.gmail.com]:587
smtp_use_tls = yes
smtp_sasl_auth_enable = yes
smtp_sasl_security_options =
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
smtp_sasl_mechanism_filter = plain
```

* Create Authentication File for Gmail SMTP
```
sudo nano /etc/postfix/sasl_passwd
```

* Add this line (replace with your actual Gmail credentials):
```
[smtp.gmail.com]:587 your_email@gmail.com:your_app_password
```

* Secure the Password File
```
sudo chmod 600 /etc/postfix/sasl_passwd
sudo postmap /etc/postfix/sasl_passwd
```

* Restart Postfix to Apply Changes
```
sudo systemctl restart postfix
```


8. Set up a cron job to run your trading bot
```
crontab -e
```

Add the following line (runs the trading bot script every weekday at 10am PST):
```
10 * * * 1-5 /usr/bin/python3 /home/ubuntu/deepseek_strategy.py >> /home/ubuntu/trading_log.txt 2>&1 && echo "Trading bot ran at $(date)" | mail -s "Trading Bot Notification" your_email@gmail.com
```

