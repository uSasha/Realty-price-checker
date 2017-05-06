## Realty price checker
### Log realty prices from Cian.ru ads to Google spreadsheets 

During 2014-2016 Russian economics was very volatile but realty market was relatively stable. All realty agencies reports were like nothing happens and it's still 2013 on the market. For me it was especially interesting are median prices are going down, is time-to-deal grows? Also situation could be different with different apartment types. My idea was to find ads of different kinds of realty, write it to excel and update prices weekly. Soon I realized that it’s very time consuming. 
So I made some automation. This script works with Google docs spread sheets. You should add links to realty ads on cian.ru and script will run thru all links and add current prices to last column and add the date. 

Note that this script will not restart automatically, to do it I recommend to use cron.
