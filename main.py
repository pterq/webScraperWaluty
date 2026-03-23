import requests
import bs4
import time
import datetime
import os
import math

file_name = "../Kursy walut - dane.csv"
starts_at_seconds = 20

url = "https://www.santander.pl/klient-indywidualny/karty-platnosci-i-kantor/kantor-santander"


def site_data_refresh_sync_start_countdown(seconds_when_to_start):
    # countdown to the start of scraping, to sync with data refresh on website
    current_time = datetime.datetime.now()

    while current_time.second != seconds_when_to_start:
        current_time = datetime.datetime.now()

        if current_time.second > seconds_when_to_start:
            remaining = 60 + (seconds_when_to_start - current_time.second)
        else:
            remaining = seconds_when_to_start - current_time.second

        print(f"\rWaiting: T-{remaining} ", end="")
        
        if remaining == 0:
            print("\n")
            break
        
        time.sleep(0.5)


def try_open_file(f_name, mode):
    modes = ['r', 'r+', 'w', 'w+', 'a', 'a+', ]

    if mode not in modes:
        print("Wrong mode")
        exit(1)
        return 1

    try:
        file_handle = open(f'{f_name}', mode)

        # Add first line to CSV file if file is empty
        if os.path.getsize(f_name) == 0:
            file_handle.write("Date;Time;EUR sell;EUR buy;USD sell;USD buy;CHF buy;CHF sell;GBP buy;GBP sell\n")

        return file_handle

    except FileNotFoundError:
        print(f'Couldnt open file: {f_name} | {FileNotFoundError}')
        exit(2)
        return 2


def get_bs4_request(f_url):
    is_done_not = True
    number_of_tries = 1
    wait = 5

    while is_done_not:
        try:   
            bs4_request =  bs4.BeautifulSoup(requests.get(f_url).text, "html.parser")
            is_done_not = False
            break
        except:
            print(f'Connection Error(Retrying in: {wait} seconds). Attempt: {number_of_tries}')
            is_done_not = True
            number_of_tries += 1
            time.sleep(wait)
            continue
    
    return bs4_request


if __name__ == "__main__":

    script_start_time = datetime.datetime.now() # used to determine whether a new day started

    # Open CSV file to append and/or create file
    file = try_open_file(file_name, "a")
    if not file:
        print("File error")
        print(f'{file_name}')
    
    print(f'Saving to file: "{file_name}"\n')
    file.close()

    
    print(f'Starts at: XX:XX:{starts_at_seconds}')

    # Wait for 20 seconds past a minute to start
    site_data_refresh_sync_start_countdown(starts_at_seconds)
    
    print("Date;Time;EUR sell;EUR buy;USD sell;USD buy;CHF buy;CHF sell;GBP buy;GBP sell")

    num_of_reads_today = 1
    while num_of_reads_today <= 24 * 60:
        file = try_open_file(file_name, "a")

        # Download request and processing data
        req = get_bs4_request(url)
        sellPrice = req.find_all("div", {"class": "exchange_office__table-value js-exchange_office__rate-sell-value"})
        buyPrice = req.find_all("div", {"class": "exchange_office__table-value js-exchange_office__rate-buy-value"})
        
        # Get current time and date
        time_now = datetime.datetime.now()
        
        if sellPrice and buyPrice:
            # holds full currency read from link site
            entry = []

            #  Add date to record entry
            todays_month = str(time_now.month)
            todays_day = str(time_now.day)

            # add "0" before month or date if month or date is a one digit long
            if len(todays_month) == 1:
                todays_month = f'0{todays_month}'
            if len(todays_day) == 1:
                todays_day = f'0{todays_day}'

            todays_date = f'{time_now.year}-{todays_month}-{todays_day}'
            entry.append(todays_date)

            # Add time to record entry
            entry.append(time.strftime("%H:%M:%S"))

            # Add currency sell and buy prices to record entry
            for i in range(4):
                entry.append(sellPrice[i].text.strip())
                entry.append(buyPrice[i].text.strip())

            # Save exchange rates to file
            save = ""
            for element in entry:
                save += f'{element};'

            save += "\n"
            file.write(save)
            file.close()

            # Print data in console
            print("----------------------------------------------------------------------------------------------------------------------------")
            print(f'| Record entry: {entry} |')
            for tekst in entry:
                print(tekst, end=';')
            print()

            #  print date and time
            print(f'| #: {num_of_reads_today} | {entry[0]} | {entry[1]} |')
            print("-----------------------------------")
            print("| Name | Sell   | Buy    | Spread |")
            print("-----------------------------------")

            # print currencies sell buy rates and their spread
            currency_names = ['EUR', 'USD', 'CHF', 'GBP']
            for i in range(2, 9, 2):
                print(f'| {currency_names[int(i/2)-1]}  | {entry[i]} | {entry[i+1]} | {"{:.4f}".format(float(entry[i+1].replace(",", ".")) - float(entry[i].replace(",", ".")))} |')
            print("-----------------------------------")

            # Check if there is a new day
            is_new_day = script_start_time.day != time_now.day

            if is_new_day:
                # restart main while loop
                num_of_reads_today = 0

                print(f'>NEW DAY!: {script_start_time.day}-{script_start_time.month}-{script_start_time.year} -> {time_now.day}-{time_now.month}-{time_now.year} | {num_of_reads_today}')
                # set current date to new day's date
                script_start_time = time_now

            else:
                print(f'>Not a new day!: {script_start_time.day}-{script_start_time.month}-{script_start_time.year} -> {time_now.day}-{time_now.month}-{time_now.year} | {num_of_reads_today} | Run time: ~ {0 if num_of_reads_today < 60 else math.floor(num_of_reads_today/60)} h : {num_of_reads_today % 60} min ')
                
        else:
            print("Data not found! (Retrying in: 60 seconds)")

        


        

        # Wait untill its 20 seconds past every minute for changes on the website
        time.sleep(0.5)
        time_now = datetime.datetime.now()
        while time_now.second != 20:
            time_now = datetime.datetime.now()
            # print(nowTime.second)
            time.sleep(0.5)


        num_of_reads_today += 1

    file.close()
    print(f'File {file_name} is closed')






