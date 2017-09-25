![shhhhbot avatar](https://raw.githubusercontent.com/javl/shhhhbot/master/img.jpg)

# shhhhBot #

shhhBot retweets tweets containing the phrase "don't tell anyone, but".

#### Usage ####
Run: `./shhhh.py`

Optional arguments:

* `-d`: drop the database
* `-v`: (up to 3 times) verbose mode

The last seen tweet's id gets saved to `info.sqlite` so the script knows where to continue from.

#### Run automatically ####
The easiest way is to add the script as a cronjob using `crontab -e`:
To look for new tweets every 10 minutes, use: `*/10 * * * * /usr/bin/python /path/to/shhhhbot.py`
