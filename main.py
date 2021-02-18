import discord
import pandas as pd
import datetime
import os
import pickle


class MyClient(discord.Client):
	def __init__(self):
		super().__init__()
		self.path = './data.csv'
		self.temp_path = './temp.pkl'
		self.members = []
		self.temp = {}
		self.data = pd.DataFrame()
		self.start_hour = 0

	async def on_ready(self):
		print('Logged on as {0}!'.format(self.user))
		if os.path.exists(self.path):
			self.data = pd.read_csv(self.path, index_col=0)
			self.members = self.data.columns.to_list()
		if os.path.exists('./start.csv'):
			self.start_hour = int(pd.read_csv('./start.csv', index_col=0).loc[0, '0'])
		if os.path.exists(self.temp_path):
			a_file = open(self.temp_path, "rb")
			self.temp = pickle.load(a_file)

	async def on_message(self, message):
		print('Message from {0.author}: {0.content}'.format(message))

		if message.content.startswith('log'):
			_, cmd, *argv = message.content.strip().split()
			if cmd == 'help':
				await message.channel.send(
					"log start n: set a day's start n:00\\ log today : show user's spent time in voice channel today")

			if cmd == 'start':
				self.start_hour = int(argv[0])
				df = pd.DataFrame([self.start_hour])
				pd.DataFrame([self.start_hour]).to_csv('./start.csv')

			if cmd == 'today':
				date = str((datetime.datetime.now() - datetime.timedelta(hours=self.start_hour)).date())
				seconds = int(self.data.loc[date, message.author.name])
				td = datetime.timedelta(seconds=seconds)
				await message.channel.send(str(td))

			if cmd == 'user':
				sort_data = self.data.sort_index()
				for member in message.mentions:
					for date, seconds in sort_data[member.name].iteritems():
						seconds = int(seconds)
						td = datetime.timedelta(seconds=seconds)
						await message.channel.send(date + '\t' + str(td))

	async def on_voice_state_update(self, member, before, after):
		if member.name not in self.members:
			self.members.append(member.name)
			self.data[member.name] = [0 for _ in self.data.index]

		if before is not None:
			if member.name in self.temp.keys():
				time_in = self.temp[member.name]
				time_out = datetime.datetime.now()
				date = str((time_out - datetime.timedelta(hours=self.start_hour)).date())
				if date not in self.data.index:
					self.data.loc[date] = [0 for _ in self.members]
					self.data.loc[date] = [0 for _ in self.members]
				self.data.loc[date, member.name] += (time_out - time_in).total_seconds()

		if after is not None:
			self.temp[member.name] = datetime.datetime.now()

		self.data.to_csv(self.path)
		a_file = open(self.temp_path, "wb")
		pickle.dump(self.temp, a_file)
		a_file.close()


client = MyClient()
client.run('ODExNTQ5MzYxOTA5MDA2MzY4.YCz0PQ.iluaKOSnZrANd7uYohoHParM630')
