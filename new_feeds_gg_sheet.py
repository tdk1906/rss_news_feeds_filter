from bs4 import BeautifulSoup as soup
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
import requests, pickle, feedparser, datetime, gspread, ssl, time

# GET CONTENT FROM NORMAL LINK
def content(link):
	# CHANGE GOOGLE RSS REDIRECT LINK TO FINAL LINK
	if "www.google.com" in link:
		link = requests.get(link)
		link = link.text.partition("URL='")[-1].rpartition("'\"")[0]
	#
	# LOAD HTML AND FIND ALL TEXT IN <P> TAGS IN HTML FILE
	r = requests.get(link);
	page_soup = soup(r.content, "html.parser")
	temp = page_soup.find_all("p", text=True)
	#
	# CONTENT OF THANHNIEN.VN PAGE STORED IN <DIV ID='ABODY'>
	if 'thanhnien.vn/kinh-doanh' in link:
		temp_1 = page_soup.find("div", {"id":"abody"})
		temp = temp_1.find_all('div')
	#
	# CONCATENATE ALL THE TEXT AND TURN TO LOWER KEYS
	content =  " "
	for item in temp: 
		content = content + item.text + " "
	return content.lower()

# GET CONTENT FROM DYNAMIC LINK - FOR VIETSTOCK.VN PAGE
def content_d(link):
	# CHANGE GOOGLE RSS REDIRECT LINK TO FINAL LINK
	if "www.google.com" in link:
		link = requests.get(link)
		link = link.text.partition("URL='")[-1].rpartition("'\"")[0]
	#
	# LOAD HTML USING PHANTOMJS BROWSER AND FIND ALL TEXT IN <P> TAGS IN HTML FILE
	driver = webdriver.PhantomJS()
	driver.get(link)
	time.sleep(5)
	temp = driver.find_elements_by_tag_name("p")
	#
	# CONCATENATE ALL THE TEXT AND TURN TO LOWER KEYS
	content =  " "
	for item in temp:
		content = content + item.text + " "
	return content.lower()

# CHANGE GOOGLE RSS REDIRECT LINK TO FINAL LINK
def fix_link(google_link):
	if "www.google.com" in google_link:
		google_link = requests.get(google_link)
		google_link = google_link.text.partition("URL='")[-1].rpartition("'\"")[0]
	return google_link

# FIX SOME PROBLEMS OF BROWSER PHANTOMJS IF HAPPEN
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# LOAD LIST OF OLD LINKS
f = open("C:\\Users\\Khai Tran\\Desktop\\test\\final_code_rss\\id_list.p", 'rb');
id_list = pickle.load(f);f.close()

# GET THE CURRENT CONTENT OF SENDING EMAIL TO APPEND NEW CONTENT
f = open("C:\\Users\\Khai Tran\\Desktop\\test\\final_code_rss\\send_email.p",'rb')
send_email = pickle.load(f);f.close()

#  CONNECT TO GOOGLE SHEET 
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name("C://Users//Khai Tran//Desktop//test//final_code_rss//sheet_access.json",scope)
client = gspread.authorize(creds)

# CONNECT TO SHEET FILE - GET RSS LINKS AND GET COMMON WORD LIST RELATED TO THE TOPIC FOR TOPIC FILTER
file_name = 'Auto_data_tracking'
file = client.open(file_name)
sheet2 = file.worksheet('Sheet2')
max_row_3 = int(sheet2.cell(2,7).value)
max_row_4 = int(sheet2.cell(2,8).value)

topic_common_wd = sheet2.range(2,1,max_row_3,1)
links = sheet2.range(2,2,max_row_4,2)

# TIME WHEN START SCRIPT
start_time = datetime.datetime.today()


# POINTER IS THE POSITION TO STORE NEW VALUE TO THE ID LIST - POINTER VALUE IS STORE IN ID_LIST[0]
pointer = id_list[0]

# VALUE TO COUNT THE SCORE OF EACH LINK FOR THE TOPIC FILTER
temp = 0

# CHANGE ARRAY TYPE TO SET TYPE TO REDUCE RUNNING TIME
link_title = set()

# VARIABLES FOR CHECKING HOW ACTIVE THE RSS IS
num_new_link = 0
link_each_rss = []

# TRACKING DATA OF EACH RUN TIME FOR SENDING TO GOOGLE SHEET
link_value = [[],[],[]]
link_value[0].append(start_time)
link_value[1].append("")
link_value[2].append("")

# CHANGE ARRAY TYPE TO SET TYPE TO REDUCE RUNNING TIME
id_list_set = set(id_list)


for k in range(len(links)):
	count_1 = 0
	print(links[k].value)
	#
	# FUNCTION TO GET FEEDS FROM RSS LINK
	feed = feedparser.parse(links[k].value)
	#
	for item in feed.entries:
		#
		# IF THE FEED IS NEW, STORE IT IN THE ID LIST AND CHECK ITS CONTENT
		if fix_link(item.link) not in id_list_set:
			num_new_link = num_new_link + 1
			id_list[pointer] = fix_link(item.link)
			id_list_set = set(id_list)
			#
			# INCREASE THE POSITION IN THE ID LIST AND RESET POINTER WHEN ID LIST IS FULL (5000 ITEM)
			pointer = pointer + 1
			if pointer == 5000: 
				pointer = 1
			count_1 = count_1 + 1
			#
			# CHECK IF THE FEED TITLE IS ALREADY IN THE EMAIL CONTENT
			if item.title not in link_title:
				try:
					# GET THE CONTENT OF THIS NEW FEED - VIETSTOCK PAGE IS DYNAMIC HTML
					if 'vietstock' in item.link: 
						content_ = content_d(item.link)
					else: content_ = content(item.link)
				except: 
					content_ = "can't get content"
				#
				# CHECK IF THE CONTENT IS RELEVANT
				if "drc" in content_ or "cao su " in content_ in content_:
					#
					# COUNT THE RELATED TOPIC WORDS IN THE CONTENT AND INCREASE THE SCORE OF THE CONTENT
					for word in topic_common_wd: 
						if word.value in content_: temp = temp + 1
				#
				# REDUCE SCORE IF CONTAIN IRRELEVANT WORDS
				if "thông báo giá thu mua" in content_: temp = 0
				#
				# IF THE CONTENT IS RELEVANT (SCORE > 2), STORE IT TO THE EMAIL CONTENT FOR SENDING
				if temp > 2: 
					send_email[0].append('<a href="' + fix_link(item.link) + '">' + item.title + '</a>')
					send_email[1].append(item.summary)
					#
					# STORE TITLE FOR CHECKING DUPLICATE TITLE
					link_title.add(item.title)
				#
				# TRACKING DATA OF NEW LINKS FOR SENDING TO GOOGLE SHEET
				link_value[0].append(fix_link(item.link))
				link_value[1].append(temp)
				link_value[2].append(content_)
				temp = 0
		else: 
			temp = 0
	#
	# VARIABLES FOR CHECKING HOW ACTIVE THE RSS IS
	link_each_rss.append(count_1)

# TIME WHEN FINISH SCRIPT
end_time = datetime.datetime.today()

# TRACKING DATA OF EACH RUN TIME FOR SENDING TO GOOGLE SHEET
link_value[0].append(end_time)
link_value[1].append("")
link_value[2].append("")

# ******************* STORE NO. LINKS/RSS AND TRACKING DATA TO GOOGLE SHEET ***********************
#  CONNECT TO GOOGLE SHEET 
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name("C://Users//Khai Tran//Desktop//test//final_code_rss//sheet_access.json",scope)
client = gspread.authorize(creds)
#
# LOAD SHEET FILE
file_name = 'Auto_data_tracking'
file = client.open(file_name)
sheet3 = file.worksheet('Sheet3')
sheet4 = file.worksheet('Sheet4')

link_count = sheet3.range(1,2,115,2)

max_row_3 = int(sheet3.cell(2,7).value)
max_row_4 = int(sheet4.cell(2,7).value)

# UPDATE  NO. LINKS/RSS
for i in range(len(link_each_rss)):
	link_count[i].value = int(link_count[i].value) + link_each_rss[i]

# STORE START, END TIME AND NO. OF NEW LINKS TO GOOGLE SHEET
update_temp_1 = sheet3.range(max_row_3 + 1, 1, max_row_3 + 1, 3)
update_temp_1[0].value = num_new_link
update_temp_1[1].value = start_time
update_temp_1[2].value = end_time

# UPDATE GOOGLE SHEET
sheet3.update_cells(link_count)
sheet3.update_cells(update_temp_1)

# STORE TRACKING DATA TO GOOGLE SHEET:
# 3 STEPS: 	GET SHEET RANGE ARRAY
# 			WRITE VALUE TO EACH ELEMENT OF THAT ARRAY
#			UPDATE THE SHEET RANGE ARRAY IN GOOGLE SHEET
update_temp_1 = sheet4.range(max_row_4 + 1, 1, max_row_4 + 1 + len(link_value[0]), 1)
update_temp_2 = sheet4.range(max_row_4 + 1, 2, max_row_4 + 1 + len(link_value[0]), 2)
update_temp_3 = sheet4.range(max_row_4 + 1, 3, max_row_4 + 1 + len(link_value[0]), 3)


for i in range(len(link_value[0])):
	update_temp_1[i].value = link_value[0][i]
	update_temp_2[i].value = link_value[1][i]
	update_temp_3[i].value = link_value[2][i]


sheet4.update_cells(update_temp_1)
sheet4.update_cells(update_temp_2)
sheet4.update_cells(update_temp_3)


# SAVE EMAIL CONTENT AND ID LIST
f = open("C:\\Users\\Khai Tran\\Desktop\\test\\final_code_rss\\send_email.p", 'wb');
pickle.dump(send_email,f);f.close()

id_list[0] = pointer
f = open("C:\\Users\\Khai Tran\\Desktop\\test\\final_code_rss\\id_list.p", 'wb');
pickle.dump(id_list,f);f.close()

