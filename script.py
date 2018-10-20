#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.

This program is dedicated to the public domain under the CC0 license.

This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

import speech_recognition as sr  # pip install SpeechRecognition

from pydub import AudioSegment  # pip install pydub y ffmpeg

import os

from skyscanner.skyscanner import FlightsCache


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
	"""Send a message when the command /start is issued."""
	update.message.reply_text('Ask me for a flight!')

def error(bot, update, error):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, error)

def transcript(bot, update):
	"""Transcribes Voice to Text"""
	r = sr.Recognizer()
	audio_recv =  update.message.voice.get_file().download()
	audio = AudioSegment.from_file(audio_recv, format= "ogg" )
	audio.export(audio_recv + ".aiff", format = "aiff")
	
	with sr.AudioFile(audio_recv + ".aiff") as audio_file:
		r.adjust_for_ambient_noise(audio_file, duration=0.5)
		audio = r.record(audio_file)
	
	mes = r.recognize_google(audio)
	os.remove(audio_recv)
	os.remove(audio_recv + ".aiff")
	return mes

def skyscanner(msg,bot,update):

	if((msg.find("flight") == -1) and (msg.find("to fly") == -1) and (msg.find("fly to") == -1) and (msg.find("fly from") == -1)):
		update.message.reply_text(msg)

	else:
		index_to = msg.rfind("to ")
		index_from = msg.rfind("from ")

		flights_cache_service = FlightsCache('ha306082955374085267757354385037')
		print(msg)
		if (index_to) != -1:
			to = msg[index_to + 3:]
			to = to[:to.find(" ")]  # de moement fins a white space o final de linia, pero faltarà 
			print(to)

		if (index_from) != -1:
			from_ = msg[index_from + 5:]
			from_ = from_[:from_.find(" ")]  # de moement fins a white space o final de linia, pero faltarà 
			print(from_)

		result = flights_cache_service.get_cheapest_quotes(
			market='UK',
			currency='GBP',
			locale='en-GB',
			originplace='SIN-sky',
			destinationplace='KUL-sky',
			outbounddate='2018-10-25',
			adults=1).parsed

		carrierID = result["Quotes"][0]["OutboundLeg"]["CarrierIds"][0]
		aeroSortida = result["Quotes"][0]["OutboundLeg"]["OriginId"]
		aeroArribada = result["Quotes"][0]["OutboundLeg"]["DestinationId"]


		carrierDic = {}
		for carrier in result["Carriers"]:
			carrierDic[carrier["CarrierId"]] = carrier["Name"];

		placesDic = {}
		for place in result["Places"]:
			placesDic[place["PlaceId"]] = place
			place.pop('PlaceId', None)

		update.message.reply_text(from_ + " --> " + to + " Vol de "+placesDic[aeroSortida]["Name"]+" a "+placesDic[aeroArribada]["Name"]+" gestionat per "+carrierDic[carrierID]+".")


def skySearch_voice(bot,update):
	skyscanner(transcript(bot,update),bot,update)

def skySearch_text(bot,update):
	skyscanner(update.message.text,bot,update)
	


def main():
	"""Start the bot."""
	# Create the EventHandler and pass it your bot's token.
	updater = Updater("658306194:AAGEnbfg-flLxhsC0HZHnJUvf-bpjJ8Vc_c")

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))

	# on noncommand i.e message - echo the message on Telegram
	dp.add_handler(MessageHandler(Filters.text, skySearch_text))
	dp.add_handler(MessageHandler(Filters.voice, skySearch_voice))

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()
