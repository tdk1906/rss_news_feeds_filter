import smtplib, pickle, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# GET TODAY DATE FOR EMAIL SUBJECT
mylist = []
today = datetime.date.today()
mylist.append(today)

# LOAD EMAIL CONTENT
f = open("C:\\Users\\Khai Tran\\Desktop\\test\\final_code_rss\\send_email.p",'rb')
send_email = pickle.load(f);f.close()

#for i in range(len(feed)):
#	list_[0].append('<a href="' + fix_link(feed['items'][i]['link']) + '">' + feed['items'][i]['title'] + '</a>')
#	list_[1].append(feed['items'][i]['summary'])
#
# IF EMAIL CONTENT IS NOT EMPTY
if len(send_email[0]) > 0:
	# CREATE EMAIL CONTENT FOR SENDING
	msg_ = MIMEMultipart('test')
	for i in range(len(send_email[0])):
		msg_.attach(MIMEText(send_email[0][i], 'html'))
		#msg_.attach(MIMEText(send_email[1][i]))
	msg_['Subject'] = ' Send via Python ' + str(mylist[0])
	msg_['From'] = 'email@gmail.com'
	msg_['To'] = 'email@gmail.com'
	#
	# SIGN IN TO GMAIL, WRITE THE CONTENT AND SEND EMAIL
	server_ = smtplib.SMTP('smtp.gmail.com', 587)
	server_.starttls()
	server_.login("email@gmail.com","password")
	server_.sendmail("email@gmail.com","email@gmail.com", msg_.as_string())
	server_.quit()
	#
	# DELETE THE STORE EMAIL CONTENT AFTER SENDING
	send_email = [[] for i in range(2)]
	f = open("C:\\Users\\Khai Tran\\Desktop\\test\\final_code_rss\\send_email.p", 'wb');
	pickle.dump(send_email,f);f.close()
