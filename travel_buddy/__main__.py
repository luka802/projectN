from travel_buddy.bot import TravelBuddy


def main():
    bot = TravelBuddy()
    print(bot.start())
    while not bot.closed:
        try:
            text = input('\nYou: ')
            answer = bot.reply(text)
        except (EOFError, KeyboardInterrupt):
            print()
            answer = bot.reply('exit')
        print('\nTravelBuddy:', answer)


if __name__ == '__main__':
    main()
