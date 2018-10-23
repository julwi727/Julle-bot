hi = ['yo', 'suh dude', 'tjenamors', 'morsning korsning', 'tjenare italienare', 'Hur står det till?', 'Vad görs bre', 'Fan tja det var inte igår', 'Hej']
bye = ['hejdå', 'Tjarå', 'Hörs bre', 'Peace bruh']
answers = ['men nu får ni fan ge er, robotar behöver också sova', 'Det beror lite på hur man ser på saken', 'arå', 'ja', 'yep', 'jafan', 'aa lätt', 'nej fan', 'nja', 'nej', 'nope', 'nah dude']
games = ['Overwatch', 'Guild Wars 2', 'Borderlands', 'Jackbox', 'Runescape', 'Tibia', 'CS:GO', 'Keep talking and Nobody Explodes', 'GTA V', 'Rocket League', 'Golf it!', 'Quake', 'Unreal Tournament', 'Warframe', 'CS Source', 'Heroes III', 'AoE II', 'Worms', 'Terraria', 'Starbound', 'Rollercoaster Tycoon 2', 'Riven', 'The Sims 3', 'Din mamma såklart']
defaults = ['fan saru din jävla knarkare', 'hörrö jag fattar inte', 'ingen aning om vad du pratar om']
good_foods = ['lite olika', 'beror på vad det är för temperatur i röven','kokain','knark','pizza', 'hamburgare', 'öl', 'lax', 'potatisgratäng']
bad_foods = ['grus', 'syre', 'skaldjursskit', 'avföring', 'rent kiss']

import datetime
import random

def get_hi():
    return random.choice(hi)

def get_bye():
    return random.choice(bye)

def get_answer():
    return random.choice(answers)

def get_game():
    return random.choice(games)

def get_default():
    return random.choice(defaults)

def get_good_food():
    return random.choice(good_foods)

def get_bad_food():
    return random.choice(bad_foods)

def process_message(msg):
    if '?' in msg:
        if 'vilket' in msg and 'spel' in msg:
            return get_game()

        elif 'vad' in msg and 'spel' in msg:
            return get_game()

        elif 'klockan' in msg: 
            now = datetime.datetime.now()
            response = 'Klockan är ' + now.strftime("%H:%M")  
            return response

        elif 'datum' in msg or 'dag' in msg:
            now = datetime.datetime.now()
            response = "Dagens datum är " + now.strftime("%Y-%m-%d")  
            return response

        elif 'vecka' in msg:
            now = datetime.datetime.now()
            response = 'Just nu är det vecka ' + now.strftime("%U")  
            return response

        elif 'favorit' in msg and 'mat' in msg:
            return get_good_food()

        elif 'inte' in msg and 'favorit' in msg and 'mat' in msg:
            return get_bad_food()

        elif 'mat' in msg and 'hatar' in msg:
            return get_bad_food()

        else:
            return get_answer()
    else:
        return get_default()