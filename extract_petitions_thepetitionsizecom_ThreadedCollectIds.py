proxies = []
import sys
import re
import urllib.request
import urllib.parse
import json
from collections import defaultdict
from datetime import datetime
from bs4 import SoupStrainer, BeautifulSoup
import concurrent.futures as futures
from time import sleep
import random
import glob

def log(msg):
    dt = datetime.now()
    print(dt.isoformat() + "\n" + str(msg), file=sys.stderr)

PETITIONSITE = ("http://www.thepetitionsite.com/takeaction")
PHPREQUEST = ("http://www.thepetitionsite.com/servlets/petitions/signatures.php")
ENV_URL_PREFIX = ("http://www.thepetitionsite.com/environment-and-wildlife/%d/")
ENV_ARCTIC = ("http://www.thepetitionsite.com/environment-and-wildlife/arctic/%d/")
ENV_ENDANGERED = ("http://www.thepetitionsite.com/environment-and-wildlife/endangered-species/%d/")
ENV_HEALTH = ("http://www.thepetitionsite.com/environment-and-wildlife/environmental-health/%d/")
ENV_CLI_CHANGE = ("http://www.thepetitionsite.com/environment-and-wildlife/global-warming-climate-change/%d/")
ENV_NAT_PARKS = ("http://www.thepetitionsite.com/environment-and-wildlife/global-warming-climate-change/%d/")
ENV_OCEANS = ("http://www.thepetitionsite.com/environment-and-wildlife/oceans/%d/")
ENV_OIL_DRILL = ("http://www.thepetitionsite.com/environment-and-wildlife/oil-drilling/%d/")
ENV_POLLUTION = ("http://www.thepetitionsite.com/environment-and-wildlife/pollution/%d/")
ENV_RAINFOREST = ("http://www.thepetitionsite.com/environment-and-wildlife/rainforest/%d/")
ENV_WHALES = ("http://www.thepetitionsite.com/environment-and-wildlife/whales/%d/")
ENV_WILDLIFE = ("http://www.thepetitionsite.com/environment-and-wildlife/wildlife/%d/")
ANIM_URL_PREFIX = ("http://www.thepetitionsite.com/animal-welfare/%d/")
ANIM_ABUSE = ("http://www.thepetitionsite.com/animal-welfare/animal-abuse/%d/")
ANIM_RESEARCH = ("http://www.thepetitionsite.com/animal-welfare/animal-research/%d/")
ANIM_FARM = ("http://www.thepetitionsite.com/animal-welfare/farm-animals/%d/")
ANIM_PETS = ("http://www.thepetitionsite.com/animal-welfare/pets/%d/")
EDU_URL_PREFIX = ("http://www.thepetitionsite.com/education/%d/")
HEALTH_URL_PREFIX = ("http://www.thepetitionsite.com/health/%d/")
HEALTH_AGING = ("http://www.thepetitionsite.com/health/aging/%d/")
HEALTH_CHILDREN = ("http://www.thepetitionsite.com/health/childrens-health/%d/")
HEALTH_DRUG = ("http://www.thepetitionsite.com/health/drug-safety/%d/")
HEALTH_FOOD = ("http://www.thepetitionsite.com/health/food-safety/%d/")
HEALTH_REPRODUCTIVE = ("http://www.thepetitionsite.com/health/reproductive-rights/%d/")
HEALTH_WOMEN = ("http://www.thepetitionsite.com/health/womens-health/%d/")
HUM_RIGHTS_URL_PREFIX = ("http://www.thepetitionsite.com/human-rights/%d/")
HUM_RIGHT_ARMED_CONFLICT = ("http://www.thepetitionsite.com/human-rights/armed-conflict-arms-trade/%d/")
HUM_RIGHT_CHILDREN = ("http://www.thepetitionsite.com/human-rights/childrens-rights/%d/")
HUM_RIGHT_CIVIL = ("http://www.thepetitionsite.com/human-rights/civil-rights/%d/")
HUM_RIGHT_DEATH_PENALTY = ("http://www.thepetitionsite.com/human-rights/death-penalty/%d/")
HUM_RIGHT_INTERNATIONAL = ("http://www.thepetitionsite.com/human-rights/international-justice/%d/")
HUM_RIGHT_PEACE = ("http://www.thepetitionsite.com/human-rights/peace-and-nonviolence/%d/")
HUM_RIGHT_REFUGEEES = ("http://www.thepetitionsite.com/human-rights/refugees/%d/")
HUM_RIGHT_TORTURE = ("http://www.thepetitionsite.com/human-rights/torture/%d/")
HUM_RIGHT_TERROR = ("http://www.thepetitionsite.com/human-rights/war-on-terror/%d/")
LGBT_URL_PREFIX = ("http://www.thepetitionsite.com/human-rights/gay-rights/%d/")
WOMEN_RIGHTS_URL_PREFIX = ("http://www.thepetitionsite.com/human-rights/womens-rights/%d/")
POLITICS_URL_PREFIX = ("http://www.thepetitionsite.com/politics/%d/")
POLITICS_CONSERVATIVE = ("http://www.thepetitionsite.com/politics/conservative/%d/")
POLITICS_INTERNATIONAL = ("http://www.thepetitionsite.com/politics/international/%d/")
POLITICS_PROGRESSIVE = ("http://www.thepetitionsite.com/politics/progressive/%d/")
CORP_URL_PREFIX = ("http://www.thepetitionsite.com/corporate-accountability/%d/")
CORP_CONSUMER = ("http://www.thepetitionsite.com/corporate-accountability/consumer-protection/%d/")
CORP_FAIR_TRADE = ("http://www.thepetitionsite.com/corporate-accountability/fair-trade/%d/")
CORP_LABOR = ("http://www.thepetitionsite.com/corporate-accountability/labor-workers-rights/%d/")
FAITH_URL_PREFIX = ("http://www.thepetitionsite.com/spirituality-and-religion/%d/")
ART_URL_PREFIX = ("http://www.thepetitionsite.com/media-arts-culture/%d/")
ART_FUNDING = ("http://www.thepetitionsite.com/media-arts-culture/arts-funding/%d/")
ART_CELEBRITIES = ("http://www.thepetitionsite.com/media-arts-culture/celebrities/%d/")
ART_GAMING = ("http://www.thepetitionsite.com/media-arts-culture/gaming/%d/")
ART_INDEP_MEDIA = ("http://www.thepetitionsite.com/media-arts-culture/independent-media/%d/")
ART_INTERNET = ("http://www.thepetitionsite.com/media-arts-culture/internet/%d/")
ART_MEDIA_ACCOUNTABILITY = ("http://www.thepetitionsite.com/media-arts-culture/media-accountability-reporting/%d/")
ART_MOVIES = ("http://www.thepetitionsite.com/media-arts-culture/movies/%d/")
ART_MUSEUMS = ("http://www.thepetitionsite.com/media-arts-culture/museums/%d/")
ART_MUSIC = ("http://www.thepetitionsite.com/media-arts-culture/music/%d/")
ART_NEWS = ("http://www.thepetitionsite.com/media-arts-culture/newspapers-magazines/%d/")
ART_PUBLIC_BROADCASTING = ("http://www.thepetitionsite.com/media-arts-culture/public-broadcasting/%d/")
ART_TV = ("http://www.thepetitionsite.com/media-arts-culture/television/%d/")


def prepareQueryUrl(prefix, page=1):
    return prefix % (page)

def requestHTML(url):
    if proxies:
        proxie = proxies[random.randint(0, len(proxies) - 1)]
        proxy_support = urllib.request.ProxyHandler(proxie)
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
    log("Requesting: " + url)
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
    response = urllib.request.urlopen(req)
    res = response.read().decode("utf-8", "ignore")
    log("Response returned: %s %s, %s" % (response.status, response.reason, str(len(res))))
    return res

def requestPOSTHTML(url, payload):
    if proxies:
        proxie = proxies[random.randint(0, len(proxies) - 1)]
        proxy_support = urllib.request.ProxyHandler(proxie)
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
    # log("Requesting post: " + url)
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
    # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    response = urllib.request.urlopen(req)
    res = response.read().decode("utf-8")
    log("***************POST Response returned: %s %s with lengths %s" % (response.status, response.reason, str(len(res))))
    return res

# Accepts petition Id in the form of /ddd/ddd/ddd/
def processSinglePetitionPage(petition_id, get_all_signers, last_seen_id=0, prefix=""):
    # petition_id, get_all_signers, last_seen_id = params
    petition_object = {}
    petition_id_concatenated = "".join(petition_id.split("/"))
    to_continue = True
    while to_continue:
        try:
            actual_petition_site = requestHTML(PETITIONSITE + petition_id)
            pet_page = BeautifulSoup(actual_petition_site)
            to_continue = False
        except Exception as e:
            log(str(e))
            to_continue = True
    title = pet_page.findAll("h1")[0].get_text()
    data = {
        'petitionID' : petition_id_concatenated,
        'type' : 'all'
    }
    data = bytes( urllib.parse.urlencode( data ).encode() )
    post_response = requestPOSTHTML(PHPREQUEST, data)
    numbers = json.loads(post_response)
    signers = numbers['signature_count']
    petition_object['petition_id'] = petition_id

    if int(last_seen_id) == 0: # or get_all_signers == 1:
        last_seen_id = 1
        owner_target = [e.getText() for e in pet_page.findAll("div", attrs={'id':'petition-col'})[0].findAll('li')]
        petition_object['owner'] = owner_target[0][4:] if len(owner_target) > 0 and owner_target[0].startswith("By:") else ""
        petition_object['target'] = owner_target[1][8:] if len(owner_target) > 1 and owner_target[1].startswith("Target:") else ""
        petition_object['signers'] = signers
        log("Number of signers " + str(signers))
        match = re.search("\"goal\":\"([0-9])+", actual_petition_site)
        goal = 1000
        if match:
            goal = int(match.group(0).split("\":\"")[1])
        petition_object['goal'] = goal
        petition_object['title'] = title
        petition_object['last_signers'] = numbers['signatures']
        if prefix:
            petition_object['topic'] = prefix.split("/")[-4] + "/" + prefix.split("/")[-3]
        overview = pet_page.find("div", {"class" : "overview"})
        updates = pet_page.find("div", {"class" : "updates"})
        letter = pet_page.find("div", {"class" : "letter"})
        category = owner_target[2] if len(owner_target) > 2 else ""
        if category:
            petition_object['category'] = ''.join([i if ord(i) < 128 else ' ' for i in category])
        if overview:
            petition_object['description_overview_text'] = overview.text
        if letter:
            petition_object['description_letter_text'] = letter.text
        if updates:
            petition_object['description_updates'] = "_____@@@@@_____".join([e.text for e in updates.findAll('div', {'class' : 'update'})])
    else:
        petition_object['signers'] = signers
        if int(numbers['signatures'][-1]['number']) > last_seen_id:
            petition_object['last_signers'] = numbers['signatures']
        elif int(numbers['signatures'][-1]['number']) <= last_seen_id:
            petition_object['last_signers'] = numbers['signatures'][:last_seen_id]
        # update this information in case it was not done already
        overview = pet_page.find("div", {"class" : "overview"})
        updates = pet_page.find("div", {"class" : "updates"})
        letter = pet_page.find("div", {"class" : "letter"})
        owner_target = [e.getText() for e in pet_page.findAll("div", attrs={'id':'petition-col'})[0].findAll('li')]
        category = owner_target[2] if len(owner_target) > 1 else ""
        if category:
            petition_object['category'] = ''.join([i if ord(i) < 128 else ' ' for i in category])
        if overview:
            petition_object['description_overview_text'] = overview.text
        if letter:
            petition_object['description_letter_text'] = letter.text
        if updates:
            petition_object['description_updates'] = "_____@@@@@_____".join([e.text for e in updates.findAll('div', {'class' : 'update'})])

    if get_all_signers and petition_object['last_signers']:
        still_to_process = petition_object['last_signers'][-1]['number'] if len(petition_object['last_signers']) > 0 else 0
        log("Last_seen_id id " + str(last_seen_id))
        while int(still_to_process) > int(last_seen_id):
            log("Still to process: " + str(still_to_process) + " until " + str(last_seen_id))
            data = {
                'petitionID' : str(petition_id_concatenated),
                'type' : 'signatures',
                'last_sig' : str(still_to_process)
            }
            to_continue = 0
            while to_continue < 5:
                data = bytes( str("petitionID="+str(petition_id_concatenated)+"&last_sig=" + str(still_to_process) + "&type=signatures").encode("utf-8") )
                try:
                    post_response = requestPOSTHTML(PHPREQUEST, data)
                    if len(post_response) > 0:
                        additional_signatures = json.loads(post_response)['signatures']
                        to_continue = 5
                    else:
                        sleep(1)
                        still_to_process = int(still_to_process) - 1 if int(still_to_process) > 0  else 0
                        log("*************RETRYING LOWER LAST_SIGN******** " + str(still_to_process))
                        continue
                except urllib.error.HTTPError as HTTP:
                    log(str(HTTP))
                    additional_signatures = {}
                    to_continue += 1
                    if to_continue > 4:
                        exit(1)
                    sleep(1)
                except Exception as e:
                    sleep(1)
                    # still_to_process = int(still_to_process) - 1 if int(still_to_process) > 0  else 0
                    #log(str(e) + "*************RETRYING LOWER LAST_SIGN******** " + str(still_to_process))
                    to_continue += 1
                    additional_signatures = {}
                    #if to_continue == 4:
                    #    log("Returning object slightly earlier")
                    #    return {} #petition_object
            #log("len additional" + str(len(additional_signatures)))
            if len(additional_signatures) > 0 and len(additional_signatures[-1]['number']) > 0:
                still_to_process = additional_signatures[-1]['number']
            else:
                still_to_process = 0
            #log("updated still to process " + str(still_to_process))
            if int(still_to_process) <= int(last_seen_id):
                additional_signatures = [el for el in additional_signatures if (len(el['number']) > 0 and int(el['number']) > int(last_seen_id)) or int(last_seen_id) == 1]
            log("Updates still to process: " + str(still_to_process))
            petition_object['last_signers'].extend(additional_signatures)
    log("Returning object")
    log("NumSignatures: " + str(len(petition_object['last_signers'])))
    return petition_object

def processPetitionPage(response, get_all_signers, existing={}, prefix=""):
    page = BeautifulSoup(response)
    resulting_petition_dict = {}
    if len(page.findAll("div", {"class": "petitions_list"})) > 0:
        petitions_list = [ elem for p_list in page.findAll("div", {"class": "petitions_list"}) for elem in p_list.findAll("div", {"class":"petition"}) ]
    else:
        log("No petitions on the page!")
        return resulting_petition_dict
    num_workers = 1
    petition_ids = []
    for pet_entry in petitions_list:
        # try:
        pet_url = pet_entry.findAll("a", {"class" : "sign_button"})[0]['href']
        # except Exception as e:
        #    log(str(e))
        #    continue
        id_match = re.findall('/[0-9]{1,3}/[0-9]{1,3}/[0-9]{1,3}/', pet_url)
        if len(id_match) > 0:
            petition_id = id_match[0]
            petition_ids.append(petition_id)
        else:
            continue
        if PETITIONSITE + petition_id in existing:
            petition_ids.append((petition_id, get_all_signers, int(existing[PETITIONSITE + petition_id]), prefix))
        else:
            petition_ids.append((petition_id, get_all_signers, 0, prefix))
    return petition_ids

def query(prefix, page, get_all_signers):
    existing = {}
    log("Loading page: %s " % (prefix % (page)) )
    get_all_signers = 1
    petition_urls = []
    to_continue = True
    while to_continue:
        try:
            response = requestHTML(prepareQueryUrl(prefix, page))
            log("query: " + prefix % (page))
            to_continue = False
            petition_objects = processPetitionPage(response, get_all_signers, existing, prefix[31:-4])
            if len(petition_objects) == 0:
                return petition_urls
            petition_urls.extend(petition_objects)
            log("Page " + str(page) + " is DONE")
        except urllib.error.HTTPError as HTTP:
            log(str(HTTP))
            sleep(5)
            to_continue = False
        except Exception as e:
            log(str(e))
            sleep(5)
            to_continue = True
    return petition_urls

def main(argv):
    petitions = {}
    num_workers = 10 if len(argv) <= 1 else int(argv[1])
    input_pages = 500
    get_all_signers = 1
    if len(argv) > 2:
        collected_ids_file = argv[2]
    if len(argv) > 3:
        output_path = argv[3]
    log("Loading number of pages: %d" % (input_pages) )

    do_not_use = {}

    if collect_ids:
        for prefix in [ENV_URL_PREFIX, ENV_ARCTIC, ENV_ENDANGERED, ENV_HEALTH, ENV_CLI_CHANGE, ENV_NAT_PARKS, ENV_OCEANS, ENV_OIL_DRILL, ENV_POLLUTION, ENV_RAINFOREST, ENV_WHALES, ENV_WILDLIFE, ANIM_URL_PREFIX, ANIM_ABUSE, ANIM_RESEARCH, ANIM_FARM, ANIM_PETS, EDU_URL_PREFIX, HEALTH_URL_PREFIX, HEALTH_AGING, HEALTH_CHILDREN, HEALTH_DRUG, HEALTH_FOOD, HEALTH_REPRODUCTIVE, HEALTH_WOMEN, HUM_RIGHTS_URL_PREFIX, HUM_RIGHT_ARMED_CONFLICT, HUM_RIGHT_CHILDREN, HUM_RIGHT_CIVIL, HUM_RIGHT_DEATH_PENALTY, HUM_RIGHT_INTERNATIONAL, HUM_RIGHT_PEACE, HUM_RIGHT_REFUGEEES, HUM_RIGHT_TORTURE, HUM_RIGHT_TERROR, LGBT_URL_PREFIX, WOMEN_RIGHTS_URL_PREFIX, POLITICS_URL_PREFIX, POLITICS_CONSERVATIVE, POLITICS_INTERNATIONAL, POLITICS_PROGRESSIVE, CORP_URL_PREFIX, CORP_CONSUMER, CORP_FAIR_TRADE, CORP_LABOR, FAITH_URL_PREFIX, ART_URL_PREFIX, ART_FUNDING, ART_CELEBRITIES, ART_GAMING, ART_INDEP_MEDIA, ART_INTERNET, ART_MEDIA_ACCOUNTABILITY, ART_MOVIES, ART_MUSEUMS, ART_MUSIC, ART_NEWS, ART_PUBLIC_BROADCASTING, ART_TV]:
            page = 1
            while page <= input_pages:
                try:
                    p = query(prefix, page, get_all_signers)
                    print(json.dumps(p))
                    if len(p) == 0:
                        break
                    page += 1
                except Exception as e:
                    page += 1
                    log(str(e))
                    break
    else:
        # command:
        # python extract_petitions.py 10 ids.json output_
        pet_ids = [el in json.loads(open(collected_ids_file, 'r').read()) ]
        pet_ids = [el for el in pet_ids if str(PETITIONSITE + el[0]) not in do_not_use]
        log("Len petitions to check yet: " + str(len(pet_ids)))
        with futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            # params: petition_id, get_all_signers=1, last_seen_id=0, prefix=""
            ps = {executor.submit(processSinglePetitionPage, pet_id[0], pet_id[1], pet_id[2], pet_id[3]): pet_id for pet_id in pet_ids}
            for p in futures.as_completed(ps):
                log("************************PETITION TO BE WRITTEN!!!****************")
                dt = datetime.now()
                try:
                    res_dump = json.dumps(p.result())
                    log("DUMPED")
                    open(output_path + "_" + dt.isoformat() + ".json", "w").write(res_dump)
                except Exception as e:
                    log(str(e))
                    continue
                log("************************PETITION IS WRITTEN!!!****************")

if __name__ == "__main__":
    main(sys.argv)
