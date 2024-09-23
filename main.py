import discord
import matplotlib.pyplot as plt
import numpy as np
import os
import time
import threading
import pandas as pd
from collections import deque 
import asyncio

from dotenv import load_dotenv
from tabulate import tabulate
from discord.ext import commands 
from tcp_latency import measure_latency

from postgres import insert_data
from postgres import aggregate_data
from postgres import retrive_channel_data

intents = discord.Intents.all()
client = commands.Bot(command_prefix = '!',intents = intents)

@client.event
async def on_ready():
    print("The bot is online")
    print("---------------------------")


hosts = {
    '1': '35.155.204.207',
    '2': '52.26.82.74',
    '3': '34.217.205.66',
    '4': '35.161.183.101',
    '5': '54.218.157.183',
    '6': '52.25.78.39',
    '7': '54.68.160.34',
    '8': '34.218.141.142',
    '9': '52.33.249.126',
    '10': '54.148.170.23',
    '11': '54.201.184.26',
    '12': '54.191.142.56',
    '13': '52.13.185.207',
    '14': '34.215.228.37',
    '15': '54.187.177.143',
    '16': '54.203.83.148',
    '17': '54.148.188.235',
    '18': '52.43.83.76',
    '19': '54.69.114.137',
    '20': '54.148.137.49',
    '21': '54.212.109.33',
    '22': '44.230.255.51',
    '23': '100.20.116.83',
    '24': '54.188.84.22',
    '25': '34.215.170.50',
    '26': '54.184.162.28',
    '27': '54.185.209.29',
    '28': '52.12.53.225',
    '29': '54.189.33.238',
    '30': '54.188.84.238',
    '31': '44.234.162.14',
    '32': '44.234.162.13',
    '33': '44.234.161.92',
    '34': '44.234.161.48',
    '35': '44.234.160.137',
    '36': '44.234.161.28',
    '37': '44.234.162.100',
    '38': '44.234.161.69',
    '39': '44.234.162.145',
    '40': '44.234.162.130'
}

#ping ip addresses from host and store it into result
def record_latency(host, channel, results):
    start = time.time()
    ping = measure_latency(host = host, port=8585, runs = 15, wait = 0)
    # elapse_time = time.time() - start 
    std = np.std(ping)
    std = float(std)
    avg_ping = sum(ping)/len(ping)
    results.append([channel, avg_ping, std])    

    
async def main(ctx):
    start = time.time()
    # Right now, we are calling the meausre_latency API for every channel within the main thread
    # One optimization is make each of these calls in its own thread
    # for Ch,Ip in hosts.items(): 
    # tasks.append(record_latency(Ip,Ch))
    results = []
    
    #enabling multithreads processing
    threads = []
    for i, (ch, ip) in enumerate(hosts.items()):
        thread = threading.Thread(target=record_latency, args=(ip, ch, results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    
    #initial ping data stores into result variable
    results = sorted(results, key=lambda x : int(x[0]))
    table = tabulate(results, tablefmt="plain")
    channel = [row[0] for row in results]
    avg_ping = [row[1] for row in results]
    std = [row[2] for row in results]
    
    # insert data into PostgreSQL database and aggregate the data of past 5 mins 
    insert_data(channel, avg_ping, std)
    channel_avg_results = aggregate_data()
    results = sorted(channel_avg_results, key=lambda x : int(x[0]))
    table = tabulate(results, tablefmt="plain")
    channel = [row[0] for row in results]
    avg_ping = [row[1] for row in results]
    std = [row[2] for row in results]    

    df = pd.DataFrame(results, columns = ['Channel', 'avg_Ping', 'std'])
    df['std'] = pd.to_numeric(df['std'])
    top_5_channel_std = df.sort_values(by='std', ascending=False).head(5)['Channel'].astype(int).tolist()
    low_5_channel_avg = df.sort_values(by ='avg_Ping', ascending=False).head(5)['Channel'].astype(int).tolist()
    
    # Split the table into chunks if it's too long
    # max_length = 1900  # Discord's message limit is 2000, we leave some room
    # table_chunks = [table[i:i+max_length] for i in range(0, len(table), max_length)]

    # style data on discord with embedding
    embed = discord.Embed(
        title="Latency Bot",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Channel",
        value="\n".join(str(row) for row in channel),
        inline=True
    )
    embed.add_field(
        name="Average Latency",
        value="\n".join(str(row) for row in avg_ping),
        inline=True
    )
    embed.add_field(
        name="Standard Deviation",
        value="\n".join(str(row) for row in std),
        inline=True
    )
    embed.add_field(
        name="Top 5 Most Unstable Channels Based on Standard Deviation (ms)",
        value= ', '.join(str(channel) for channel in top_5_channel_std),
        inline=False
    )
    embed.add_field(
        name="Worst 5 Channels based on Average Ping (ms)",
        value= ', '.join(str(channel) for channel in low_5_channel_avg),
        inline=False
)
    

    # Let's make sure this asynchronous call is legit
    # try:
    #     await ctx.send(embed = embed)
    # except discord.errors.HTTPException as e:
    #     await ctx.send(f"An error occurred while sending the message: {str(e)}")
    return embed

    elapsed_time = time.time() - start
    print(elapsed_time)
    
    
def measure_channel_ping(channel):
    ping = []
    host = hosts[channel]
    ping = measure_latency(host = host, port=8585, runs = 15, wait = 0)
    return ping

@client.command()
async def ping_graph(ctx, channel):
    data = retrive_channel_data(channel=channel)
    avg_ping = [item[0] for item in data]
    plt.figure(figsize=(10, 6))
    plt.plot(avg_ping, color='#1ABC9C') 
    plt.ylabel('Latency (ms)', color='white')  
    plt.gca().set_xticks([])
    plt.gca().set_facecolor('#2c2d31')  
    plt.gcf().set_facecolor('#2c2d31')  
    plt.grid(True, color='#7289DA', linestyle='-', linewidth=0.5, axis='y') 
    plt.tick_params(colors='white') 

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    plt.savefig("ping_chart.png", bbox_inches='tight', facecolor='#2c2d31')
    plt.close()  

    with open("ping_chart.png", "rb") as f:
        file = discord.File(f)

        embed = discord.Embed(
            title = f'Channel: {channel} Latency',
            color=discord.Color.blue()
        )
        embed.set_image(url="attachment://ping_chart.png")
        await ctx.send(embed= embed, file= file)    

@client.command()
async def check_ping(ctx, host=None):
    message = None
    while True:
        updated_embed = await main(ctx) 
        if message is None:
            message = await ctx.send(embed=updated_embed)
        else:
            await message.edit(embed=updated_embed)
            
        await asyncio.sleep(15) 

# Load environment variables from .env file
load_dotenv()
token = os.getenv('TOKEN')
client.run(token)