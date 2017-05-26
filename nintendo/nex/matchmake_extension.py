
from nintendo.nex.matchmake_common import Gathering
from nintendo.nex.common import DataHolder, NexEncoder

import logging
logger = logging.getLogger(__name__)


class SearchCriteria(NexEncoder):
	version_map = {
		30504: 0
	}

	def init(self, attribs, game_mode, min_participants, max_participants, matchmake_system,
		     vacant_only, exclude_locked, exclude_non_host_pid, selection_method, unk=None):
		self.attribs = attribs
		self.game_mode = game_mode
		self.min_participants = min_participants
		self.max_participants = max_participants
		self.matchmake_system = matchmake_system
		self.vacant_only = vacant_only
		self.exclude_locked = exclude_locked
		self.exclude_non_host_pid = exclude_non_host_pid
		self.selection_method = selection_method
		self.unk = unk
	
	def encode_old(self, stream):
		stream.list(self.attribs, stream.string)
		stream.string(self.game_mode)
		stream.string(self.min_participants)
		stream.string(self.max_participants)
		stream.string(self.matchmake_system)
		stream.bool(self.vacant_only)
		stream.bool(self.exclude_locked)
		stream.bool(self.exclude_non_host_pid)
		stream.u32(self.selection_method)
	
	def encode_v0(self, stream):
		self.encode_old(stream)
		stream.u16(self.unk)
		
		
class MatchmakeSession(NexEncoder):
	version_map = {
		30504: 0
	}
	
	def init(self, gathering, game_mode, attribs, open_participation, matchmake_system, application_data, unk, unkdata, unk2=None, unk3=None):
		self.gathering = gathering
		self.game_mode = game_mode
		self.attribs = attribs
		self.open_participation = open_participation
		self.matchmake_system = matchmake_system
		self.application_data = application_data
		self.unk = unk
		self.unkdata = unkdata
		self.unk2 = unk2
		self.unk3 = unk3

	def get_name(self):
		return "MatchmakeSession"
	
	def encode(self, stream):
		self.gathering.encode(stream)
		super().encode(stream)
		
	def decode(self, stream):
		self.gathering = Gathering.from_stream(stream)
		super().decode(stream)

	def encode_common(self, stream):
		stream.u32(self.game_mode)
		stream.list(self.attribs, stream.u32)
		stream.bool(self.open_participation)
		stream.u32(self.matchmake_system)
		stream.data(self.application_data)
		stream.u32(self.unk)
		
	def encode_old(self, stream):
		self.encode_common(stream)
		stream.data(self.unkdata)
		
	def encode_v0(self, stream):
		self.encode_common(stream)
		stream.u8(self.unk2)
		stream.data(self.unkdata)
		stream.u32(self.unk3)
		
	def decode_common(self, stream):
		self.game_mode = stream.u32()
		self.attribs = stream.list(stream.u32)
		self.open_participation = stream.bool()
		self.matchmake_system = stream.u32()
		self.application_data = stream.read(stream.u32())
		self.unk = stream.u32()
		
	def decode_old(self, stream):
		self.decode_common(stream)
		self.unkdata = stream.read(stream.u32())
		
	def decode_v0(self, stream):	
		self.decode_common(stream)
		self.unk2 = stream.u8()
		self.unkdata = stream.read(stream.u32())
		self.unk3 = stream.u32()
DataHolder.register(MatchmakeSession, "MatchmakeSession")


class MatchmakeExtensionClient:
	
	METHOD_CLOSE_PARTICIPATION = 1
	METHOD_OPEN_PARTICIPATION = 2
	METHOD_AUTO_MATCHMAKE = 3
	METHOD_BROWSE_MATCHMAKE_SESSION = 4
	METHOD_BROWSE_MATCHMAKE_SESSION_WITH_HOST_URLS = 5
	METHOD_CREATE_MATCHMAKE_SESSION = 6
	METHOD_JOIN_MATCHMAKE_SESSION = 7
	METHOD_MODIFY_CURRENT_GAME_ATTRIBUTE = 8
	METHOD_UPDATE_NOTIFICATION_DATA = 9
	METHOD_GET_FRIEND_NOTIFICATION_DATA = 10
	METHOD_UPDATE_APPLICATION_BUFFER = 11
	METHOD_UPDATE_MATCHMAKE_SESSION_ATTRIBUTE = 12
	METHOD_GETLST_FRIEND_NOTIFICATION_DATA = 13
	METHOD_UPDATE_MATCHMAKE_SESSION = 14
	METHOD_AUTO_MATCHMAKE_WITH_SEARCH_CRITERIA = 15
	METHOD_GET_PLAYING_SESSION = 16
	METHOD_CREATE_COMMUNITY = 17
	METHOD_UDPATE_COMMUNITY = 18
	METHOD_JOIN_COMMUNITY = 19
	METHOD_FIND_COMMUNITY_BY_GATHERING_ID = 20
	METHOD_FIND_OFFICIAL_COMMUNITY = 21
	METHOD_FIND_COMMUNITY_BY_PARTICIPANT = 22
	METHOD_UPDATE_PRIVACY_SETTING = 23
	METHOD_GET_MY_BLACK_LIST = 24
	METHOD_ADD_TO_BLACK_LIST = 25
	METHOD_REMOVE_FROM_BLACK_LIST = 26
	METHOD_CLEAR_MY_BLACK_LIST = 27
	METHOD_REPORT_VIOLATION = 28
	METHOD_IS_VIOLATION_USER = 29
	METHOD_JOIN_MATCHMAKE_SESSION_EX = 30
	METHOD_GET_SIMPLE_PLAYING_SESSION = 31
	METHOD_GET_SIMPLE_COMMUNITY = 32
	METHOD_AUTO_MATCHMAKE_WITH_GATHERING_ID = 33
	
	PROTOCOL_ID = 0x6D
	
	def __init__(self, back_end):
		self.client = back_end.secure_client
		
	def auto_matchmake_with_search_criteria(self, search_criteria, gathering, description):
		logger.info("MatchmakeExtension.auto_matchmake_with_search_criteria(...)")
		#--- request ---
		stream, call_id = self.client.init_message(self.PROTOCOL_ID, self.METHOD_AUTO_MATCHMAKE_WITH_SEARCH_CRITERIA)
		stream.list(search_criteria, lambda x: x.encode(stream))
		DataHolder(gathering).encode(stream)
		stream.string(description)
		self.client.send_message(stream)
		
		#--- response ---
		stream = self.client.get_response(call_id)
		object = DataHolder.from_stream(stream).data
		logger.info("MatchmakeExtension.auto_matchmake_with_search_criteria -> %s", object)
		return object