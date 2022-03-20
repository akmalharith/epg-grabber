import os
from app import scrape
from config.constants import CONFIG_DIR, TESTS_FILE

def load_config_for_tests():
    os.remove(TESTS_FILE)
    
    config_items = []

    for config_file in os.listdir(CONFIG_DIR):

        with open(os.path.join(CONFIG_DIR,config_file))as file:
            firstline = file.readline().rstrip()
            config_items.append(firstline)

        with open(TESTS_FILE, "a") as testfile:
            testfile.write(firstline+"\n")
            testfile.close()

load_config_for_tests()
scrape()
