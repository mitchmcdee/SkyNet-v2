from bs4 import BeautifulSoup
import urllib3
all_scraped = []
names_or_url = ["Ant","Spider","Snail","Crab","Frog","Turtle"]
all_scraped += names_or_url
names_lower = []
for word in names_or_url:
    names_lower.append(word.lower())
print(names_lower)
http = urllib3.PoolManager()
new_dict = []
for url_name in names_lower:
    url = "http://wordbrain.org/"+url_name+"/"
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data, "html.parser")
    parent = soup.find("div", class_="entry-content clearfix")
    p_children = parent.findChildren("p")
    for child in p_children:
        word = str(child.find(text=True, recursive=False)).strip('\r').strip('\n')
        if (type(word) is str) and len(word) > 2 and (len(word) < 70):
            word_list = word.split(" – ")
            new_dict += word_list

penguin_words = ["Table – Record – North","Cupboard – Oval – Roof","Lantern – Ask – Barrel","Pencil – Earth – Sheep","Celery – Thick – Slide","Tongue – Mirror – Crow","Trophy – Nurse – Melon","Butter – Bacon – Drink","Meat – Sheep – Bat – Card","Bag – Nut – Dream – Cabin","Gloves – Bag – Keyring","Goat – Bullet – Orange","Hatchet – Nut – Stilts","Flag – Neck – Starfish","Switch – Drink – Piano","Trombone – Tricycle","Roof – Empty – Jump – Tin","Card – Necktie – Spray","Saw – Hen – Crow – Finger","Scissors – Wink – Heel"]
print("PENGUIN")
all_scraped += ["Penguin"]
for word in penguin_words:
    word_list = word.split(" – ")
    new_dict += word_list
    print(word_list)
sheep = "GoldFish – Cemetery – Jam – boot – Trowel – Tin – Mouse – Butter – Spoon – Timber – TV – Oar – Twins – Screw – Twins – Rabbit – BarBell – Tepee – Moth – Meat – Sheriff – Boots – Talk – Root – Haystack – Bullet – Sock – Bottle – Aerial – Bag – TV – Shoes – Anchor – Scooter – Elk – Cap – Record – Chimney – Scooter – Mince – Edge – Crab – Biscuit – Smell – Small – Camera – Skirt – Ruler – Bullet – Onion – Block – Volcano – Boot – Kitten – Puzzle – Barn – Cheese – Axe – Keyring"
sheep_word_list = sheep.split(" – ")
print("SHEEP")
all_scraped += ["Sheep"]
print(sheep_word_list)
new_dict += sheep_word_list

shark = "Lapel – Bathroom – Bat – Pumpkin – Sugar – Soup – Tail – DoorBell – Bald – bullet – onion – heart – Nail – Patient – Peach – Oval – tongue – pencil – Duck – Elevator – Crab – Bomb – Fly – Boot – Snail – Infinity – Birthday – Palm – Drink – Rope – Bed – Heart – Ruler – Record – Floor – Buckle – Skull – Coconut – Loop – Canoe – Tent – Mailbox – Bacon – Steak – Patient – Fork – Collar – Dress – Cheek – Trunk – Rocket – Ghost – Eagle – Pencil – Think – Snowman – Path – Cabin – Music – Toilet – Punch"
shark_word_list = shark.split(" – ")
print("SHARK")
all_scraped += ["Shark"]
print(shark_word_list)
new_dict += shark_word_list

names_or_url = ["Snake"]
all_scraped += ["Snake"]
names_lower = []
for word in names_or_url:
    names_lower.append(word.lower())

for url_name in names_lower:
    print(url_name.upper())
    url = "http://wordbrain.org/"+url_name+"/"
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data, "html.parser")
    parent = soup.find("div", class_="entry-content clearfix")
    p_children = parent.findChildren("p")
    for child in p_children:
        if child.a is None:
            continue
        word = str(child.a.find(text=True, recursive=False)).strip('\r').strip('\n')
        if (type(word) is str) and len(word) > 2 and (len(word) < 70):
            word_list = word.split(" – ")
            print(word_list)
            for word in word_list:
                if len(word) < 15:
                    new_dict += [word]
print(new_dict)
with open("scrape_dict.txt","w") as dict_file:
    dict_file.truncate()
    new_dict.sort()
    for word in new_dict:
        dict_file.write(word.lower() + "\n")
print(all_scraped)
