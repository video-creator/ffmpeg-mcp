import json
class StreamDisposition:
    def __init__(self, disposition):
        self.default = disposition.get("default", 0)
        self.dub = disposition.get("dub", 0)
        self.original = disposition.get("original", 0)
        self.comment = disposition.get("comment", 0)
        self.lyrics = disposition.get("lyrics", 0)
        self.karaoke = disposition.get("karaoke", 0)
        self.forced = disposition.get("forced", 0)
        self.hearing_impaired = disposition.get("hearing_impaired", 0)
        self.visual_impaired = disposition.get("visual_impaired", 0)
        self.clean_effects = disposition.get("clean_effects", 0)
        self.attached_pic = disposition.get("attached_pic", 0)
        self.timed_thumbnails = disposition.get("timed_thumbnails", 0)
        self.non_diegetic = disposition.get("non_diegetic", 0)
        self.captions = disposition.get("captions", 0)
        self.descriptions = disposition.get("descriptions", 0)
        self.metadata = disposition.get("metadata", 0)
        self.dependent = disposition.get("dependent", 0)
        self.still_image = disposition.get("still_image", 0)
        self.multilayer = disposition.get("multilayer", 0)

class StreamTags:
    def __init__(self, tags):
        self.handler_name = tags.get("handler_name", "")
        self.vendor_id = tags.get("vendor_id", "")

class VideoStream:
    def __init__(self, stream):
        self.index = stream.get("index")
        self.codec_name = stream.get("codec_name")
        self.codec_long_name = stream.get("codec_long_name")
        self.profile = stream.get("profile")
        self.codec_type = stream.get("codec_type")
        self.codec_tag_string = stream.get("codec_tag_string")
        self.codec_tag = stream.get("codec_tag")
        self.width = stream.get("width")
        self.height = stream.get("height")
        self.coded_width = stream.get("coded_width")
        self.coded_height = stream.get("coded_height")
        self.has_b_frames = stream.get("has_b_frames")
        self.sample_aspect_ratio = stream.get("sample_aspect_ratio")
        self.display_aspect_ratio = stream.get("display_aspect_ratio")
        self.pix_fmt = stream.get("pix_fmt")
        self.level = stream.get("level")
        self.color_range = stream.get("color_range")
        self.color_space = stream.get("color_space")
        self.color_transfer = stream.get("color_transfer")
        self.color_primaries = stream.get("color_primaries")
        self.chroma_location = stream.get("chroma_location")
        self.field_order = stream.get("field_order")
        self.refs = stream.get("refs")
        self.view_ids_available = stream.get("view_ids_available", "")
        self.view_pos_available = stream.get("view_pos_available", "")
        self.id = stream.get("id")
        self.r_frame_rate = stream.get("r_frame_rate")
        self.avg_frame_rate = stream.get("avg_frame_rate")
        self.time_base = stream.get("time_base")
        self.start_pts = stream.get("start_pts")
        self.start_time = stream.get("start_time")
        self.duration_ts = stream.get("duration_ts")
        self.duration = stream.get("duration")
        self.bit_rate = stream.get("bit_rate")
        self.nb_frames = stream.get("nb_frames")
        self.extradata_size = stream.get("extradata_size")
        self.disposition = StreamDisposition(stream.get("disposition", {}))
        self.tags = StreamTags(stream.get("tags", {}))

class AudioStream:
    def __init__(self, stream):
        self.index = stream.get("index")
        self.codec_name = stream.get("codec_name")
        self.codec_long_name = stream.get("codec_long_name")
        self.profile = stream.get("profile")
        self.codec_type = stream.get("codec_type")
        self.codec_tag_string = stream.get("codec_tag_string")
        self.codec_tag = stream.get("codec_tag")
        self.sample_fmt = stream.get("sample_fmt")
        self.sample_rate = stream.get("sample_rate")
        self.channels = stream.get("channels")
        self.channel_layout = stream.get("channel_layout")
        self.bits_per_sample = stream.get("bits_per_sample")
        self.initial_padding = stream.get("initial_padding")
        self.id = stream.get("id")
        self.r_frame_rate = stream.get("r_frame_rate")
        self.avg_frame_rate = stream.get("avg_frame_rate")
        self.time_base = stream.get("time_base")
        self.start_pts = stream.get("start_pts")
        self.start_time = stream.get("start_time")
        self.duration_ts = stream.get("duration_ts")
        self.duration = stream.get("duration")
        self.bit_rate = stream.get("bit_rate")
        self.nb_frames = stream.get("nb_frames")
        self.extradata_size = stream.get("extradata_size")
        self.disposition = StreamDisposition(stream.get("disposition", {}))
        self.tags = StreamTags(stream.get("tags", {}))

class FormatContext:
    def __init__(self, json_data):
        data = json.loads(json_data)
        streams = data["streams"]
        self.video_streams = []
        self.audio_streams = []
        for stream in streams:
            if stream["codec_type"] == "audio":
                self.audio_streams.append(AudioStream(stream))
            elif stream["codec_type"] == "video": 
                self.video_streams.append(VideoStream(stream))
