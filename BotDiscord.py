import discord
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
import asyncio
import os
from dotenv import load_dotenv

if __name__ == '__main__':

    cmc = CoinMarketCapAPI('')

    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    alert = []

    client = discord.Client()

    def loading():
        alertFile = open("Alert.txt", "r+")
        for line in alertFile:
            try:
                print(alert[int(alert.index(line.split(" ")[0]))])
            except Exception as error:
                addingNewCrypto(line.split(" ")[0])
            alert[int(alert.index(line.split(" ")[0]) + 1)].append(float(line.split(" ")[1]))
        print(alert)
        return "loaded !"

    def addingNewCrypto(xcrypto):
        alert.append(xcrypto)
        alert.append([])

    def saving():
        alertFile = open("Alert.txt", "w+")
        for i in range(0,len(alert),2):
            print(alert[i])
            for prc in alert[i+1]:
                alertFile.write(alert[i]+" "+str(prc)+"\n")

    def removingAlert(xcrypto, yalert):
        print(alert[int(alert.index(xcrypto) + 1)][alert[int(alert.index(xcrypto)+1)].index(float(yalert))])
        alert[int(alert.index(xcrypto) + 1)].remove(alert[int(alert.index(xcrypto) + 1)][alert[int(alert.index(xcrypto)+1)].index(float(yalert))])
        emb = discord.Embed(title=xcrypto + "USD Alert",
                            description=" Alerte enlevée au prix de : " + str(yalert) + "$",
                            color=discord.Colour(0xFFE377),
                            )
        saving()
        return emb

    def addingAlert(xcrypto, yalert):
        alertFile = open("Alert.txt", "a")
        try:
            print(alert[int(alert.index(xcrypto) + 1)])
        except Exception as error:
            addingNewCrypto(xcrypto)
        alert[int(alert.index(xcrypto) + 1)].append(yalert)
        logo = cmc.cryptocurrency_info(symbol=xcrypto).data[xcrypto]['logo']
        t = cmc.cryptocurrency_categories(symbol=xcrypto)
        r = cmc.cryptocurrency_category(id=t.data[0]['id'])
        emb = discord.Embed(title=xcrypto + "USD Alert",
                            description=" Alerte ajoutée au prix de : " + str(yalert) + "$",
                            color=discord.Colour(0xFFD367),
                            )
        emb.set_thumbnail(
            url=logo
        )
        saving()
        return emb

    def upOrDown(percent):
        if percent < 0:
            return "▼"
        elif percent > 0:
            return "▲"
        else:
            return "-"

    def redOrGreen(p1,p2,p3):
        indi=p1*0.5+p2+p3*0.25
        if indi < 0:
            if abs(indi) < 10:
                return int('0x%02x%02x%02x' % (255,230,0),0)
            elif abs(indi) < 25:
                return int('0x%02x%02x%02x' % (255, 125, 0), 0)
            elif abs(indi) < 50:
                return int('0x%02x%02x%02x' % (255, 0, 0), 0)
            elif abs(indi) < 75:
                return int('0x%02x%02x%02x' % (125, 0, 0), 0)
            elif abs(indi) < 100:
                return int('0x%02x%02x%02x' % (50, 0, 0), 0)
            else:
                return int('0x%02x%02x%02x' % (255, 255, 0), 0)
        elif indi > 0:
            if indi < 20:
                return  int('0x%02x%02x%02x' % (230,255,0),0)
            elif indi < 50:
                return int('0x%02x%02x%02x' % (125, 255, 0), 0)
            elif indi < 100:
                return int('0x%02x%02x%02x' % (0, 255, 0), 0)
            elif indi >= 100:
                return int('0x%02x%02x%02x' % (0, 150, 0), 0)
            else:
                return int('0x%02x%02x%02x' % (255, 255, 0), 0)
        else:
            return int('0x%02x%02x%02x' % (255, 255, 0))

    def alerting(xcrypto, yalert):
        print("oe")


    def tellPrice(xcrypto):
        logo = cmc.cryptocurrency_info(symbol=xcrypto).data[xcrypto]['logo']
        t = cmc.cryptocurrency_categories(symbol=xcrypto)
        r = cmc.cryptocurrency_category(id=t.data[0]['id'])
        for i in range(len(r.data['coins'])):
            if r.data['coins'][i]['symbol'] == xcrypto:
                cryptoPrice=r.data['coins'][i]['quote']['USD']['price']
                cryptoPercent1h=r.data['coins'][i]['quote']['USD']['percent_change_1h']
                cryptoPercent24h=r.data['coins'][i]['quote']['USD']['percent_change_24h']
                cryptoPercent7d=r.data['coins'][i]['quote']['USD']['percent_change_7d']
                break
        emb = discord.Embed(title=xcrypto + "USD",
            description=xcrypto + " au prix de : " + str(
            "{:.8f}".format(cryptoPrice))+ "$\n\n" +
            "Dernière heure : " + str(cryptoPercent1h)+"% "+ upOrDown(cryptoPercent1h) + "\n"
            "Dernières 24 heures : " + str(cryptoPercent24h)+"% "+ upOrDown(cryptoPercent24h) + "\n"
            "Cette semaine : " + str(cryptoPercent7d)+"% "+ upOrDown(cryptoPercent7d) + "\n",
            color=discord.Colour(redOrGreen(cryptoPercent1h,cryptoPercent24h,cryptoPercent7d)),
            url=f"https://fr.tradingview.com/chart/USy4FDma/?symbol=COINBASE%3A" +xcrypto + "USD")
        emb.set_thumbnail(
            url=logo
        )
        return emb

    @client.event
    async def on_ready():
        print("Le bot est prêt !")


    async def my_background_task():
        await client.wait_until_ready()
        channel = client.get_channel(id=922418862958444544)
        print(loading())
        while not client.is_closed():
            try:
                for i in range(0,len(alert),2):
                    t = cmc.cryptocurrency_categories(symbol=alert[i])
                    r = cmc.cryptocurrency_category(id=t.data[0]['id'])
                    cryptoPrice = r.data['coins'][i]['quote']['USD']['price']
                    for j in range(len(alert[i+1])):
                        print(alert[i],alert[i+1][j], i , j)
                        if abs((float(cryptoPrice)/float(alert[i+1][j]))-1) <= 0.025:
                            await channel.send("@everyone "+alert[i]+" au prix de : "+str(alert[i+1][j])+"$ !")
                            removingAlert(alert[i],alert[i+1][j])
            except Exception as error:
                print(error)
            await asyncio.sleep(120)

    @client.event
    async def on_message(message):
        print(message.content)

        if message.content == "list alert":
            for i in range(0,len(alert),2):
                for j in range(len(alert[i+1])):
                    await message.channel.send(
                        embed=discord.Embed(title="Alerte", description="Alerte de " + alert[i] + " au prix de : " + str(alert[i+1][j]) + "$",
                                            color=discord.Colour(0xF0F0F0)))

        if message.content.split(" ")[0] == "remove":
            try:
                await message.channel.send(embed=removingAlert(message.content.split(" ")[1],message.content.split(" ")[2]))
            except Exception as error:
                await message.channel.send(
                    embed=discord.Embed(title="Error", description="Alerte introuvable.",
                                        color=discord.Colour.red()))

        if message.content.split(" ")[0] == "set":
            try:
                await message.channel.send(embed=addingAlert(message.content.split(" ")[1],message.content.split(" ")[2]))
            except Exception as error:
                await message.channel.send(
                    embed=discord.Embed(title="Error", description="Token introuvable.",
                                        color=discord.Colour.red()))

        if message.content.split(" ")[0] == "price":
            try:
                await message.channel.send(embed=tellPrice(message.content.split(" ")[1].upper()))
            except Exception as error:
                await message.channel.send(embed=discord.Embed(title="Error", description="Token ou monnaie introuvable.", color=discord.Colour.red()))

    client.loop.create_task(my_background_task())
    client.run(TOKEN)
