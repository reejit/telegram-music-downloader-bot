import os
import sys
import json
import youtube_dl
import telepotpro
from random import randint
from multiprocessing import Process
from youtubesearchpython import SearchVideos


bot = telepotpro.Bot("1461874967:AAEGbATjZZU-AaCxP_5pms9VPS0NFl6C-qk")

def startMsg(chat_id, first_name):
	bot.sendMessage(chat_id, '🤖 Hello, '+ first_name +'!\n\n'
	'📩 Send me:\n\n'
	'"*/music* _song name_"  or\n'
	'"*/music* _musician name - song name_"\n\n'
	'to order some music. 🎶', parse_mode= 'Markdown')

def helpMsg(chat_id, first_name):
	bot.sendMessage(chat_id, '🤖 Hello, '+ first_name +'!\n\n'
	'The Commans available for this bot are:'
	'"*/music* _song name_"  or\n'
	'"*/music* _musician name - song name_"\n\n'
	'"And I'll do my best to bring your music"\n'
        '🎶🎶🎶🎶🎶🎶🎶🎶', parse_mode= 'Markdown')

def errorMsg(chat_id, error_type):
	if error_type == 'too_long':
		bot.sendMessage(chat_id, '‼️ *Shit! The Song is too long..!*\n'
			'Order something 30 minutes or less.', parse_mode= 'Markdown')

	if error_type == 'spotify_command':
		bot.sendMessage(chat_id, "‼️ *Oops! The bot doesn't support Spotify links!*\n"
			'Try: "*/music* _song name_"\n'
			'or: "*/music* _musician name - song name_"', parse_mode= 'Markdown')

	if error_type == 'invalid_command':
		bot.sendMessage(chat_id, '‼️ *Oops! You typed an invalid command!*\n'
			'Try: "*/music* _song name_"\n'
			'or: "*/music* _musician name - song name_"', parse_mode= 'Markdown')

def downloadMusic(file_name, link):
	ydl_opts = {
		'outtmpl': './'+file_name,
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '256',
		}],
		'prefer_ffmpeg': True
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		info_dict = ydl.extract_info(link, download=True)

def validMusicInput(userInput, chat_id, chat_type):
		#Search music on youtube
		search = SearchVideos(userInput[6:], offset = 1, mode = "json", max_results = 1)
		resultados = json.loads(search.result())
		
		#Get video duration
		duration = resultados['search_result'][0]['duration'].split(':')
		splitCount = len(duration)

		if int(duration[0]) < 30 and splitCount < 3:
			title = resultados['search_result'][0]['title']
			link = resultados['search_result'][0]['link']
			file_name = title +' - '+str(randint(0,999999))+'.mp3'

			bot.sendMessage(chat_id,'🎵 '+title+'\n'+'🔗 '+link)
			DownloadingMsg = bot.sendMessage(chat_id,'🔻 Downloading🔻 '
				'\n_(this may take a while.)_', parse_mode= 'Markdown')

			#Download the music
			downloadMusic(file_name, link)

			bot.sendAudio(chat_id,audio=open(file_name,'rb'))
			bot.deleteMessage((chat_id, DownloadingMsg['message_id']))
			bot.sendMessage(chat_id, '✅Success✅')

			print ("Sucess!")
			os.remove(file_name)

		else:
			errorMsg(chat_id, 'too_long')

		pass

def recebendoMsg(msg):
	userInput = msg['text']
	chat_id = msg['chat']['id']
	first_name = msg['from']['first_name']
	chat_type = msg['chat']['type']

	if chat_type == 'group':
		if '@yourfavmusicbot' in userInput:
			userInput = userInput.replace('@yourfavmusicbot', '')

        if userInput.startswith('/start'):
		#Shows start dialog
		helpMsg(chat_id, first_name)


	if userInput.startswith('/start'):
		#Shows start dialog
		startMsg(chat_id, first_name)

	elif userInput.startswith('/music') and userInput[6:]!='':
		if 'open.spotify.com' in userInput[6:]:
			errorMsg(chat_id, 'spotify_command')

		else:
			#Process the music
			validMusicInput(userInput, chat_id, chat_type)

	else:
		#Invalid command
		errorMsg(chat_id, 'invalid_command')

	pass

def main(msg):
	main_process = Process(target=recebendoMsg, args=(msg,))
	main_process.start()

bot.message_loop(main, run_forever=True)
