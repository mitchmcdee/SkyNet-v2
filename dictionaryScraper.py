import requests
from bs4 import BeautifulSoup

base = 'http://wordbrain.info/en/'
levels = ['ant','spider','snail','crab','frog','turtle','penguin','snake',
          'rat','sheep','shark','cat','elephant','whale','octopus','pig',
          'lion','squirrel','owl','monkey','student','clown','waiter',
          'policeman','chef','teacher','doctor','astronaut','scientist',
          'alien','dinosaur','dragon','monster','robot','unicorn']

# Ensure we have a unique set of words
words = set()

# Loop over the given levels
for level in levels:
    print("Scraping solutions from " + level)

    request = requests.get(base + level)
    soup = BeautifulSoup(request.text, 'html.parser')
    solutions = soup.findAll("span", {"class": "solution"})

    # For each solution on the page, split its solutions and add them to the set
    [[words.add(s) for s in solution.text.split(',')] for solution in solutions]

print("Writing to file")
# Write set to a file
with open('scrapedWords.txt','w') as f:
    f.write(('\n').join(sorted(words)))

print("Done!")