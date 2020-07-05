# modified Audio-Converter for iFlatFHD-skin by gordon55
#
# based on VTI AudioInfo and MediaPortal mp_audioinfo, thx @VTI and MP teams
#
# enhanced : 
# a) formats aac, ogg and m4a
# b) 3rd option "AudioInfo" return short text in upper case, max size 6 chars, f.e. "DD+2.0"
# c) fixes DD info for ServusTV-HD not showing "5.1", where DD info in languages is lower case, but in description uppercase
#    by adding .lower() in compare and DD info shown in lower case avoided by adding .title() at "return languages"

from enigma import iPlayableService
from Components.Converter.Converter import Converter
from Components.Element import cached
from Poll import Poll

class iFlatAudioInfo(Poll, Converter, object):
	GET_AUDIO_ICON = 0
	GET_AUDIO_CODEC = 1
	GET_AUDIO_INFO = 2

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.type = type
		self.poll_interval = 3000
		self.poll_enabled = True
		self.lang_strings = ("ger", "german", "deu")
		self.codecs = {    "01_dolbydigitalplus": ("digital+", "digitalplus", "ac3+", "e-ac-3"),
				   "02_dolbydigital": ("ac3", "ac-3", "dolbydigital"),
				   "03_mp3": ("mp3", ),
				   "04_wma": ("wma", ),
				   "05_flac": ("flac", ),
				   "06_aac": ("aac", ),
				   "07_lpcm": ("lpcm", ),
				   "08_dts-hd": ("dts-hd", ),
				   "09_dts": ("dts", ),
				   "10_pcm": ("pcm", ),
				   "11_mpeg": ("mpeg", ),
				   "12_ogg": ("ogg", "vorbis"),
				   "13_m4a": ("applelossless", ),
				}
		self.codec_info = { "dolbydigitalplus": ("51", "20", "71"),
				    "dolbydigital": ("51", "20", "10", "71"),
				    "wma": ("8", "9"),
				  }
		self.type, self.interesting_events = {
				"AudioIcon": (self.GET_AUDIO_ICON, (iPlayableService.evUpdatedInfo,)),
				"AudioCodec": (self.GET_AUDIO_CODEC, (iPlayableService.evUpdatedInfo,)),
				"AudioInfo": (self.GET_AUDIO_INFO, (iPlayableService.evUpdatedInfo,)),
			}[type]

	def getAudio(self):
		service = self.source.service
		audio = service.audioTracks()
		if audio:
			self.current_track = audio.getCurrentTrack()
			self.number_of_tracks = audio.getNumberOfTracks()
			if self.number_of_tracks > 0 and self.current_track > -1:
				self.audio_info = audio.getTrackInfo(self.current_track)
				return True
		return False

	def getLanguage(self):
		languages = self.audio_info.getLanguage()
		for lang in self.lang_strings:
			if lang in languages:
				languages = "Deutsch"
				break
		languages = languages.replace("und ", "")
		return languages

	def getAudioCodec(self, info):
		description_str = _("unknown")
		if self.getAudio():
			languages = self.getLanguage()
			description = self.audio_info.getDescription();
			description_str = description.split(" ")
			#print "iFlatAudioInfo description_str=", description_str
			#print "iFlatAudioInfo languages=", languages
			if len(description_str) and description_str[0].lower() in languages.lower():
				return languages.title()
			if description.lower() in languages.lower():
				languages = ""
			description_str = description + " " + languages
		return description_str

	def getAudioIcon(self, info):
		description_str = self.get_short(self.getAudioCodec(info).translate(None, ' .').lower())
		return description_str

	def getAudioInfo(self, info):
		description_str = self.getAudioCodec(info).translate(None, ' .').lower()
		#print "iFlatAudioInfo description_str2=", description_str
		for return_codec, codecs in sorted(self.codecs.iteritems()):
			for codec in codecs:
				if codec in description_str:
					codec = return_codec.split('_')[1]
					if codec in self.codec_info:
						for ex_codec in self.codec_info[codec]:
							if ex_codec in description_str:
								if len(ex_codec) > 1:
									ex_codec = ex_codec[0] + "." + ex_codec[1]
								codec += ex_codec
								#codec = codec + " " + ex_codec						# insert blank 
								break
					#print "iFlatAudioInfo codec0=", codec
					codec = codec.replace("dolbydigitalplus", "DD+")	
					codec = codec.replace("dolbydigital", "DD")
					codec = codec.upper()
					#print "iFlatAudioInfo codec1=", codec
					return codec
					
		return " "


	def get_short(self, audioName):
		for return_codec, codecs in sorted(self.codecs.iteritems()):
			for codec in codecs:
				if codec in audioName:
					codec = return_codec.split('_')[1]
					if codec in self.codec_info:
						for ex_codec in self.codec_info[codec]:
							if ex_codec in audioName:
								codec += ex_codec
								break
					return codec
		return audioName

	@cached
	def getText(self):
		service = self.source.service
		if service:
			info = service and service.info()
			if info:
				if self.type == self.GET_AUDIO_CODEC:
					return self.getAudioCodec(info)
				if self.type == self.GET_AUDIO_ICON:
					return self.getAudioIcon(info)
				if self.type == self.GET_AUDIO_INFO:
					return self.getAudioInfo(info)
		return _("invalid type")

	text = property(getText)

	def changed(self, what):
		if what[0] != self.CHANGED_SPECIFIC or what[1] in self.interesting_events:
			Converter.changed(self, what)