import bs4
import requests
import json
import csv
import selenium.webdriver as webdriver

# ----------------------------------------------------------
# Turn webpage into a parseable BeautifulSoup object
# which represents the document as a nested data structure
# ----------------------------------------------------------
def getSoup(url):
    get_response = requests.get(url)
    soup = bs4.BeautifulSoup(get_response.text, "html.parser")
    return soup

# ----------------------------------------------------------
# Get a list of all occurrences of a particular class
# in the soup (note: type can be "div", "a", etc.)
# Returns ResultSet of tags
# ----------------------------------------------------------
def getClassInstances(soup, type, givenClass):
    result = soup.find_all(type, class_=givenClass)
    return result

# ----------------------------------------------------------
# Get the first of all occurrences of a particular class
# in the soup (note: type can be "div", "a", etc.)
# Returns a tag, which is a list containing a single object
# ----------------------------------------------------------
def getFirstClassInstance(soup, type, givenClass):
    result = soup.find_all(type, class_=givenClass)   
    if (len(result) >= 1):
        return result[0]
    else:
        print("Error: getFirstClassInstance - no class instances found")
        exit(0)

# ----------------------------------------------------------
# Sets up selenium webdriver for Chrome
# ----------------------------------------------------------
def getSeleniumDriverForChrome(url):
    option = webdriver.ChromeOptions()
    option.add_argument("--incognito")
    driver = webdriver.Chrome(executable_path='/Users/nsujela/Downloads/chromedriver2', chrome_options=option)
    return driver

# ----------------------------------------------------------
# Expands webpage to get all comments for a professor
# ----------------------------------------------------------
def seleniumExpansion(url, driver):
	print("Getting driver")
	chrome_driver = getSeleniumDriverForChrome(url)

	chrome_driver.get(url)

	print("Checking for automated test blocker")
	close_button = chrome_driver.find_element_by_xpath("//*[@id='cookie_notice']/a[1]")

	if close_button is not None:
	    print("Found close button")
	    close_button.click()
	    print("Clicked close button")
	else:
	    print("Did not find close button")
        
	print("Starting expansion")

	load_more = chrome_driver.find_element_by_id('loadMore')
	print(load_more)

	while (True):
		if load_more is None:
			break

		print("Found load more")
		load_more.click();
		print("Clicked close button")
		load_more = chrome_driver.find_element_by_xpath('loadMore')

	print("Expansion complete")


# ----------------------------------------------------------
# Compile a database of RMP *reviews* with the following 
# column fields: University(K), Professor(K), Average Rating(K),
# Student Ratings (Overall Quality and Level of Difficulty),
# Date, Tags, The Review Itself(K), Would Take Again, Grade 
# Received
# ----------------------------------------------------------

def one_iteration(url, global_index):
    # HTML Tags
    div = "div"
    a = "a"
    h1 = "h1"
    span = "span"
    td = "td"
    table = "table"
    p = "p"

    # Expand webpage fully
    # Note: load_more button not Selenium-clickable
    # Unable to expand
    # seleniumExpansion(url, driver)

    # Produce BeautifulSoup object for parsing
    soup = getSoup(url)

    print("-----")

    # University Name
    uniName = getFirstClassInstance(soup, a, "school").find_all(text=True, recursive=False)
    uniName = uniName[0]
    print("University: " + uniName)

    # Professor Name
    profName = getFirstClassInstance(soup, span, "pfname").find_all(text=True, recursive=False) + getFirstClassInstance(soup, span, "plname").find_all(text=True, recursive=False)
    profName[0] = profName[0].replace(" ", "").replace('\r', '').replace('\n', '') # First name
    profName[1] = profName[1].replace(" ", "").replace('\r', '').replace('\n', '') # Last name
    profName = profName[0] + " " + profName[1] # Stringify name

    print("Professor: " + profName)

    # Average Rating
    fivePointRating = getFirstClassInstance(soup, div, "grade").find_all(text=True, recursive=False)
    fivePointRating = fivePointRating[0]
    print("Average Professor Rating: " + fivePointRating)

    # Get all Review Information: Student Ratings, Grade Received, Would Take Again, Date, Tags, Review 
    table = getFirstClassInstance(soup, table, "tftable")

    # Get all reviews
    reviewBoxes = getClassInstances(soup, td, "comments")
    
    all_reviews = []    

    print("-----")
    for box in reviewBoxes:
        for child in box.children:
            if(child.name == 'p'):
                print("Review: ")
                text = child.text
                text_list = text.split(" ")
                text_list = text_list[20:] # Get rid of initial 20-ct whitespace
                text = " ".join(text_list)
                all_reviews.append(text)
    
    # Get all cells
    for row in table.find_all("tr")[1:]: # skip header
        cells = row.find_all(td)


    # Student Ratings: Overall Quality, Level of Difficulty
    all_quality = []
    all_difficulty = []

    quality_set = getClassInstances(soup, span, "score poor")
    for i in range(0, len(quality_set)):
        all_quality.append(quality_set[i].text)

    quality_set = getClassInstances(soup, span, "score average")
    for i in range(0, len(quality_set)):
        all_quality.append(quality_set[i].text)

    quality_set = getClassInstances(soup, span, "score good")
    for i in range(0, len(quality_set)):
        all_quality.append(quality_set[i].text)

    # -- Debugging --
    # print("length of all student quality scores")
    # print(len(all_quality))

    difficulty_set = getClassInstances(soup, span, "score inverse good")
    for i in range(0, len(difficulty_set)):
        all_difficulty.append(difficulty_set[i].text)

    difficulty_set = getClassInstances(soup, span, "score inverse average")
    for i in range(0, len(difficulty_set)):
        all_difficulty.append(difficulty_set[i].text)

    difficulty_set = getClassInstances(soup, span, "score inverse poor")
    for i in range(0, len(difficulty_set)):
        all_difficulty.append(difficulty_set[i].text)

    print("-----")
    print("Student Overall Quality Scores: ")
    for i in range(0, len(all_quality)):
        print(all_quality[i])
    
    print("-----")
    print("Student Difficulty Scores: ")
    for i in range(0, len(all_difficulty)):
        print(all_difficulty[i])

    # -- Debugging --
    # student_rating_boxes = getClassInstances(soup, td, "rating"_
    # print("student rating boxes")
    # print(student_rating_boxes[0].text)

    # Grade Received
    all_letter_grades = []

    grade_set = getClassInstances(soup, span, "grade")
    for item in grade_set:
        grade_text = item.text
        grade_text_arr = grade_text.split(": ")
        
        if (len(grade_text_arr) == 2):
            letter = grade_text_arr[1]

        all_letter_grades.append(letter)


    print("-----")    
    print("Letter Grades: ")
    for i in range(0, len(all_letter_grades)):
        print(all_letter_grades[i])


    all_would_take_again = []

    would_take_again_set = getClassInstances(soup, span, "would-take-again")
    for item in would_take_again_set:
        text = item.text
        text_arr = text.split(": ")
        
        if (len(text_arr) == 2):
            would_take_again = text_arr[1]

        all_would_take_again.append(would_take_again)

    print("-----")
    print("Would Take Again: ")
    for i in range(0, len(all_would_take_again)):
        print(all_would_take_again[i])


    all_annotations = []

    print("-----")
    print("Annotation: ")
    for i in range(0, len(all_would_take_again)):
        if (all_would_take_again[i] == "Yes"):
            all_annotations.append("pos")
        elif (all_quality[i] == "3") or (all_quality[i] == "4") or (all_quality[i] == "5"):
        	all_annotations.append("pos")
        else:
            all_annotations.append("neg")

    for annotation in all_annotations:
        print(annotation)

    filename = "rmp_dump.csv"

    with open(filename, 'a') as f1:
        writer = csv.writer(f1, delimiter=',')
        index = 0;
        
        # Annotate training set, not testing set
        for i in range(0, len(all_reviews)):
        	if (global_index <= 4000):
        		writer.writerow([index, uniName, profName, fivePointRating, all_reviews[i], all_letter_grades[i], all_quality[i], all_difficulty[i], all_would_take_again[i], all_annotations[i]])
        		index += 1
        	elif (global_index > 4000):
        		writer.writerow([index, uniName, profName, fivePointRating, all_reviews[i], all_letter_grades[i], all_quality[i], all_difficulty[i], all_would_take_again[i], ""])
        		index += 1


# ------------------------------------------------------------
# 						*	MAIN	*
# 	- Annotated training set: 4000 reviews
# 	- Non-annotated testing set: 1000 reviews
# ------------------------------------------------------------
def main():

	# Set up CSV header
	filename = 'rmp_dump.csv'
	with open(filename, 'w') as f1:
		writer = csv.writer(f1, delimiter=',')
		writer.writerow(["#", "University", "Professor", "Average Rating", "Review", "Grade Received", "Quality", "Difficulty", "Would Take Again", "Annotation"])

	template_url = "http://www.ratemyprofessors.com/ShowRatings.jsp?tid="

    # Get 10 reviews
	count = 0

	for i in range(111111,999999):

		if (count > 5000):
			break

		url = template_url + str(i)
		response = requests.get(url)

		bs = getSoup(url)
		page_not_found_set = getClassInstances(bs, "div", "header error")

		if (len(page_not_found_set) > 0):
			print("Page not found")

		else:
			# driver = getSeleniumDriverForChrome(url)
			print(url)
			try:
				print("Count: ")
				print(count)
				one_iteration(url, count)
				count +=1
				continue

			except:
				print("This iteration failed. Moving to the next one...")
				continue



# ----------
# S T A R T
# ----------

main()

# ----------
# 	E N D
# ----------


# --- OLD SCRAPERWIKI SCRIPT ---
# import scraperwiki
# from bs4 import BeautifulSoup
# import string
# import unicodedata
# import time

# headers = ["Name","Department","Total Ratings","Overall Quality","Easiness","Hot"]
# #Dictionary of school ids (keys) that map to tuple of school name and number of pages
# colleges = {"580":("MIT",16),"1222":("Yale",23),"181":("CMU",28), "1085":("UChicago",28),"1040":("Tufts",46), "1350":("Duke",84),"1255":("UTexas",84),"953":("Stanford",32),"799":("Rice",17),"780":("Princeton",16)}

# for sid in colleges.keys():
#     college,pages = colleges[sid]
#     print college
#     html = scraperwiki.scrape("http://www.ratemyprofessors.com/")

#     for i in xrange(1,pages+1):
#         response = scraperwiki.scrape("http://www.ratemyprofessors.com/SelectTeacher.jsp?sid=%s&pageNo=%s" % (sid,str(i)))
#         time.sleep(5)
#         soup = BeautifulSoup(response)
#         rows = soup.find_all("div",{"class":"entry odd vertical-center"})
#         rows.extend(soup.find_all("div",{"class":"entry even vertical-center"}))
#         for row in rows:
#             columns = row.find_all('div')
#             columns = columns[3:]
#             variables = {}
#             for i,col in enumerate(columns):
#                 value = unicodedata.normalize('NFKD', col.text).encode('ascii', 'ignore')
#                 variables[headers[i]] = value
#             variables["College"] = college
#             scraperwiki.sqlite.save(unique_keys=['Name',"Department"], data = variables)