import json

# Read the cards.json file
with open("./cards.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# Extract the card field from each object in the array
cards = [card_obj["card"] for card_obj in data]

# Write the cards to cards.txt file
with open("cards.txt", "w", encoding="utf-8") as txt_file:
    for card in cards:
        txt_file.write(card + "\n")
